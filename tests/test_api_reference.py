"""Offline capture and provenance checks; never contact NASCAR from CI."""

import io
import json
import re
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

from scripts import nascar_reference as reference


def test_inventory_is_exact_original_brief_including_four_exclusions():
    brief = (reference.ROOT / "NASCAR_Race_Center_Codex_Brief.md").read_text()
    urls = re.findall(r"^- (https://cf\.nascar\.com/\S+)", brief, re.M)
    endpoints = reference.load_endpoints()
    assert len(endpoints) == len(urls) == 28
    assert [endpoint["url"] for endpoint in endpoints] == urls
    assert len({endpoint["id"] for endpoint in endpoints}) == 28
    assert sum(endpoint["category"] == "excluded" for endpoint in endpoints) == 4


def test_schema_visits_all_array_variants_and_preserves_json_type_distinctions():
    schema = reference.inspect_schema(
        {
            "items": [
                {"id": 1, "optional": None, "flag": True, "nest": [{"x": 1.5}]},
                {"id": "2", "flag": False, "nest": [{"y": []}]},
            ]
        }
    )
    assert schema['$["items"][*]["id"]']["types"] == ["integer", "string"]
    assert schema['$["items"][*]["flag"]']["types"] == ["boolean"]
    assert schema['$["items"][*]["optional"]']["missing_observed"]
    assert schema['$["items"][*]["optional"]']["null_observed"]
    assert schema['$["items"][*]["nest"][*]["x"]']["missing_observed"]
    assert schema['$["items"][*]["nest"][*]["y"]']["types"] == ["array"]
    assert not any("example" in field for field in schema.values())


def test_schema_diff_is_sample_evidence_not_a_required_field_claim():
    before = reference.inspect_schema({"id": 1, "a": []})
    after = reference.inspect_schema({"id": "1", "b": None})
    result = reference.schema_diff(before, after)
    assert result == {
        "added_paths": ['$["b"]'],
        "absent_paths": ['$["a"]'],
        "changed_types": {
            '$["id"]': {
                "before": ["integer"],
                "after": ["string"],
            }
        },
    }
    assert "required" not in json.dumps(result)


def response(body, *, code=200, headers=None):
    result = io.BytesIO(body)
    result.code = code
    result.headers = headers or {"Content-Type": "application/json"}
    return result


def test_probe_is_anonymous_no_redirect_and_preserves_exact_bytes():
    body = b'{ "series_id": 2, "race_id": 99000, "vehicles": [] }\n'
    opener = Mock()
    opener.open.return_value = response(body)
    record, captured = reference.probe(reference.load_endpoints()[0], opener)
    assert captured == body
    assert record["json_usable"] and record["http_status"] == 200
    assert record["observed_context"] == {"series_id": 2, "race_id": 99000}
    assert record["content_state"] == "observed_json_freshness_unverified"
    request = opener.open.call_args.args[0]
    assert not any(
        key.lower() in {"cookie", "authorization"} for key in request.headers
    )
    assert (
        reference.NoRedirect().redirect_request(
            request, None, 302, "login", {}, "https://feed.nascar.com/"
        )
        is None
    )
    opener.open.assert_called_once()


def test_proxy_connect_denial_is_never_recorded_as_origin_403():
    opener = Mock()
    opener.open.side_effect = URLError(
        OSError("Tunnel connection failed: 403 Forbidden")
    )
    record, body = reference.probe(reference.load_endpoints()[0], opener)
    assert record["outcome"] == "proxy_connect_denied"
    assert record["proxy_connect_status"] == 403
    assert record["http_status"] is None and body is None


@pytest.mark.parametrize("status", [302, 401, 403, 404, 429, 503])
def test_origin_errors_do_not_capture_protected_or_error_content(status):
    opener = Mock()
    opener.open.side_effect = HTTPError(
        "https://cf.nascar.com/", status, "error", {}, io.BytesIO(b"sensitive")
    )
    record, body = reference.probe(reference.load_endpoints()[0], opener)
    assert record["http_status"] == status
    assert not record["json_usable"] and body is None
    assert "sensitive" not in json.dumps(record)


@pytest.mark.parametrize(
    "body",
    [
        b"<html>login</html>",
        b'{"id":1,"id":2}',
        b'{"x":NaN}',
        b"[" * 2000 + b"0" + b"]" * 2000,
        b" " * (reference.MAX_BYTES + 1),
    ],
)
def test_invalid_ambiguous_deep_and_large_bodies_are_not_saved(body):
    opener = Mock()
    opener.open.return_value = response(body)
    record, capture = reference.probe(reference.load_endpoints()[0], opener)
    assert record["http_status"] == 200
    assert not record["json_usable"] and capture is None


@pytest.mark.parametrize("excluded,no_store", [(True, False), (False, True)])
def test_protected_or_no_store_json_is_inspected_but_not_retained(excluded, no_store):
    endpoint = reference.load_endpoints()[-1 if excluded else 0]
    opener = Mock()
    opener.open.return_value = response(
        b'{"id":1}',
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-store" if no_store else "max-age=60",
        },
    )
    record, capture = reference.probe(endpoint, opener)
    assert record["json_usable"] and capture is None
    assert record["capture_withheld"] == "excluded_or_no_store"


def test_no_authorization_never_opens_network(monkeypatch):
    monkeypatch.setattr("sys.argv", ["nascar_reference.py"])
    opener = Mock()
    monkeypatch.setattr(reference, "build_opener", opener)
    with pytest.raises(SystemExit):
        reference.main()
    opener.assert_not_called()


def test_provenance_covers_every_fixture_with_unchanged_synthetic_content():
    directory = reference.ROOT / "tests/fixtures/nascar"
    provenance = json.loads((directory / "PROVENANCE.json").read_text())["fixtures"]
    assert {row["file"] for row in provenance} == {
        path.name for path in directory.glob("*.json") if path.name != "PROVENANCE.json"
    }
    assert all(
        row["provenance"] == "handmade_synthetic" and not row["nascar_capture"]
        for row in provenance
    )
    import hashlib

    for row in provenance:
        assert (
            row["sha256"]
            == hashlib.sha256((directory / row["file"]).read_bytes()).hexdigest()
        )


def test_live_tool_stops_after_server_pause_without_retry(monkeypatch, tmp_path):
    monkeypatch.setattr(reference, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["nascar_reference.py", "--authorized"])
    probe = Mock(
        return_value=(
            {
                "id": "live_feed",
                "http_status": 429,
                "outcome": "http_error",
                "schema": None,
            },
            None,
        )
    )
    monkeypatch.setattr(reference, "probe", probe)
    reference.main()
    probe.assert_called_once()
    report = json.loads(next(Path(tmp_path).rglob("report.json")).read_text())
    assert len(report["results"]) == 28
    assert all(
        row["outcome"] == "not_attempted_after_server_pause"
        for row in report["results"][1:]
    )
