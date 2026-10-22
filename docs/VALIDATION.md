# Current validation report

Current controlled-beta evidence: [Phase 6A validation](PHASE6A_VALIDATION.md),
[installation](PHASE6A_INSTALLATION.md), [acceptance](PHASE6A_BETA_CHECKLIST.md)
and [rollback](PHASE6A_ROLLBACK.md). Owner hardware/device results remain NOT TESTED.
The earlier evidence below retains its original phase scope.

Phase 3A checks and evidence limits are recorded in
[PHASE3A_VALIDATION.md](PHASE3A_VALIDATION.md). The Phase 2 and Phase 1 reports
below are historical records, not the current inventory or check results.

# Phase 2 delivery and validation

Validation date: 2026-10-20. Phase 2 began on feature branch
`feat/phase-2-schedules-calendars-favorites` from reviewed, squash-merged
`main` commit `0ad03aeb000a620f5e6ddc2afdedbbf9cf71eeb2`. The 113-test
Phase 1 baseline passed before implementation. The earlier report below is
retained as historical evidence, rather than the current feature inventory.

## Implemented and exercised

- All three national series retain their existing entities and configuration.
  Immutable race/session models, optional global embedded sessions and per-series
  session feeds provide complete published season schedules and multi-day
  practice/qualifying/race weekends. Malformed optional embedded sessions retain
  usable race identity/timing and expose a diagnostic failure count.
- Native read-only series calendars expose overlapping sessions and derived
  weekend date ranges through Home Assistant's actual `calendar.get_events`
  service. Valid explicit-offset start/end pairs become timed events; known
  starts without a reliable end become clearly labeled local-date notices.
  Unknown starts are omitted. Local alarms advance active events and unload
  cleanly, including overlapping weekend/session boundaries.
- Daily independent driver/track reference refreshes share the authorized CF
  transport. Driver IDs survive name, team, number and series changes. Track
  identifiers enrich calendar descriptions without making references mandatory
  for schedules. Each reference feed has independent failure/freshness state.
- Up to 50 favorite NASCAR driver IDs are editable through UI configuration and
  searchable cached options. Initial onboarding accepts optional numeric IDs;
  source-specific names become available in options after setup. Unknown IDs and
  selections survive directory outages. Compact metadata sensors expose reliable
  facts, including at most three unambiguous per-series associations. Removing
  a favorite cleans up its integration-owned metadata entity/device; retained
  favorites keep their identities across reloads.
- November/December prefetch tolerates unpublished next seasons. January startup
  discovers prior-season events with known future/ongoing times, including after
  a restart. Failed seasons remain available for diagnostics while healthy
  seasons drive calendars, counts, next-race selection and schedule-based live
  polling. A successful empty optional season cannot hide a current-season
  failure. Accepted extreme timestamps cannot overflow calendar conversion or
  boundary timers.
- CF response caching is bounded to 16 endpoints; failure counters/cooldowns are
  bounded to 24 each. Conditional validators remain cached across both seasons,
  all three series and references. Negative cooldowns prevent repeated shared
  schedule requests after denial/missing responses. Existing timeouts, response
  limits, host-wide rate-limit handling and shared-session ownership remain.

## Final local checks

The prepared Python **3.14.8** / Home Assistant **2026.10.2** environment was
reused without dependency installation. NASCAR calls in every automated test
are mocked. Integration setup tests use actual Home Assistant fixtures and its
shared aiohttp client; these are distinct from the independent environment smoke
test.

| Check | Result |
| --- | --- |
| `pytest -q` | **234 passed**, including the Phase 1 regression cases and 121 additional cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 47 Python files |
| `mypy custom_components/nascar_race_center` | Passed; 18 source files |
| Official HA `2026.10.2` Hassfest | Passed; one integration, zero invalid integrations |
| Prepared runtime smoke test | Passed; one independent test |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| HACS | Skipped while private; public visibility and brands checks remain release gates |
| Anonymous CF/current feed or active-session verification | Not run; destination policy excludes `cf.nascar.com` and data-use gates remain unresolved |
| Manual frontend/browser review | Not run; UI selectors and calendar services exercised through actual Home Assistant fixtures |

Commands used after environment activation:

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
pytest -q
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q \
  -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
