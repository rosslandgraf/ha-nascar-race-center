"""Manual anonymous CF probes; raw JSON stays in ignored work/, never production.

No network activity on import or in normal CI. See docs/api/README.md.
"""

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/api/endpoints.json"
MAX_BYTES = 4 * 1024 * 1024
MAX_NODES = 100_000
MAX_DEPTH = 64


class NoRedirect(HTTPRedirectHandler):
    """Never follow login, media, alternate-host or other redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_endpoints():
    """The original 28 exact URLs are the only network destinations."""
    return json.loads(INVENTORY.read_text())["endpoints"]


def reject_constant(value):
    """NaN and infinity are not JSON numbers."""
    raise ValueError("Non-JSON constant")


def decode_json(body):
    """Bound decoding and reject ambiguous duplicate object keys."""

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    return json.loads(
        body, parse_constant=reject_constant, object_pairs_hook=unique_pairs
    )


def inspect_schema(payload):
    """Visit every nested value; union array shapes without storing field values.

    Paths use JSON bracket notation; [*] aggregates all array elements. Presence
    counts are observations, never a required-field or provider guarantee.
    """
    fields = {}
    nodes = 0

    def visit(value, path, parent, depth):
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise ValueError("Schema inspection limit exceeded")
        kind = (
            "null"
            if value is None
            else "boolean"
            if isinstance(value, bool)
            else "integer"
            if isinstance(value, int)
            else "number"
            if isinstance(value, float)
            else "string"
            if isinstance(value, str)
            else "object"
            if isinstance(value, dict)
            else "array"
        )
        field = fields.setdefault(
            path,
            {
                "types": [],
                "seen": 0,
                "objects": 0,
                "parent": parent,
            },
        )
        field["seen"] += 1
        if kind not in field["types"]:
            field["types"].append(kind)
            field["types"].sort()
        if isinstance(value, dict):
            field["objects"] += 1
            for key, child in value.items():
                visit(child, f"{path}[{json.dumps(key)}]", path, depth + 1)
        elif isinstance(value, list):
            for child in value:
                visit(child, f"{path}[*]", path, depth + 1)

    visit(payload, "$", None, 0)
    for path, field in fields.items():
        parent = field["parent"]
        field["missing_observed"] = (
            field["seen"] < fields[parent]["objects"]
            if parent and not path.endswith("[*]")
            else False
        )
        field["null_observed"] = "null" in field["types"]
    return dict(sorted(fields.items()))


def schema_diff(before, after):
    """Report shape differences only; no fixture replacement or required claims."""
    return {
        "added_paths": sorted(after.keys() - before.keys()),
        "absent_paths": sorted(before.keys() - after.keys()),
        "changed_types": {
            path: {"before": before[path]["types"], "after": after[path]["types"]}
            for path in sorted(before.keys() & after.keys())
            if before[path]["types"] != after[path]["types"]
        },
    }


def probe(endpoint, opener=None):
    """One GET, no cookies/authentication/redirects/retries; bounded read."""
    started = datetime.now(UTC)
    clock = time.monotonic()
    record = {
        "id": endpoint["id"],
        "url": endpoint["url"],
        "attempted_at_utc": started.isoformat(),
        "http_status": None,
        "response_type": None,
        "outcome": "transport_error",
        "json_usable": False,
        "url_context": endpoint["url_context"],
        "observed_context": {},
        "content_state": "unverified",
        "capture": None,
        "schema": None,
    }
    payload = body = None
    opener = opener or build_opener(NoRedirect())
    request = Request(
        endpoint["url"],
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": "NASCAR-Race-Center-Reference/1.0 (manual validation)",
        },
    )
    try:
        try:
            response = opener.open(request, timeout=20)
        except HTTPError as error:
            response = error
        with response:
            record["http_status"] = response.code
            record["response_type"] = response.headers.get("Content-Type")
            record["cache_control"] = response.headers.get("Cache-Control")
            record["http_date"] = response.headers.get("Date")
            record["age"] = response.headers.get("Age")
            record["last_modified"] = response.headers.get("Last-Modified")
            record["retry_after"] = response.headers.get("Retry-After")
            if response.code != 200:
                record["outcome"] = (
                    "redirect_not_followed"
                    if 300 <= response.code < 400
                    else "access_denied"
                    if response.code in (401, 403)
                    else "http_error"
                )
            else:
                body = response.read(MAX_BYTES + 1)
                record["bytes"] = len(body)
                if len(body) > MAX_BYTES:
                    record["outcome"] = "oversized"
                    body = None
                else:
                    try:
                        payload = decode_json(body)
                        record["schema"] = inspect_schema(payload)
                    except ValueError, UnicodeError, RecursionError:
                        record["outcome"] = "invalid_json_or_schema_limit"
                        body = None
                    else:
                        record["outcome"] = "json"
                        record["json_usable"] = True
                        record["sha256"] = hashlib.sha256(body).hexdigest()
                        if isinstance(payload, dict):
                            for key in (
                                "series_id",
                                "race_id",
                                "run_id",
                                "race_season",
                                "time_of_day_os",
                            ):
                                value = payload.get(key)
                                if isinstance(value, int | str) and not isinstance(
                                    value, bool
                                ):
                                    record["observed_context"][key] = value
                        # A path name or HTTP Date never proves a live session.
                        record["content_state"] = "observed_json_freshness_unverified"
                        if (
                            endpoint["category"] == "excluded"
                            or "no-store" in (record["cache_control"] or "").lower()
                        ):
                            body = None
                            record["capture_withheld"] = "excluded_or_no_store"
    except (URLError, OSError, TimeoutError) as error:
        # CONNECT status belongs to the proxy, not the NASCAR origin. Do not
        # log arbitrary exception strings, proxy URLs, headers or error bodies.
        if "Tunnel connection failed: 403" in str(error):
            record["outcome"] = "proxy_connect_denied"
            record["proxy_connect_status"] = 403
        record["error_type"] = type(error).__name__
        body = None
    record["duration_ms"] = round((time.monotonic() - clock) * 1000)
    record["completed_at_utc"] = datetime.now(UTC).isoformat()
    return record, body


def main():
    """Explicitly invoked developer utility, separate from all automated CI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="confirm permission for these manual anonymous GETs",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        choices=[endpoint["id"] for endpoint in load_endpoints()],
        help="select IDs; otherwise probe all original 28 URLs",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="previous local report.json for a schema comparison",
    )
    args = parser.parse_args()
    if not args.authorized:
        parser.error(
            "--authorized is required; check data-use and network policy first"
        )
    baseline = {}
    if args.baseline:
        baseline = {
            item["id"]: item
            for item in json.loads(args.baseline.read_text())["results"]
        }
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "work/nascar-reference" / run_id
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    results = []
    endpoints = [
        endpoint
        for endpoint in load_endpoints()
        if not args.endpoint or endpoint["id"] in args.endpoint
    ]
    for index, endpoint in enumerate(endpoints):
        if index:
            time.sleep(1)  # one pass, conservative spacing, no retry loops
        record, body = probe(endpoint)
        if body is not None:
            capture = output / endpoint["category"] / f"{endpoint['id']}.json"
            capture.parent.mkdir(exist_ok=True, mode=0o700)
            capture.write_bytes(body)  # exact original bytes, no rewritten values
            capture.chmod(0o600)
            record["capture"] = str(capture.relative_to(output))
        previous = baseline.get(endpoint["id"], {}).get("schema")
        if previous is not None and record["schema"] is not None:
            record["schema_diff"] = schema_diff(previous, record["schema"])
        results.append(record)
        print(f"{endpoint['id']}: {record['outcome']}", flush=True)
        # An origin rate limit/503 stops the run. Unattempted endpoints are
        # explicitly reported; no rapid retry or disregard of Retry-After.
        if record["http_status"] in (429, 503):
            for remaining in endpoints[index + 1 :]:
                results.append(
                    {
                        "id": remaining["id"],
                        "url": remaining["url"],
                        "outcome": "not_attempted_after_server_pause",
                        "http_status": None,
                        "json_usable": False,
                        "capture": None,
                        "schema": None,
                    }
                )
            break
    report = output / "report.json"
    report.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "client": "urllib anonymous, TLS verified, no redirects",
                "raw_capture_policy": (
                    "local only; redistribution permission unresolved"
                ),
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )
    report.chmod(0o600)
    print(f"Local report: {report}")


if __name__ == "__main__":
    main()
