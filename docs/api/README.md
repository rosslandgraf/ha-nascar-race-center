# NASCAR API reference library

Start with [ENDPOINT_CATALOG.md](ENDPOINT_CATALOG.md), then
[SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md) and the latest
[audit report](AUDIT_REPORT.md). The original
[brief](../../NASCAR_Race_Center_Codex_Brief.md) remains authoritative for the
28 exact URLs. [endpoints.json](endpoints.json) is the machine-readable inventory;
it is separate from the smaller production allowlist. Listing an endpoint here
does not enable it in the integration.

The latest [owner-reported CF correction](../REAL_CF_EVIDENCE.md) narrows the
schedule UTC contract and isolates driver identities. Its missing raw attachments
and independent published-time corroboration are recorded explicitly.

## Evidence and data boundaries

The imported observed package is now the primary structural source for Phase 3B.
Its redacted samples are documentation, not original captures or replay inputs.
The following inventory describes the earlier development audit.

- Owner browser reports: 24 working, four error/login on October 20, 2026.
- Fresh anonymous direct attempts: see [probe evidence](probes/2026-10-21.json).
  All 28 were blocked at proxy CONNECT, before an origin response. This does not
  establish NASCAR denial, Cloudflare behavior, schema, or live freshness.
- Stored JSON fixtures: six existing **handmade synthetic** examples, with
  fictional values and individual [provenance](../../tests/fixtures/nascar/PROVENANCE.json).
  There are currently **no real NASCAR captures** in Git or locally.
- Community references: pinned in [SCHEMA_EVIDENCE.md](../SCHEMA_EVIDENCE.md).
  These support experimental parser contracts, not current observed schemas.

NASCAR data/media permissions, storage/redistribution rights and allowed polling
rates remain unresolved. MIT covers project code only. Do not commit feed
captures, media URLs/tokens, account information, protected responses or full
datasets without rights and a separate content review. Anonymous success alone
does not grant redistribution rights. See [DATA_USE.md](../DATA_USE.md).

## Manual capture and schema comparison

Routine CI is offline. There is deliberately no scheduled/live API workflow.
Run this developer-only tool from a network that permits the documented CF host,
after confirming authorization for these specific manual GETs:

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
python scripts/nascar_reference.py --authorized
# Prefer only the endpoint needed for development:
python scripts/nascar_reference.py --authorized --endpoint live_feed \
  --baseline work/nascar-reference/PREVIOUS_RUN/report.json
```

The prepared activation path is specific to this workspace; elsewhere use your
Python 3.14 environment. The tool accepts only original catalog IDs, sends no
cookies/credentials, verifies TLS, follows no redirects and makes no retries.
One-second spacing, 20-second timeout, 4 MiB read cap, 64-level schema depth and
100,000-node inspection cap bound each pass. These are developer protection
limits, not provider permissions or documented NASCAR limits. An origin 429 or
503 stops the pass and labels remaining URLs unattempted. The Retry-After header
is recorded for the operator; the tool never retries or sleeps until it expires.
Respect that hint before another invocation.

Each invocation creates a new private directory under ignored
`work/nascar-reference/`. Successful eligible JSON is saved as **exact bytes** in
category/endpoint files; no formatting or value changes. Error/HTML/login bodies
are discarded. Excluded endpoint responses and `no-store` bodies are not saved,
even if they contain JSON. The local report records status, content type, UTC
start/end and duration, safe cache metadata, URL context, selected reported root
IDs/source-time values, SHA-256 and an exhaustive bounded nested schema. It does
not claim that HTTP Date, a live pathname, content changes, or a timestamp field
name proves active racing or a timezone. Node/depth/read-limit failures are
explicit rather than partial schemas presented as complete.

`--baseline` compares observed path/type sets only when both runs have schemas.
Absent fields can be a session/sample difference, not necessarily a breaking
change; requiredness and semantics still need review. Array elements are all
inspected, with union types, object counts, missing-observed and null-observed
markers. Empty arrays provide no evidence about element shapes. Reports never
automatically replace fixtures, generate production models, or commit anything.

The current cloud proxy denies CF. Add the host through the environment's normal
configuration before retrying here; do not change proxies, disable TLS, use IP
aliases or route through an alternate host. Another legitimate option is an
owner-supplied response obtained in an authorized ordinary browser, with its
exact URL, retrieval time, series/race/run IDs and authentication/cache context.
Review it privately first and use `inspect_schema` from this script for offline
inspection. Mark that evidence owner-supplied, not an anonymous direct probe.
Never copy a browser session's cookies or NASCAR credentials into this project.

## Required feature workflow

1. Read the endpoint catalog, field reference and corresponding fixture provenance.
2. Distinguish real captures, community-supported structures and synthetic cases.
3. When practical and authorized, inspect current responses for the selected
   series/season/session; avoid repeated collection of unchanged examples.
4. Review every nested shape, timestamp, unit, identifier and null/omission case.
   Record inferred semantics separately from verified facts and active-race tests.
5. Update evidence and field documentation. Keep raw captures local while rights
   are unresolved; author a minimal synthetic structural regression where needed.
6. Run offline regression checks, then CI. Keep live checks manually triggered
   and separate. Production continues using the real network adapters/polling;
   test fixtures must never supply a silent live fallback.

The subsequent Phase 3B assignment explicitly scopes evidence-limited implementation.
Read [Phase 3B evidence](../PHASE3B_EVIDENCE.md) and [validation](../PHASE3B_VALIDATION.md).
The separately [imported observed package](../nascar-api-reference/START_HERE.md)
corroborates structural fields; it does not resolve live identity, freshness,
scoring/finality semantics or permissions. Earlier proxy observations below
remain historical and are not a claim that no other source obtained responses.
