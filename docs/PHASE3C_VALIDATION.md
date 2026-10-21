# Phase 3C delivery and validation

October 21, 2026 (America/New_York). Feature branch `phase3c-race-events` starts
from latest main `219ac5f8e86c55b62f8e826e1cad8cd787d92d3d`, the squash-merged
Phase 3B PR #5. Phases 1, 2, 3A and 3B are merged. The untouched **429-test**
baseline passed from a separate ignored archive of that commit. Read AGENTS,
architecture, roadmap, original brief, Phase 3A/3B validation/evidence and the
observed API reference before implementing. No Phase 4 work was started.

## Delivered

- Typed reusable event engine over existing immutable normalized models, with
  one documented namespace and small stable payloads. All events default off.
- Supported upcoming reminders, observed lap-zero-to-green race starts,
  green/yellow/red/white/checkered changes, lead/favorite-lead changes, configurable
  favorite top-N crossings and evidence-limited embedded pit observations.
- One checkered flag-completion observation per race/run; no additional finish,
  official-result, retirement, stage-finish or championship-movement events.
- Silent setup/reload/restart/reconnect/session-switch baselines; source-clock,
  identity, health, progress, missing-driver and skipped-interval gates.
- Durable bounded high-water marks, terminal marks, event hashes, sent reminders
  and eviction floors, persisted before publication. Storage failures fail closed
  independently of schedule/entity availability. No raw feeds enter the ledger.
- One live listener, one schedule listener, bounded queue/worker and one local
  reminder timer with clean entry-owned shutdown. Source loss/switch, including
  switch-and-return during a disk write, prevents pending publication.
- Translated UI options with safe defaults and clearable preferences; existing
  entities/configuration version preserved. Diagnostics expose event readiness.
- User-enabled notification and brand-independent lighting blueprints. Queued
  light effects snapshot/restore before the next run, end early on newer flags,
  discard expired queued events and retain a recovery scene after restoration
  failure. No direct notification/device action exists in integration code.
- Roadmap merged-state corrections and a persistent final-objective checklist;
  Phases 4–6 remain History & Analytics, Premium Dashboard with dedicated data
  interface, and Beta & Release Readiness / HACS-ready distribution.

See [EVENTS.md](EVENTS.md) for contract, setup, retention, supported evidence,
intentional omissions and device-recovery limitations.

## Executed local checks

Prepared Python **3.14.8**, Home Assistant **2026.10.2** and pinned development
tools were reused. No onboarding, dependency reinstall or production access.
Automated NASCAR data is handmade synthetic, with no live network access.
The workspace's supported network-enabled command mode was needed for test
sockets and Git/public HA-source retrieval; configured proxy/TLS remained intact.
No blocked NASCAR destination was requested or bypassed.

| Check | Result |
| --- | --- |
| Untouched main baseline | **429 passed** |
| Complete `pytest -q` | **507 passed** (all 429 baseline tests plus 78 Phase 3C cases) |
| Blueprint runtime tests | **5 passed**, including rapid/latest flag colors, on/off restoration, failed command and failed-restoration recovery |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 95 Python files |
| `mypy custom_components/nascar_race_center` | Passed; 27 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Prepared independent HA runtime smoke test | **1 passed**; actual authenticated REST/state/service dispatch |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| New NASCAR probes / active-session verification | Not run; existing evidence and data-use limits preserved |
| Physical bulbs / production HA / manual browser review | Not run; real HA schemas/flows/automations and local test lights were exercised |
| HACS | Private-repository skip and temporary brands exception remain; no full HACS approval |
| Hosted GitHub Actions | Recorded in the Phase 3C PR; distinct from these local checks |

Hassfest used official Home Assistant source commit
`8d7fd8b68677c2585be36ec86043308f403875b8`, extracting only `script/` into ignored
`work/home-assistant-core`; no Docker runtime or new project dependency.

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

## Reliability and regression evidence

A replayable handmade scenario covers initial cold baseline, start, caution,
restart, lead/favorite threshold changes, pit entry/exit, red/white/checkered and
unchanged refreshes. Every repeated observation emits zero additional events.
Tests exercise all national-series contexts, race/run switches and return,
missing/future/stale clocks, unavailable sources, practice/qualifying, unknown
flags/laps/run IDs, regressing lap/elapsed progress, conflicting clocks, missing
or ambiguous driver ranks and leaderboard reordering. Missing drivers never
reappear as false top-N entries. Short missed intervals report only the observed
change; long gaps silently rebaseline. Unsupported pit clocks/laps and historical
pit rows cannot generate events. Completion never promotes provisional data to
an official result.

JSON-round-tripped ledgers verify deterministic IDs, restart/replay suppression,
completion tombstones, bounded retention and eviction floors. HA runtime tests
verify data is already saved when the bus event is observed, zero setup/reload
publication, disabled legacy behavior with zero storage work, multi-series single
publication, source failures, changed options, bounded bursts, corrupt/renamed
ledger handling and write errors. Disk-write races cover unload, outage, switch,
switch-and-return, unknown flags and future clocks. Listeners/tasks/timers stop on
unload; existing failed/cancelled setup and late coordinator completion tests
remain in the complete suite. Event startup follows successful platform setup.

Reminder tests cover future deadline crossing exactly once, initial setup inside
the window, restarted engines, changed lead time, rescheduling into the window,
schedule outage, canceled/unknown starts and missed deadlines. The actual local
reminder timer causes **zero additional provider schedule requests**. One- and
three-series event tests issue only the existing setup live read (one more on
reload), regardless of favorite preferences; there is no event-originated fetch.
Existing CF startup budgets, cache/304, optional-feed eligibility/backoff and
Recorder tests all remain passing. No transport, parser, endpoint or polling
frequency change was introduced.

Both blueprint files are substituted using Home Assistant's actual blueprint
schema, installed as real automations and executed through real scene/light
components. Notification actions call an in-process test service only. Demo and
unselected-series events are filtered. Test lights exercise yellow/red/green,
latest supported colors under rapid events, expiration, on/off/brightness/color
restoration, failure before restoration, retained recovery scene and suppression
of later effects until that scene is recovered. No external messages were sent.

## Remaining verification and data-use limits

The imported package is a redacted structural reference, not synchronized
original-response replay. Existing community mappings and inferred source-clock
semantics remain experimental. Authorized observations of a real pre-start,
start, caution/restart, pit entry, checkered, run switch and CDN outage are still
needed to verify behavior against NASCAR. Conservative gates can deliberately
omit starts, late pit records and events after outages/gaps; polling never
reconstructs an unseen timeline. Standalone pit/stage/points association stays
blocked where Phase 3B found missing IDs/clocks or unverified namespaces.

Persistence provides at-most-once publication, not guaranteed notification
receipt: a crash between save and bus publication can drop the event. Ledger
removal/older backup restoration and a source falsifying advancing clocks are
outside the guarantee. Corrupt storage disables events until a valid ledger is
restored and the entry reloaded. Light restoration needs running HA and reachable
devices; automation/HA interruption, overlapping controllers or unsupported
hardware can require manual recovery. These limits are documented for users.

MIT covers code only. NASCAR data-use, permitted polling/retention, media rights,
branding, public HACS validation, broader HA/OS/Supervisor compatibility and
release authorization remain unresolved release gates. No new NASCAR requests,
raw captures, assets, credentials, deployment, merge, visibility change or release
were made. No historical collection, dashboard or Phase 4 implementation began.
