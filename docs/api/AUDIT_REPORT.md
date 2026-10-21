# API reference and Phases 1–3A audit

Audit date: **October 21, 2026 (America/New_York)**. Branch:
`phase-3a-live-timing`, existing [PR #3](https://github.com/rosslandgraf/ha-nascar-race-center/pull/3).
Starting head: `43d9ada1f1e87ae7ba78a946f4947e91b968b241`.
The complete root brief, AGENTS, roadmap, architecture, Phase 3A validation,
schema provenance, production adapters/coordinators/entities and regression
tests were reviewed. The unmodified **303-test baseline passed**.

## Finding and completion status

The permanent reference infrastructure and offline implementation audit are
ready for review. **The requested real-response/schema validation is blocked,
not complete.** Every original URL was freshly attempted; the environment proxy
denied every HTTPS CONNECT before a NASCAR response. No inference of NASCAR
denial, persistent Cloudflare failure or universal endpoint inaccessibility is
supported. The owner's successful browser/other-session retrieval reports remain
credible separate evidence; those JSON bodies were not supplied here.

Phase 3B remains paused. No merge, deployment, production installation, release,
repository visibility change, media access or publishing was performed.

## All-endpoint results

The [catalog](ENDPOINT_CATALOG.md) documents every exact URL, intended purpose,
series/season/race/run context, timestamp and duration, accessibility, intended
live/historical/cache behavior, related feeds, feature dependencies, limitations
and fixture availability. The [machine report](probes/2026-10-21.json) records
the anonymous urllib GETs, spaced one second apart, with ordinary TLS/proxy
configuration, no credentials/cookies, no redirects or retry loops.

| Original group | URLs attempted | Proxy CONNECT 403 | Origin responses | Usable real JSON |
| --- | --- | --- | --- | --- |
| Global live | 5 | 5 | 0 | 0 |
| Schedule/reference | 7 | 7 | 0 | 0 |
| Historical/statistical | 8 | 8 | 0 | 0 |
| Legacy/race-specific | 4 | 4 | 0 | 0 |
| Previously error/login, excluded | 4 | 4 | 0 | 0 |
| **Total** | **28** | **28** | **0** | **0** |

Origin HTTP status/content type are **unknown**, not 403/HTML/JSON. Request-path
IDs are documented as requested context, not observed response identities. No
live-session, historical-content or cache-freshness classification was verified.
A separate curl probe of the global live URL produced the same CONNECT denial.

Legitimate alternatives investigated: independent browser-tool retrieval of the
global live and season list. It exposed a JSON content-type label without an
inspectable live body/status, and an internal retrieval error for the schedule;
neither is a usable JSON sample or an origin-status observation. Existing pinned
community references remain useful structural hypotheses, not current NASCAR
captures. Do not route around the environment restriction. Add `cf.nascar.com`
through normal environment configuration, or review owner-supplied JSON with its
exact URL/retrieval/authentication/cache context. The owner was asked about the
allowlist while independent work continued.

## Permanent library and samples

- `docs/api/ENDPOINT_CATALOG.md`: complete 28-URL reference and per-request evidence.
- `docs/api/endpoints.json`: exact machine inventory, tested against the brief;
  24 owner-reported working plus four error/login, all retained in original order.
- `docs/api/SCHEMA_REFERENCE.md`: actual-observation gap, exhaustive nested
  synthetic field dictionary (91 per-file paths), exact JSON paths/types, fictional examples,
  missing/null observations, interpreted meanings, joins and unit/timezone limits.
- `docs/api/synthetic_schemas.json`: machine-readable synthetic path/type/count
  dictionaries; explicitly not observed NASCAR schemas.
- `tests/fixtures/nascar/`: six preexisting handmade files moved **byte-for-byte**,
  plus individual provenance/content hashes. All current fixture tests point here.
- `scripts/nascar_reference.py`: developer-only, explicit-authorized manual
  refresh and nested schema comparison; no CI/live integration dependency.
- Library links and maintenance instructions in README, AGENTS, CONTRIBUTING,
  architecture and prior endpoint/schema/validation evidence.

**Real JSON captures committed: 0. Real JSON captures retained locally: 0.**
Six synthetic fixtures are committed, covering minimal live, nested live timing,
basic season, detailed sessions, drivers and tracks. No fake historical, legacy
or inaccessible-endpoint capture was created. Local `work/` contains the probe
report and development tools, not NASCAR datasets or protected bodies.

The manual utility writes successful eligible raw JSON as exact original bytes
to new private, ignored `work/nascar-reference/` directories. It records safe
metadata, timestamps and hashes and inspects every nested array variant within
explicit bounds. Raw captures are never automatically promoted to Git. Excluded
and `no-store` response bodies are not retained. A schema diff compares observed
paths/types and never claims requiredness or overwrites reviewed fixtures.

## Implementation findings and corrections

**Confirmed malformed-input defect, fixed:** default JSON decoding silently
accepted duplicate object keys and retained the last value, including conflicting
`series_id` or nested `driver_id`. That could route ambiguous source identities
as if they were unambiguous. Two offline regressions failed before the change.
The shared transport now rejects duplicate keys at every nesting level as an
explicit `SchemaError`, without exposing the body. This is an implementation
robustness defect reproduced with synthetic bytes, **not an observed NASCAR
schema discrepancy**. Well-formed JSON parsing, network requests, cache behavior
and live polling architecture retain their existing contracts.

**Reference organization corrected:** the six synthetic files now share a
discoverable NASCAR directory with individual provenance and unchanged bytes.
Inventory tests prevent omitting the four prior error/login URLs. New utility
tests cover nested array variants and mixed types, omission/null observations,
schema differences, exact-byte capture, anonymous request headers, redirects,
origin versus proxy denial, malformed/ambiguous/deep/oversized bodies,
excluded/no-store retention, authorization and stopping after a server pause.

No other implementation mismatch could be **confirmed against real responses**,
because no body was obtained. The following distinguishes exercised behavior
from unresolved provider assumptions; passing mocks never closes the latter.

| Area reviewed | Existing behavior exercised by the complete suite | Unverified provider contract / practical effect |
| --- | --- | --- |
| API adapters/parsers | Strict basic `series_N`, detailed array, driver `response`, track `items`, live object contracts; invalid optional scoring isolated | Current envelopes, field spellings/types/nullability and limits remain unobserved; no guessed parser relaxation |
| Normalized models | Stable series/race/season and NASCAR-driver identities; immutable race/session/live/timing records; unique leader and read-only field lookup | Actual identity relationships/run transitions and complete-entry-list semantics unverified |
| Refresh/cache/errors | Shared HA session, independent schedule/live/reference coordinators, bounded cache/body/backoff, ETag/304, 403/404/429/503, cancellation/unload | Server directives and allowed cadence unverified; HTTP success/cache validation never resets source timestamp |
| HA entities/Recorder | Existing IDs and devices retained, compact attributes; actual HA options/setup/unload/reload; existing Recorder test suppresses unchanged favorite/lap/leader writes | Source values remain experimental; no full leaderboard or historical dataset in entity attributes |
| Season schedules/calendars | Selected-series isolation, detail failure fallback, nonempty detail independence, adjacent seasons, DST, rescheduling, overlapping sessions, unknown durations | Current date formats, UTC-named naive timestamps, publication/removal/cancellation semantics and authoritative session IDs unverified |
| Live standings/timing | One global reported series/run, whole-snapshot replacement, driver-ID lookup, optional values, no inherited prior-race field | Concurrent series coverage, actual numeric formats, lap-time/speed units and inactive/empty payload shape unverified |
| Favorites | IDs survive names/cars/teams/series changes and reference outages; one shared refresh; no per-driver requests | Directory is not a roster; slug/sponsor changes may leave series associations unknown |
| Progress/flags | Unknown codes stay unknown; fresh supported flags/laps gate activity; stale source expires locally | Current enum meanings and race lifecycle unverified; checkered is not an official finalized classification |
| Unknown values/timestamps | No zero substitution; explicit-offset strings only; malformed/naive/numeric/future source times cannot establish freshness | Actual `time_of_day_os` representation, units/timezone and schedule naive-time meaning require evidence |
| Gaps/laps led/status | Raw gap has no assigned unit; intervals not summed; only community status 1 maps to running | Negative gap/lap-deficit conventions, interval inclusivity/overlap, retirement and official result statuses unverified |

The concrete population risks documented in prior reviews remain: offset-free
times can yield race counts/names but no next-race/calendar times; unrecognized
directory slugs cannot supply numeric series; missing durations produce labeled
date notices rather than timed events; internal session IDs can change on a
rename; a global feed cannot populate three concurrent series by copying data.
These are evidence gaps, not newly verified source failures.

## Validation executed

Prepared environment reused without onboarding/dependency reinstall: Python
3.14.8, HA 2026.10.2. All NASCAR requests in automated tests are mocked.

| Check | Current result |
| --- | --- |
| Unmodified Phase 3A baseline | **303 passed** |
| Revised full `pytest -q` | **326 passed**: 303 existing + 23 new cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 60 Python files |
| `mypy custom_components/nascar_race_center` | Passed; 21 integration source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid integrations |
| Prepared independent HA runtime REST/state/service test | Passed; one test |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| Hosted CI for this follow-up | Pending push/check execution; final result will be recorded in PR #3 |
| HACS | Private-repository skip and temporary brands exception remain; not full HACS approval |
| Current-origin / active-race validation | Blocked; zero real bodies |
| Manual frontend/card review | Not run; no frontend changes |

Hassfest used official HA source
`8d7fd8b68677c2585be36ec86043308f403875b8`, retrieved to ignored `work/`.
Commands match CONTRIBUTING and the original Phase 3A validation report. Fixture
and multiprocessing sockets, Git/public-source retrieval and the explicitly
requested manual probes used supported network-enabled execution, preserving
the configured proxy/TLS policy. No denied destination was bypassed.

The complete suite re-executes earlier selected-series, offline demo,
authorization, cache/304, source-age, optional failures, startup/unload/reload,
season/timezone, favorites and actual Recorder-budget checks. This extends their
regression evidence; it does not establish live service compatibility or production
Home Assistant OS/HACS installation.

## Data use and recommendation before Phase 3B

Public accessibility does not resolve NASCAR's polling, retention,
redistribution, asset or video permissions. MIT remains code-only. No protected
content, raw feed dataset, image/logo/video or credential was committed. The
manual utility and provenance workflow provide a path for future eligible
captures while those rights remain unresolved.

Before starting Phase 3B, obtain inspectable authorized current responses for the
implemented global live, season/session and reference feeds. Resolve timestamp
representation/timezone and verify the IDs used to join races/runs/drivers.
Then review active practice/qualifying/race, checkered-to-next-session,
series-switch, stale CDN, inactive/off-season and optional-feed outage cases.
Observe actual gap/status/interval/unit behavior without inventing meanings.
No broad polling or capture redistribution should follow from this audit alone.
Future pit/stage/points features need their own observed contracts; none was
implemented here. Keep the new library as the entry point for future API work,
and keep this audit explicitly blocked on real-data validation until that work
can be completed and reviewed by the owner.
