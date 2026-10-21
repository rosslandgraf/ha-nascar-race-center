# Phase 4B — Racing analytics and comparisons validation

October 21, 2026 (America/New_York). Branch `feat/phase4b-analytics` starts from
latest merged main **907e5bba46d5017836a074197e68fd26a3093b69**, Phase 4A / PR #9.
Remote main was verified through GitHub and a subsequent successful Git fetch.
The inherited **810** cases remain in the full suite; **105 new cases** cover
analytics. No separate untouched-baseline test run is claimed.

The complete project brief, AGENTS, roadmap, architecture, history contract and
validation, observed field/relationship reference, endpoint/audit/provenance
documents and historical models/parser/provider/service were reviewed. The
prepared Python **3.14.8**, HA **2026.10.2**, Ruff **0.17.1** and mypy **2.4.0**
were reused without onboarding or dependency reinstallation.

## Delivered scope

Pure, deterministic validation and calculations over immutable Phase 4A models:
recorded lap series, exclusions/coverage/gaps, mean/median/extrema, population
standard deviation, coefficient of variation, consecutive changes, contiguous
windows, observed positions, explicit multi-driver comparison bases and numerical
differences. Selected reported race/session results, stage observations, exact
loop/average labels and original provenance stay separate from derived metrics.
Run namespaces, unknown fields, DNF text, stage conflicts and candidate sentinels
are preserved without invented semantics. Archived pits never become driver rows.

The immutable contract v1 and entry-owned `runtime_data.analytics` interface are
documented in [ANALYTICS.md](ANALYTICS.md). The service reuses HistoryService,
coalesces identical consumers and runs calculations in the HA executor with
bounded concurrent work. No new endpoint, polling, startup/periodic historical
I/O, raw archive, Recorder data, entity, frontend or authenticated transport.

## Executed checks

| Check | Actual result |
| --- | --- |
| Full `pytest -q` | **915 passed** in 32.04 seconds: inherited 810 plus 105 new cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed, including Python examples in documentation |
| `mypy custom_components/nascar_race_center` | Passed; 38 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Prepared independent HA runtime smoke | **1 passed**; authenticated REST/state/service dispatch, separate from integration behavior |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| GitHub Actions | Hosted status and run links are recorded in the Phase 4B PR after completion; no unexecuted hosted check is claimed here |
| HACS | Existing private-repository conditional skip and temporary brands exception retained; no full HACS approval |
| NASCAR network calls | **Zero**; all NASCAR-shaped responses were handmade synthetic/intercepted |
| Production HA OS / physical devices | Not exercised |

