# Phase 3D-B — Adaptive polling validation

October 21, 2026 (America/New_York). Branch `phase3d-b-adaptive-polling` starts
from merged main **b1f1468**, including Phase 3D-A PR #7. The unchanged baseline
passed **546 tests**. The original brief, current instructions, roadmap,
architecture, API catalog/field/provenance/audit records, Phase 3C/3D-A validation,
HTTP/provider/configuration and event implementation were reviewed.

## Capability, synthetic results and actual CF boundary

| Category | Actual result / limitation |
| --- | --- |
| Implemented capability | Adaptive 10-second race/practice/qualifying targets; configurable 30–60-second approach, five-minute session discovery/gaps, hourly idle/overnight and six-hour off-season targets, subject to provider/server/source constraints |
| Measured normalized-provider performance | Each race/practice/qualifying scenario: **61 scheduled reads in 600 simulated seconds**, startup included; **60 consecutive intervals of exactly 10 seconds** using HA's actual coordinator scheduler and test clock |
| Measured HTTP performance | Each session kind: **61 mocked GETs in 600 simulated seconds**, including startup; real shared NascarApiClient, 10-second fallback/request floor, three series and ten favorites. Practice/qualifying have zero session laps and no supported race flag |
| Current CF frequency | Conservative policy remains default. Adaptive options cannot enable CF fast operation. Automatic active-observation floor remains **300–3600 seconds**, existing race-discovery window **900 seconds**, nearby idle **3600 seconds**, off-season **21600 seconds**, with larger cache/cooldown/backoff limits respected |
| Real CF traffic in this assignment | **Zero** NASCAR probes, captures or live-provider requests. All endpoint-shaped automated calls are intercepted synthetic responses |
| Actual NASCAR feed latency | **Unverified**; no claim of a 10-second real-world delivery guarantee or authorized 10-second NASCAR cadence |

Tests use the actual HA scheduler with its fake-clock timer helper; these measure
deterministic scheduling and request behavior, not wall-clock network/server
latency. The steady active synthetic budget is at most **360 GETs/hour**, excluding
one startup read. Approach budgets are 60–120/hour; five-minute discovery 12/hour;
idle one/hour; off-season four/day. These are capability budgets, not NASCAR
permission. CF's default active ceiling is twelve/hour, excluding startup, and
can only fall with source/server limits. See [POLLING.md](POLLING.md) for exact
evidence, options, conservative compatibility and future authorization rules.

## Executed checks

Prepared Python **3.14.8**, Home Assistant **2026.10.2** and pinned development
tools were reused without reinstall/onboarding. Supported network-enabled
execution was used for test sockets, Git and official HA-source retrieval, with
the inherited proxy and TLS policy intact. No NASCAR destination was attempted.

| Check | Actual result |
| --- | --- |
| Untouched main pytest baseline | **546 passed** |
| Complete revised `pytest -q` | **615 passed**: all baseline cases plus 69 new cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |
| `mypy custom_components/nascar_race_center` | Passed; 29 integration source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Independent prepared HA runtime smoke | **1 passed**; authenticated REST/state/service dispatch, separate from NASCAR integration tests |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| First pushed checkpoint `eb8bb26` | [Tests and quality passed](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39632466287); [Integration validation passed](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39632466212) |
| Final-head hosted checks | Recorded in the Phase 3D-B pull request after its final push |
| HACS | Private-repository job remains skipped; temporary brands exception remains. No full HACS approval claimed |
| NASCAR/HA OS production/physical devices | Not exercised; permission/live-source/installation gates remain open |

Hassfest used `script/` from official HA commit
`8d7fd8b68677c2585be36ec86043308f403875b8`, extracted under ignored `work/`.
No Docker build, dependency reinstall or production installation was needed.

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

## Synthetic evidence and compatibility findings

New cases in `test_adaptive_polling.py` and `test_adaptive_runtime.py` use handmade
normalized observations, existing structural fixtures with explicit synthetic
mutations, or tiny fake HTTP responses. There are no new CF JSON fields or raw
NASCAR captures. Practice/qualifying evidence uses the existing reported
`vehicles[].is_on_track` field with recognized run kind and complete fresh run
identity. Its real active-session semantics remain an acceptance gate.

