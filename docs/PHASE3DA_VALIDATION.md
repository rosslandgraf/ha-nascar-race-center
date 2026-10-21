# Phase 3D-A — CF provider compatibility

October 21, 2026 (America/New_York). Branch `phase-3d-a-cf-compatibility`
starts from latest merged main `5e4445a` (Phase 3C, PR #6). The unchanged main
baseline passed **508 tests**. This assignment makes no NASCAR requests.
The imported package is structural evidence from separately obtained snapshots;
its redacted samples are neither original responses nor replay fixtures.

## Comparison and corrections

| Area / observed evidence | Production comparison and result |
| --- | --- |
| Live object, endpoint 01 | Existing nested `vehicles[].driver.driver_id`, string `vehicle_number`, positions, lap metrics, `laps_led` intervals and Boolean `is_on_track` match. Keep status 3 unknown. Add retained `run_type_code` and `flag_state_code` so unrecognized codes survive normalization without a new semantic mapping. |
| Source clock, 01 / relationship observations | Existing `datetime.fromisoformat` accepts seven fractional digits and explicit offsets; synthetic `...1234567-04:00` becomes UTC with microsecond precision. No timestamp implementation change was needed. Numeric `time_of_day` never becomes an epoch/freshness fallback. |
| Global season object, 06 | Existing `series_1/2/3` filtering, season/race IDs and nested schedule match. `date_scheduled` and `race_date` remain distinct; no postponement inference or substitution. |
| Detailed session arrays, 09–11 | Existing `race_name`, `event_name`, race/series/track IDs, run type and paired start/end fields match. Unmatched races remain retained, reflecting the documented unmatched Cup schedule race. Added cross-source track-ID conflict rejection: optional details cannot overwrite an independently valid basic race with contradictory venue context. This is a synthetic consistency regression, not an observed conflicting track pair. |
| Schedule time strings, 06 / 09–12 | Observed strings lack offsets, including `*_utc`. Existing policy deliberately leaves them unknown. Counts/names can work while next-race starts and calendar entries remain unavailable. No timezone, end/duration or cancellation status is invented. Retain session `run_type_code`, including observed code 0 with unknown kind. |
| Per-series basic array, 12 | Different envelope from global 06. The production provider requests 06, never 12; retain its strict global-envelope parser and existing request set. No alternate endpoint/fallback fetch was added. |
| Driver directory, 07 | Existing `response` wrapper and NASCAR identity match. `Driver_ID` remains a separate namespace; unknown/blank series labels do not become numeric associations. **Corrected field assumption:** 653 of 915 observed `Team` strings are numeric. Preserve bounded original text as `DriverAssociation.team_raw`; leave the team display name unknown for numeric strings. Do not interpret them as team IDs, resolve them elsewhere or expose them in entities/diagnostics. Textual labels retain existing behavior. |
| Track reference, 08 | Existing `items`, `track_id`, numeric length and optional locality/type/surface match. Null `races` and media fields are ignored. No timezone is inferred. |
| Embedded pits / stage, 01 | Existing `positions_gained_lossed` spelling, parent NASCAR driver identity and `stage_num` / `finish_at_lap` / `laps_in_stage` match. Existing zero/negative physical-value handling and optional-failure isolation remain. No completed-stop/stage count or duration subtraction. |
| Standalone pits/stages/points, 03–05 | Existing Phase 3B parsers match documented fields. Pits lack driver/race context; stage race differs from live and lacks series/time; points context IDs are zero. Preserve the existing namespace/freshness gates and `unsupported_association`; all three stay excluded from automatic polling. No new associations or scoring formulas. |

The field comparison uses
[observed profiles](nascar-api-reference/Documentation/field_profiles.json),
[formats and limits](nascar-api-reference/Documentation/findings.md),
[identifier relationships](nascar-api-reference/Documentation/verified_relationships.json)
and [observed codes](nascar-api-reference/Documentation/observed_code_domains.json).
A matching field/type is not a verified unit, enum meaning, requiredness or
current-session contract. Existing community-supported flag/run/status meanings
remain experimental; this phase adds no meanings.

## Pipeline diagnostics and transport corrections

`cf_pipeline.transport` reports at most 24 allowlisted paths, each with delivery
(`network`, `cache`, `revalidated`, `cooldown`, `cancelled`), transport outcome,
last surfaced HTTP status, JSON status and local response-header receipt time.
No body, headers, validators, URLs, names, team values, config secrets or exception
text is exported. Cache reads retain the original response time; 304 establishes
cache revalidation, not a new body or new source timestamp. A cooldown makes no
request. A surfaced HTTP status alone does not identify whether an intermediary
or NASCAR generated it; a connection error supplies no origin status.

`cf_pipeline.parsers` retains at most 24 outcomes: `not_parsed` after an
unsuccessful transport/JSON read, `invalid` for domain schema/identity failure,
`parsed` for successful normalization (including the existing null/no-session
contract), or `context_conflict` for contradictory schedule track identities.
Basic/session schedule outcomes include year and selected series, so parsing a
shared cached list for one series cannot erase another series' failure.
Reference success/failure and normalized counts remain under `reference`.

`live` adds raw numeric codes, selected-series match, per-series health,
`usable_timing` and `retained_last_good`. Existing race/run IDs, source clock,
optional-field failure counts and schedule/reference counts remain available.
Inspect both transport and parsing: valid JSON does not establish the expected
race or fresh usable timing, and retained old context must not look current.

Two synthetic transport defects were also corrected: Python's JSON decoder
accepted non-JSON NaN/Infinity literals, and body/JSON schema errors discarded a
known HTTP 200 (likewise an invalid cacheless 304 lost its known status). Reject
those literals, retain the surfaced status on these errors, and normalize decoder
resource failures to safe schema errors. These are implementation robustness
fixes, not claims that NASCAR emitted malformed JSON. Cache TTLs, request bounds,
coordinator polling, error backoff and server retry hints are unchanged.

## Executed validation

Prepared Python **3.14.8**, HA **2026.10.2** and development tools were reused;
no onboarding or dependency reinstall. Network-enabled command execution was
needed for test sockets, Git and official public HA source retrieval. Inherited
proxy/TLS policy was preserved. No NASCAR endpoint was attempted.

| Check | Actual result |
| --- | --- |
| Untouched main `pytest -q` | **508 passed** |
| Complete revised `pytest -q` | **546 passed**, including all prior tests and 38 new cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |
| `mypy custom_components/nascar_race_center` | Passed; 27 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Independent prepared HA runtime smoke | **1 passed**; authenticated REST/state/service dispatch, separate from the integration tests |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| HACS | Private-repository skip / temporary brands exception remain; not full HACS approval |
| NASCAR GETs, original-response replay, HA OS live session, physical devices | Not performed; authorization/network/live-evidence gates remain open |

New synthetic files have [individual scope/provenance](../tests/fixtures/phase3da/README.md).
Every fixture path and JSON type is checked against the observed field profiles;
scalar values are handmade. Additional mutations are explicitly synthetic error
or unknown-value cases. The real HA tests exercise the actual CF provider, shared
transport, coordinators, favorite metadata/position and stage entities, and
redacted diagnostics for two reported series. Three-series startup remains
**seven GETs**, independent of favorite count, with no standalone scoring request.
Immediate cached refresh adds zero GETs; failed JSON after cache expiry leaves
schedule data usable, marks timing unavailable and labels retained last-good
context. Prior demo, Recorder, lifecycle, event baseline/persistence/replay,
rate-limit, optional-scoring and season/time-boundary regressions all pass.

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
pytest -q
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
git diff --check
```

Hassfest used only `script/` from official HA source commit
`8d7fd8b68677c2585be36ec86043308f403875b8`, extracted under ignored `work/`.
Hosted checks are reported in the pull request separately.

## Remaining acceptance gates

Follow the [authorized HA OS procedure](CF_LIVE_VALIDATION.md) when approved.
Actual current responses must verify race/series/run identity, source clock and
freshness, full directory identity/name behavior, schedule publication/revisions
and timezone semantics, inactive feeds, practice/race/session switches and
optional-field variations. Authorized pre-start/active/checkered/reconnect
observations and replay are still needed for event semantics. Single redacted
snapshots and passing mocks cannot certify those behaviors or HA OS/Supervisor
installation. Existing `elapsed_seconds` naming is retained for compatibility;
its source unit remains unverified and no new conversion is introduced.

NASCAR data use, polling/retention/redistribution permission, asset rights and
allowed cadence remain unresolved. MIT covers code only. No deployment,
publication, visibility change, merge, historical analytics, frontend, new
automation or Phase 3D-B work is included.