Hassfest used official `script/` from HA tag 2026.10.2, commit
`8d7fd8b68677c2585be36ec86043308f403875b8`, under ignored
`work/home-assistant-core`. The supported network-enabled execution mode was
used for Git and local HA test sockets, with inherited proxy and TLS intact.
No NASCAR host access or environment policy change was needed. Initial commands
inside the isolated network sandbox could not reach the proxy/local test sockets;
those interrupted attempts are not passing checks. The completed runs above used
the supported execution mode. No destination denial was bypassed.

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
git diff --check
```

## Independently specified numerical examples

All inputs are invented numerical examples grounded in the documented model
shapes, never source captures or redacted placeholder values.

| Synthetic input | Expected and verified result |
| --- | --- |
| Times 10, 12, 14, 16, 18 | Mean/median 14; min/fastest 10; max 18; range 8 |
| Same times: deviations -4, -2, 0, 2, 4 | Sum of squared deviations 40; population deviation `sqrt(40/5) = sqrt(8)`, about 2.8284271247461903 |
| Same times | CV `sqrt(8)/14`, about 0.20203050891044216; mean absolute consecutive change 2; four consecutive pairs |
| Valid numbered times 1 through N+2, each allowed N | Three N-lap windows; first mean/median `(N+1)/2`; exact inclusive start/end laps |
| Times 10, 12, null/invalid, 16, 18, 20 | Five valid times; mean 15.2; runs 1–2 and 4–6; no five-lap window across the exclusion |
| Sparse laps 1, 2, 4, 5 in range 1–7 | Absent lap intervals 3 and 6–7; a null on lap 4 is separately a missing time |
| Driver A at laps 1/2/4: 10/20/30; B at 2/3/4: 40/50/60 | All-available means 20/50, difference -30 and -60%; common-valid-lap means 25/50, difference -25 and -50% |
| Positions at laps 1/2/3/5: 8/6/1/3 | First 8, last 3, observed change 5, best 1, worst 8; one position-one sample; lap 4 remains absent |
| Times 10^12-1 and 10^12 | Population deviation exactly 0.5, avoiding cancellation in nearly equal large values |
| One valid time, or none | Singleton consistency unavailable; zero valid times yield unavailable time scalars with reasons |
| Constant reference-driver times | Zero deviation remains valid; relative percentage against that zero is unavailable |

Additional synthetic cases cover even medians, fastest ties, original out-of-order
arrays, explicit lap ranges, all six window sizes, unequal lap counts, empty
common bases, missing drivers, null/zero/negative/nonfinite/Boolean samples,
tiny and extreme floating-point arithmetic, candidate 999 time/average/position
values, sparse or entirely absent positions, duplicate dataset/driver/lap/stage
identities, race/season/series conflicts, results-run conflicts and unvalidated
provenance. No array order/name/car number repairs an identity.

Reported result tests preserve starting/finishing positions, completed/led laps,
race/playoff points, DNF/status text and session run namespaces. Start minus
finish is explicitly derived; no reported position-difference field is invented.
Weekend/archived stage disagreements retain both values with conflict flags;
invalid archived context leaves weekend results usable. Loop fields such as
rating remain reported, never reconstructed. Reported 999 average candidates
stay labeled; unsupported invented metric labels fail independently. Mixed
available/empty/unsupported/not-published/failed feeds preserve their own states.

## Performance and resource findings

Three untraced calculation runs per scenario used preconstructed synthetic
immutable inputs. A separate `tracemalloc` run measured allocations of validation,
calculation and output, excluding preexisting source models, HA, HTTP and JSON
decoding. These measurements are observations on this prepared environment,
not a whole-process memory limit or production latency guarantee.

| Scenario | Output | Three elapsed runs (seconds) | Retained / peak traced bytes |
| --- | --- | --- | --- |
| Largest accepted 50,000 source lap rows: ten drivers × 5,000, eight selected, five-lap rolling | 40,000 samples; 39,968 windows; 28 pairs | 0.2992 / 0.2827 / 0.2380 | 16,713,488 / 17,297,424 |
| Maximum 60,000 projected rolling points: eight drivers × 1,250 laps × six window sizes | 10,000 samples; 59,208 actual windows; 28 pairs | 0.3303 / 0.1838 / 0.1923 | 13,394,024 / 13,395,904 |

The shorter actual window count reflects insufficient leading laps for each N,
without inserting placeholders. Tests accept the 50,000-row input and reject
5,001 rows per driver, total input beyond 50,000 and excessive query complexity.
Eight selected drivers, a 5,000-number inclusive range, at most 60,000 projected
rolling points and two simultaneous requests bound entry-owned work. Consumers
own returned results and must separately bound retained client data. Source
HistoryService/HTTP memory and request limits are unchanged.

## Actual Home Assistant behavior and regression coverage

- Real HA setup and ordinary live/schedule/reference/scoring refreshes preserve
  the **seven GET** CF three-series startup budget, with **zero historical GETs**.
- Twenty identical analytics consumers through `entry.runtime_data.analytics`
  share one executor calculation and one additional intercepted lap GET (total
  eight). A repeated request recalculates from HTTP cache with no additional GET.
  The calculation thread differs from HA's event-loop thread.
- Reload closes old analytics/history services, clears historical bodies,
  preserves the existing non-history cache and shared session, and adds no GETs.
  Entity registry IDs are unchanged by analytics consumption.
- Ten full demo analytics reads add **zero Recorder state rows**. Offline demo
  analytics uses no network or bundled-fixture fallback.
- One cancelled waiter preserves shared consumers. Two distinct computation
  slots are enforced before retrieval; another selection returns
  `calculation_budget`. Underlying same-dataset retrieval stays coalesced.
- Actual entry unload, reload and HA stop cancel/drain blocked history retrieval.
  A cancelled executor job retains its slot; unload waits until the bounded pure
  worker finishes. Repeated cancellation also retains the worker bound, returns
  `calculation_draining` to a repeat request and eventually releases the slot.
  Failed/cancelled setup closes analytics, and a closed service rejects new work.
- All 810 Phase 1–4A tests remain passing, including prior HTTP/no-store/cache,
  rate-limit, request/Recorder budgets, entity IDs, schedule/reference/favorite,
  polling permission, event baseline suppression, persistence-before-publication,
  restart/replay and lifecycle tests. No event or automation behavior changed.

## Remaining evidence limits

The supplied observed historical examples establish shapes and limited identity
relationships, not all years/series/races, timing or speed units, source sentinel
definitions, comparable race conditions or final official classification. Path
provenance does not certify lap/average content identity. Numerical summaries
describe selected recorded samples only. Small/unequal/incomplete samples do not
establish driver skill or strategy. No green-flag, tire age, pit-cycle, fuel,
on-track-pass, official laps-led or championship/rating inference is added.

Anonymous current-source access, active-session behavior, permitted polling,
retention/redistribution, data/media rights, HACS release readiness and production
HA OS acceptance remain open gates. No NASCAR requests, capture redistribution,
unauthorized CF cadence change, merge, deployment, release, visibility change,
Phase 5 frontend or authenticated dashboard transport was performed.
