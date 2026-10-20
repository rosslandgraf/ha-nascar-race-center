# Phase 1 delivery and validation

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
