# Phase 3A delivery and validation

Validation date: October 20, 2026 (America/New_York). Work began from latest
`origin/main` commit `fb88120`, containing reviewed/merged Phases 1 and 2.
The unmodified **243-test baseline passed** before development. Feature branch:
`phase-3a-live-timing`. Checkpoint commits were pushed during development.

## Implemented

- Experimental CF live adapter extends only the existing global live endpoint.
  Immutable reported field, read-only NASCAR-ID lookup and deterministic position
  order cover the usable reported competitors, including all three national
  series. No assumption of concurrent series coverage or an official full roster.
- Optional driver ID/name/car/manufacturer, position/start-position change,
  last/best laps, reported gaps and speed fields, completed laps, raw status code,
  on-track boolean and reported laps-led intervals. No guessed gap units,
  retirement mapping, team, interval-to-next or laps-led aggregate.
- Reported run identity/name, elapsed time, current/total/remaining laps and flags.
  One unique reported first position supplies a compact leader sensor. New
  session-progress observations require fresh supported flag evidence; checkered
  completion does not imply official finalized results.
- Favorite position plus opt-in last/best lap, reported gap, running status and
  start-position-change sensors. Existing metadata IDs/devices remain stable;
  timing works without a reference directory. Only position is enabled by
  default, with six registered metrics per favorite independent of series count.
  Options removal cleans up all recognized favorite metrics and unused devices.
- `LiveView` separates field facts, source health and evidence-limited progress.
  Global series/run/race changes replace the entire snapshot; missing competitors
  and omitted values never inherit old race data. Scoring schema drift leaves
  independent flag/lap data usable. Failed/stale fields remain diagnostic context
  and cannot supply current scoring.
- Shared coordinators, transport cache/validators/backoff and polling bounds
  retained. No additional CF endpoint, per-driver request, alternate-series
  polling, background task or persisted timing/history store. Unknown/track-only
  flags no longer accelerate polling. Local stale expiry and entry-owned
  unload/reload/shutdown keep their existing lifecycle protections.
- Bounded diagnostic counts and lightweight states. Actual Recorder measurement
  proves timestamp-only and other-driver changes do not add rows for unchanged
  favorite position, current lap or leader. Legacy `source_updated_at` attributes
  now follow the last meaningful sample; diagnostics supply latest source and
  transport timestamps. The optional transport timestamp entity stays disabled.

## Executed local checks

The prepared environment was restored through
`/workspace/.cloud-setup/nascar-race-center/activate.sh`, without reinstalling
packages or re-onboarding Home Assistant: Python **3.14.8**, Home Assistant
**2026.10.2**, pytest **9.0.3**, Ruff **0.17.1**, mypy **2.4.0**.
Every NASCAR request in automated checks is mocked.

| Check | Result |
| --- | --- |
| Entire `pytest -q` | **303 passed**; 243 baseline plus 60 additional cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 53 Python files |
| `mypy custom_components/nascar_race_center` | Passed; 21 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid integrations |
| Independent prepared-runtime smoke test | Passed; one authenticated REST/state/service test |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| HACS | Skipped while private; branding and full public validation remain release gates |
| Direct anonymous CF / current live-session validation | Not run; host excluded by policy and data-use gates unresolved |
| Manual frontend/browser review | Not run; no dashboard/card delivered; entity/options behavior uses real HA fixtures |

Hassfest used the official HA source at
`8d7fd8b68677c2585be36ec86043308f403875b8` (the documented 2026.10.2 baseline),
retrieved from GitHub's public source archive into ignored `work/`. Only scripts
were extracted; the installed dependency baseline was reused.

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q \
  -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
git diff --check
```

Commands needing fixture/multiprocessing sockets, Git and public source retrieval
used the supported network permission with inherited proxy and TLS intact.
No destination restriction was bypassed. GitHub repository/PR operations use the
connected GitHub app where the CLI's API access is unavailable. Hosted CI results
are separate and will be linked in the pull request.

## Coverage and measured budgets

Synthetic model cases exercise 40-car fields in all three series, ordering,
read-only identities, leading-zero car numbers, unknown/unranked drivers,
missing/empty/partly malformed fields, duplicate identities/ranks, schema bounds,
nonfinite/invalid numeric fields, unknown status codes, signed/zero gaps,
invalid laps-led intervals and unsupported timestamp representations. A real
transport/adapter test verifies cache hits and 304s preserve original source time
and scoring rather than refreshing their age.

Actual HA cases exercise favorite metadata outages, live optional entity enablement,
position/lead changes, run/race/series switches, race-to-practice reset,
unselected-series routing, empty source, fresh checkered and stale checkered
observations, unknown/cold/hot flags, lap zero, absent/future/old source clocks,
missing metrics, invalid optional scoring, 403/429/503 retention/recovery,
source expiry without a provider request, options cleanup, reload/listener/timer
shutdown and shared-session ownership. Existing failed/cancelled/in-flight setup
and unload regressions remain in the entire suite.

A CF setup with three series and unavailable driver/track directories makes
exactly **seven mocked requests**: one basic season, three optional session
feeds, two references and one global live feed. An immediate live refresh reuses
cache and adds zero requests. Fifty favorites register 300 live entities but
only **50 live-position entities are enabled by default**, with one provider
refresh total; field entries never create their own entities.

The actual HA in-memory Recorder test records a baseline, then applies **ten**
whole-field refreshes with advancing source time and changed nonfavorite timing:
**zero added rows** for the unchanged favorite position, current lap and leader.
One subsequent favorite-position change adds **exactly one favorite row**, with
no extra lap/leader rows. This is a controlled synthetic write-budget check,
not an estimate of live race traffic or a production Recorder benchmark.
The pre-fix experiment reproduced ten unnecessary current-lap rows even when
`source_updated_at` was excluded from recorded attributes; the changed-sample
callback fixes that behavior.

## Evidence limits and remaining work

Before implementation, the pinned TannerYohe live model and ooohfascinating
live-feed document were read through GitHub. Their exact provenance and narrow
contract are in [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md) and the handmade
[Phase 3A fixture notes](../tests/fixtures/PHASE3A_LIVE.md). They are community
schema hypotheses, not official/current NASCAR verification or data-use grants.
No NASCAR endpoint was requested, and no feed capture, assets or third-party
implementation is distributed. Offline demo still works with fictional
schedules/references and an empty live feed.

Unverified source-time semantics, current anonymous access, permitted cadence,
status-code meanings beyond running, gap units/negative values, laps-led interval
inclusivity, media/branding and storage/redistribution rights remain explicit
gates. Optional omission is not a zero, retirement, empty official entry list,
final result or concurrent series session. Unknown freshness can show reported
facts but cannot establish active/completed progress. Practice sentinel lap
totals are preserved as reported, without derived race-distance percentages.

The leaderboard is a reusable internal normalized model, not a frontend or
historical data API. A full-field dashboard/data endpoint, verified active-session
observations, broader HA/Python/OS/Supervisor compatibility, full HACS validation
and permission review remain future gates. Pit stops, stages, championship
points, flag timelines, automation events/deduplication and Phase 3B/3C are not
started. No merge, deployment, production installation, visibility change,
release or publication is part of this work.