git diff --check
```

Hassfest used official HA source commit
`8d7fd8b68677c2585be36ec86043308f403875b8`. The sandbox's supported network
permission was needed for fixture sockets, Hassfest multiprocessing sockets and
the configured Git proxy. Initial isolated-network attempts failed or stalled;
the final commands above succeeded with that permission and inherited proxy/TLS
settings intact. No denied CF destination was probed or bypassed.

Coverage includes DST spring/fall changes, month/year and exclusive query
boundaries, overlap alarms, cancellations supplied by normalized synthetic
models, unknown/naive/missing/overflow timestamps, rescheduling without UID
changes, conflicting/oversized schemas, multi-series drivers and metadata
changes, optional outages, stale data, cache validators/cooldowns, configuration
updates, reload/restart discovery and clean unload. The January routing
regression now expects the intentional previous-season request alongside the
current season; its original new-year routing protection is retained.

## Source limits and remaining work

Community code supports the narrow structural contracts documented in
[SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md); fixtures are handmade and do not
redistribute NASCAR feed captures or media. Current response shapes and
anonymous access remain unverified. Offset-free source values stay unknown,
including fields whose names contain `utc`. Unknown durations are never guessed.
An explicit detailed race session with an unknown/ambiguous start clears a
potentially obsolete basic race time.

The referenced schemas expose race IDs but no authoritative session ID or
cancellation/postponement status contract. Session identity excludes dates and
list order but may change on a source session rename. Revisions update schedules;
the CF adapters do not claim explicit cancellation detection. A general driver
directory does not establish an active roster; manufacturer media URLs are not
treated as names. Direct schema/time/status checks, permissions, polling limits,
branding, HACS and broader compatibility remain documented release gates.

Phase 3 still owns favorite-driver live timing/positions, standings, pits, stages,
points, session lifecycle and durable deduplicated automation events. This change
does not start that work, install on production, merge itself, change visibility
or publish a release. Hosted CI is reported separately in the pull request.

## Focused final Phase 2 review (2026-10-20)

Reviewed PR #2 at `a56ee4d2f76637ef2bc57ee1c1de4f292e7c1b50`. Its existing
234 tests passed before changes. Two defects were reproduced before fixing:

- Clearing the optional favorites selector could restore saved favorites. The
  form's validation default reinserted the previous IDs before the options step,
  and the options step also restored omitted IDs. Saved IDs now prefill through
  `suggested_value`; an omitted/empty submission persists `favorite_drivers: []`
  to override entry data. Four real-HA flow cases cover both submission forms
  with favorites stored in data or options, removal of all favorite sensors and
  unused devices, unchanged other entity/device identities, reopened forms and
  reload persistence. A separate case preserves a favorite device still used by
  another entity. Existing source-switch/outage tests now explicitly submit the
  retained IDs, as the prefilled form does; omission means clear.
- An empty optional detailed-session feed masked a failed basic schedule request
  or invalid basic envelope. It now propagates the original failure, allowing
  coordinator last-good retention and unavailable states. Two regressions failed
  before the fix. Nonempty details still work independently during a basic outage,
  and a valid empty basic season remains supported.

Additional review coverage exercises truly overlapping timed sessions: a shorter
qualifying session takes over during practice, practice resumes at its end, and
the weekend marker follows at the practice end, without HTTP requests. Reference
coordinator assertions now join schedule/live assertions across unload/reload,
failed/cancelled setup, queued refreshes and late in-flight completion. Existing
cases cover missing durations, postponed/TBD starts, session removal/revisions,
DST, exclusive month/year boundaries and January restart discovery. No additional
calendar/lifecycle implementation defect was confirmed.

Phase 1 config version/defaults and existing sensor/binary-sensor identifiers are
unchanged; no migration is needed for absent favorites. All coordinators register
shutdown with the entry on construction. Entity listeners and calendar alarms
are removed through HA unload; entry runtime data is released by HA after a
successful unload. The transport owns bounded in-memory caches and no independent
polling tasks; a reload constructs a fresh provider/cache while the old
coordinators are stopped. The shared aiohttp session remains HA-owned and open.
Platform-unload refusal intentionally keeps the loaded integration operational.

Final review checks in the prepared Python 3.14.8 / HA 2026.10.2 runtime:

| Check | Result |
| --- | --- |
| Complete `pytest -q` | **243 passed** (nine additional regression cases) |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 47 files |
| `mypy custom_components/nascar_race_center` | Passed; 18 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid integrations |
| `git diff --check` | Passed |

Hassfest uses the same official source commit and invocation documented above.
Only its scripts and translation helpers were retrieved into ignored `work/`;
no dependencies were reinstalled. Commands requiring fixture/multiprocessing
sockets and Git used supported network-enabled execution with inherited proxy
and TLS intact. No CF host request, policy bypass, manual frontend test or live
session observation occurred. Earlier runtime smoke/config results above are
historical and were not rerun for this focused review. Hosted CI is separate.

The detailed [contract review](SCHEMA_EVIDENCE.md#focused-final-phase-2-contract-review-2026-10-20)
identifies concrete real-data population risks, especially the referenced
consumer's offset-free timestamps, strict response envelopes, unknown series
slugs and missing optional durations. Timestamp timezone semantics and CF
cancellation status remain unverified. These checks establish mocked behavior
and supported-HA compatibility, not current NASCAR service compatibility.
Phase 3, merge, production deployment, release and visibility changes remain
outside this review; HACS/private/brands and data-use release gates remain open.

# Historical Phase 1 delivery and validation

Validation date: 2026-10-20. This report describes the foundation PR only. The complete product remains the target in [ROADMAP.md](../ROADMAP.md); Phase 2 waits for Phase 1 review.

## Implemented

- Single-instance UI configuration and options, selected national series 1/2/3, validated polling bounds, translated labels, and clean reload/unload.
- Offline demonstration by default. Experimental anonymous CF adapter behind explicit data-use acknowledgement; no NASCAR credentials or restricted Swagger API.
- Immutable normalized race/session models, a provider protocol, allowlisted endpoints, asynchronous shared-session HTTP, bounded caching/responses, conditional requests, timeouts, retry hints and backoff.
- Separate schedule and live coordinators; per-series schedule failure isolation; one global live request routed by its reported series; last-good data with availability/freshness diagnostics.
- Next-race name/start, schedule count, session kind, flag and current-lap sensors. Diagnostic feed status, last successful live update and source-staleness entities. No full schedules or leaderboards stored in attributes.
- Local next-race boundary and source-staleness expiry updates without another provider request; current-year routing and optional November/December next-season prefetch.
- Permanent AGENTS instructions, architecture, six-phase implementation roadmap, contributing guide, all 28 owner-reported endpoints, schema provenance, data-use notes, HACS metadata, and CI workflows.

`race_status` is the stable internal metric key; its UI label is **Session type**. The source's `run_type` identifies practice/qualifying/race, not a validated live lifecycle. Demonstration devices are explicitly marked `(Demo)`.

## Validation environment

The existing prepared environment was restored by sourcing `/workspace/.cloud-setup/nascar-race-center/activate.sh`; no onboarding or dependency reinstall was performed. Baseline: CPython 3.14.8, Home Assistant 2026.10.2, pytest 9.0.3, pytest-homeassistant-custom-component 0.13.373, Ruff 0.17.1 and mypy 2.4.0.

The independent prepared runtime smoke test passed (one test), including authenticated HA REST API, state and service dispatch. `hass --script check_config --config /workspace/.cloud-setup/nascar-race-center/hass-config` exited zero. These establish runtime restoration separately from integration behavior. No production configuration was used.

## Project checks executed

| Check | Result |
| --- | --- |
| `pytest -q` | **100 passed** in 1.94 seconds: 49 Home Assistant behavior tests and 51 transport/model/provider tests |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 32 Python files formatted |
| `mypy custom_components/nascar_race_center` | Passed; 12 source files |
| Official Hassfest, Home Assistant tag `2026.10.2` | Passed; one integration, zero invalid integrations |
| Prepared environment runtime test | Passed; one independent runtime smoke test |
| Prepared environment `hass --script check_config` | Passed; exit zero |
| Hosted Hassfest | Passed in [GitHub Actions](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39481343580/job/118830411926) |
| Hosted quality suite | Initial attempt failed before tests because Ubuntu 24.04 calls the native package `libturbojpeg`; corrected workflow is being rerun. Current results appear in the PR Checks tab. |
| HACS action | Attempted; rejected the private repository before validation. Job is now conditional on public visibility and skipped during private development. |

Hassfest was run from the official Home Assistant source at commit `8d7fd8b68677c2585be36ec86043308f403875b8`, fetched into the ignored `work/` directory, without installing dependencies:

```bash
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
```

The mocked suite covers UI configuration/authorization/interval validation, duplicate-instance prevention, options reload, clean unload and stable IDs; missing/unknown/stale/future-dated live data, series isolation and source-age diagnostics; partial/total schedule failure, first-start access denial with usable independent live data, recovery, rescheduling, local race-start transitions, optional next season and year rollover; timezone handling and schema drift; conditional caching, cache directives/eviction, bounded concurrent requests/responses, 403/404/429/503, malformed/empty JSON, timeout/connection failure, Retry-After and cancellation. No assertion is based on a request to NASCAR.

No screenshot is included: no dashboard/custom card is delivered in this phase, and UI flows were tested through Home Assistant's actual flow manager rather than manually in a browser. Hosted validation remains a distinct check; neither a configured action nor a local Hassfest result is represented as an executed HACS action.

## Evidence limits and deferred work

- **No CF endpoint was requested.** The environment destination policy excludes `cf.nascar.com`. Anonymous access, real response shapes, session freshness and current live behavior remain independently unverified. [Schema evidence](SCHEMA_EVIDENCE.md) records third-party references and the handmade fixture provenance.
- Only global season `race_list_basic.json` and global `live-feed.json` have experimental adapters. A listed endpoint is not an implemented capability. Naive source datetimes remain unknown; real next-race times may be unavailable pending verified timezone semantics.
- Permission, allowed polling rates, storage/redistribution rights and branding remain unresolved. The acknowledgement is a user decision, not a determination that access is permitted. Default demo and CI make no NASCAR requests.
- The official HACS action cannot validate private repositories; full validation remains a release gate. When available, HACS CI deliberately skips `brands`, also a release blocker. HACS compatibility metadata and passing checks do not constitute catalog acceptance or permission to publish.
- Full weekend sessions/calendars and favorite drivers are Phase 2. Detailed timing/standings, pits/stages/points and durable automation events are Phase 3. History/analytics, responsive custom cards/dashboard and release readiness are Phases 4–6. None are claimed complete.
- Broader HA/Python compatibility, Home Assistant OS/Supervisor installation, real HACS installation, manual frontend/browser review, active-session replay and event restart/deduplication checks remain future gates. No events are emitted in Phase 1.
- No merge, production installation, public release, media redistribution or release/deployment workflow is included.

## Focused final Phase 1 review (2026-10-20)

The pinned HA 2026.10.2 `DataUpdateCoordinator` constructor already registers each coordinator's `async_shutdown` override with `config_entry.async_on_unload`. HA awaits these callbacks after successful platform unload, during reload, and after failed/cancelled setup. Both overrides cancel their custom timer and then the base polling/debouncer. The small integration unload function was therefore sufficient for normal cleanup; no duplicate shutdown registration or shared-session closure was added. Its ownership comments now explain this dependency on the supported HA baseline. Failed platform unload intentionally does not stop the still-loaded platforms' coordinators.

A real race remained: a provider refresh started before shutdown could finish afterwards and re-arm a custom timer. Both coordinators now mark themselves stopped before shutdown and prevent timer registration/callback work after that point. Regression tests exercise both armed timers through real HA unload/reload, failed and cancelled platform forwarding, late schedule/live refresh completion, and queued refresh requests after unload. The replacement runtime is also unloaded and checked for inactivity past poll and timer deadlines. A separate unload-handler test verifies platform-unload refusal preserves timers until successful unload.

Timestamp parsing already rejected timezone-free dates without assuming a zone. UTC conversion now also handles range overflow as an unknown optional timestamp. New tests cover date-only values, positive/negative explicit offsets, UTC range limits, and mixed known/unknown dates. The README and schema evidence document the effect on next-race selection and polling. The scheduled-races sensor and bounded diagnostics report unknown start counts; no raw source timestamps or payloads are exposed. This remains a real CF usability limitation pending source evidence, not an assertion of timezone semantics.

The broader review checked listener ownership, options reload, failed-setup callbacks, in-flight refreshes, shared aiohttp ownership, bounded HTTP cache, retained-data availability, source expiry, and the single global live polling loop. No additional actionable lifecycle/leak/duplicate-polling defect was identified within Phase 1. No real CF request or active-session validation was performed.

Final checks on the revised source:

| Check | Result |
| --- | --- |
| `pytest -q` | **113 passed**: all 100 existing cases plus 13 new regression cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 33 Python files |
| `mypy custom_components/nascar_race_center` | Passed; 12 source files |
| Official HA `2026.10.2` Hassfest | Passed; one integration, zero invalid integrations |
| `git diff --check` | Passed |

Hassfest used the same official source commit and command documented above. Before-fix verification deliberately restored the PR's original coordinator/parser files: both late-refresh timer cases and both UTC-overflow cases failed; the revised files were restored and the full suite passed. Tests mock all NASCAR access. The sandbox needed network-enabled execution for HA fixture event-loop setup; Git and source retrieval used the configured proxy normally. No environment dependency reinstall or production configuration change was needed.

Hosted checks for the review commit are recorded in PR #1. HACS remains skipped while the repository is private; branding/data-use/source-schema release gates remain unchanged. Phase 2 has not started, visibility is unchanged, and no merge, deployment or release was performed.