The cases cover race/practice/qualifying activity, zero/unknown laps, missing run
and session identity, future/stale/regressing/frozen source clocks, selected-series
and run changes, approaching/unknown/canceled starts, bounded discovery after
start, gaps/overnight/weekend end/off-season, schedule revisions and automatic
re-arming. Six scheduled scenarios vary session kind and favorite count; real HA
entities and Phase 3C listeners consume their observations with no extra reads.
An advancing source recovers from a frozen-clock slowdown automatically.

Transport cases measure ten-second fallback expiry, validator/304 reuse, explicit
120-second freshness, a **172800-second** upstream lifetime (no early one-day
request), Date/Expires age accounting, and replacement of old Age on 304.
Concurrent batches of twenty reads produce **one** network request per slot for
both no-cache and no-store; all nineteen waiting readers defer. Expired explicit
upstream freshness also defers until conditional revalidation is eligible; a local
request floor never waives must-revalidate. No-store retains no body.
200/304/403/429/503 Retry-After hints prevent early requests. Existing repeated
failure/backoff reset, malformed/oversize body, denial, timeout, host-wide 429,
validator, cache-bound and cancellation regressions also pass.

CF is tested with **300 attempted reads across one 300-second simulated slot**:
one GET before its deadline, one more at the eligible deadline. Selecting
Adaptive leaves `fast_permitted=false`, preserves the 900-second discovery
budget and cannot supply permission. The existing all-series setup budget remains
**seven GETs** in the mocked single-season case: one shared basic schedule,
three session-detail reads, one live read and two references. Existing one/three
series and varying-favorite setup cases still pass. Standalone pit/stage/point
requests remain **zero**.

A new client's restored HA Store reservation prevents requests before its saved
deadline, including a **900-second** server cooldown. The host-wide 429 deadline
also blocks a new schedule request after restore. Cancellation preserves the
reserved slot. A swallowed/no-op storage write blocks live I/O before any GET.
Normal HA reload retains the bounded in-memory CF cache/cooldowns, preserving
existing enabled stage/pit observations and avoiding extra refresh requests.
Real process restart retains deadlines only; missing live data stays unavailable
until the next permitted observation. Malformed persisted host clocks fail closed for live requests without crashing
schedule reads. Storage corruption/failure fails closed;
clearing/rolling back storage or using multiple independent installations is
outside that reservation guarantee.

The new actual Recorder test schedules ten unchanged observations at ten-second
intervals: **zero additional rows** for watched favorite position/current lap/
leader. One changed favorite position then produces **exactly one** favorite
row and zero extra lap/leader rows. Existing Phase 3A/3B Recorder tests also pass.
Full fields and polling diagnostics never become new entity history attributes.

One changed race flag at 30 seconds emits exactly one existing Phase 3C flag event;
its deduplication ID is present in the durable ledger. Practice/qualifying emit
zero race events. All prior persistence-before-publication, restart/replay,
source-expiry, missing-driver, switch and event meaning tests pass. No event
type/meaning or blueprint behavior changed.

Real options-flow tests verify valid adaptive reload with preserved entity IDs,
configuration version 1 and conservative defaults for missing legacy options.
Invalid policy and out-of-range/Boolean/fractional approach values are rejected.
HA failed/cancelled fast setup removes the polling/schedule listeners; scheduled
reads stop after unload. Existing reload/unload, in-flight cancellation and late
completion regressions remain passing. No custom live polling task was added.

## Remaining limits

The regular offline demo intentionally still has no active race. This phase
implements capability and synthetic measurements; authorized current NASCAR
observations must separately verify timestamp progression, on-track semantics,
run/series switches, CDN behavior, actual latency and permitted cadence. Use the
future [authorized HA OS procedure](CF_LIVE_VALIDATION.md) only within its
separately approved scope. Faster polling cannot reconstruct missed events or
turn checkered observations into official results.

NASCAR data-use, cadence, retention/redistribution and media rights remain
unresolved. MIT remains code-only. No visibility change, deployment, publication,
merge, production access, Phase 4 history or Phase 5 dashboard work occurred.
