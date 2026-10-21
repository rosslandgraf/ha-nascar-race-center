# Phase 5A — Focused pagination correction validation

October 21, 2026 (America/New_York). Existing branch
`feat/phase5a-dashboard-api`, existing PR #11. Correction starts at **df9e614**;
merged Phase 4B remains **926e669**. No new PR, Phase 5B, merge, deployment,
publication, visibility change or NASCAR network access.

## Concrete reproduction and root cause

Before changing production code, `pytest -q tests/test_dashboard_pagination.py`
ran two actual Home Assistant WebSocket cases against the original PR head.
Both **failed**: three selected datasets and all seven selected datasets returned
a successful first page, followed immediately by **`snapshot_changed` on page 2**.
The intercepted CF inputs were the handmade observed-shape Phase 4A fixtures,
requested for key `(2024, 1, 88001)` with a two-record page size. They were not
already-constructed `HistoryResponse` mocks. The path was authenticated HA socket
→ registered command → `DashboardRuntime` → real `HistoryService` →
`CFHistoryProvider` → the entry's shared `NascarApiClient`/aiohttp session.
First-page GET counts were **10** and **14**, including seven normal startup GETs.
Every selected dataset was available on the first page.

The original dashboard called `history.async_get(key, datasets)` on **every page**.
HistoryService releases normalized results after its last waiter. The HTTP cache
retains only two historical bodies; selecting three/seven evicts earlier documents.
Per-endpoint request deadlines survive eviction. Immediate rereads of evicted
paths therefore raise `PollingDeferred` under the existing **60-second floor**.
The history provider represents these as network/access failures, changing the
semantic rows/status hashed by the page builder. Hence `snapshot_changed`, despite
unchanged upstream fixtures. Waiting out the floor could trigger more GETs and
still could not guarantee one consistent content version.

The original pagination tests predominantly reused preconstructed results. They
verified serializers but did not cover this service/transport/cache interaction.

## Exact correction and lifecycle

`dashboard_snapshots.py` provides a bounded immutable serialized row index for
history **and analytics**, owned by the entry runtime and budgeted through one
HA-instance store. Admission reserves a full slot **before service retrieval**.
The first request uses the existing history/analytics service exactly once,
projects allowlisted normalized fields and hashes content once in HA's executor.
Only serialized header/record bytes and their index survive construction. Raw CF
bodies, full normalized source models and analytics calculation objects are not
retained by the snapshot. Existing service/transport caches are unchanged.

The opaque random/content-bound token identifies the entry runtime, authenticated
user, originating socket, command, race key, ordered dataset selection, all
analytics query options and immutable content version. All native authentication,
active-administrator, loaded-entry and monitored-series checks still run. Offset
and page size can change; selection cannot. Token replay at offset zero rereads
the pinned snapshot. Offset zero without a token starts a new selection.

Continuations decode only the requested indexed rows: **no history retrieval,
network GET, analytics recalculation or complete serialization/hash pass**. Source
changes leave an issued snapshot intact; a fresh selection sees the service's
current result, respecting its HTTP freshness and request floor. Explicit partial
source availability stays pinned rather than silently acquiring/dropping records.

- **Four slots globally**, across all config entries/users, including construction
  and cancellation drain; **two per user**, across entries/tabs.
- **24 MiB per slot**, **100,000 records**, at most **96 MiB** reserved index storage.
  Accounting includes encoded bytes/object overhead, conservative list/tuple
  pointers and metadata allowance. This supports measured 50,000-lap and roughly
  80,000-record analytics streams without enlarging the raw HTTP cache.
- **300-second fixed lifetime** from completed construction; no sliding renewal.
  Expiry removes data and its connection cleanup registration. Completed streams
  remain replayable only for that lifetime. No admission-driven eviction.
- Disconnect releases only that connection's snapshots. Unload/reload/shutdown
  cancels/drains work and removes the owner's snapshots. Canceled builders retain
  reservations and request slots until their executor worker drains.
- `snapshot_limit` fails before retrieval. Memory/record overflow or any unpageable
  record (including one after the first page) fails **before issuing a token**.
- Existing **256 KiB envelope**, **1–200 rows/page**, **30 commands/10 seconds**,
  **8 requests/entry**, **2 requests/user/entry**, subscriptions, native HA queues,
  source/service computation budgets and cancellation behavior remain in force.

The 96 MiB bound is **additional indexed storage**, not total process RSS. Existing
bounded HTTP JSON decoding, normalized service results, analytics workers, HA
queues and returned page objects apply additionally. At most four globally
reserved snapshot constructions can hold their temporary service results; decoded
pages remain bounded by existing request and response limits. Traced measurements
below exclude source models, HTTP decoding and the Home Assistant process.

Schedule/live-detail commands retain their lightweight stateless content digests.
No endpoint, polling timer, historical prefetch, disk archive or formula was added.

## Regression coverage and executed checks

`tests/test_dashboard_pagination.py` adds **27 actual HA WebSocket cases**:

- Retrieve **every page** with three distinct datasets and with all seven; compare
  the concatenation against independently parsed original fixture record sequences.
  Immediate next-page requests add zero GETs and cannot hit the request floor.
- Full all-seven-dataset navigation with **50,028 history records** and **79,324
  analytics records**; ordered stream digests and total counts prove no loss or
  duplication. Every response fits the byte limit and the index fits its budget.
- A changed intercepted CF lap time is visible in a fresh selection after ordinary
  cache release and 61 seconds of transport-clock advance. The old token still
  reproduces the original lap time and adds no GETs.
- Reject modified, expired, wrong-race, wrong-dataset, other-tab, other-user,
  other-entry and revoked-admin tokens without upstream calls. Analytics tokens
  also bind driver IDs, windows, lap range and time basis. Page-size changes and
  offset-zero replay work.
- Actual socket disconnect, timer expiry, unload, reload and HA stop release
  retained indexes. Shared global admission across entries, user admission,
  over-budget selection and an oversized later row fail explicitly.

Existing tests now target the index worker when testing cancellation drain and
assert that only the surviving peer's snapshot remains. The Recorder test replays
its two pinned history/analytics tokens, verifying **zero new Recorder rows** for
20 reads plus a live subscription. Inherited tests continue covering concurrent
service sharing, blocked-request cancellation, stop/unload/reload, authentication,
rate limits, normal live polling, HTTP safeguards, events and Recorder behavior.
An initial full run exposed the Recorder test's repeated creation of new sessions;
its calls were corrected to follow the bounded token lifecycle, then rerun.

| Check | Actual result |
| --- | --- |
| Focused pagination tests | **27 passed in 7.24 s** |
| Full pytest suite | **1,004 passed in 52.48 s**; original 977 plus 27 new WebSocket cases |
| Ruff lint / formatting | Passed after correction |
| Strict mypy | Passed; **44** integration source files |
| Official HA **2026.10.2** Hassfest | Passed; **1 integration, 0 invalid** |
| Independent prepared HA runtime smoke | **1 passed in 0.23 s**; independent REST/state/service smoke, not a NASCAR test |
| `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| Hosted GitHub Actions | Correction push triggers existing workflows; hosted results appended after completion |
| HACS | Existing private-repository conditional skip/brands exception retained; no full HACS approval |
| NASCAR / production / visual frontend | No network access, deployment or frontend work |

The prepared Python **3.14.8**, Home Assistant **2026.10.2**, Ruff **0.17.1** and
mypy **2.4.0** were reused. Official Hassfest source is tag 2026.10.2,
`8d7fd8b68677c2585be36ec86043308f403875b8`, under ignored
`work/home-assistant-core`. GitHub retrieval and local test/multiprocessing sockets
use the supported network-enabled execution mode with inherited proxy/TLS intact;
CF is not allowed in the environment policy and was never requested.

Reproduce:

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
pytest -q -s tests/test_dashboard_pagination.py tests/test_dashboard_performance.py
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

## Measured request, response and memory budgets

All measurements are local/synthetic, not NASCAR latency or a service promise.
Large WebSocket tests use intercepted CF HTTP, real parsers/services and all seven
datasets. The synthetic client clock advances 0.35 s per continuation to model
compliant request pacing; production rate limiting is unchanged. Expiry still uses
the actual loop clock. No test bypasses the HTTP floor.

| Actual HA WebSocket stream | Records | First page including retrieval/calculation/index | Subsequent mean / max | Largest continuation JSON | Accounted index bytes | Continuation GETs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 drivers × 5,000 historical laps, all seven datasets | 50,028 | 0.543 s | 0.00272 / 0.00653 s | 36,254 | 10,906,062 | **0** |
| 8 drivers × 1,250 laps, 6 analytics windows, all seven datasets | 79,324 | 1.355 s | 0.00287 / 0.00561 s | 217,526 | 19,086,650 | **0** |

Both large scenarios make **14 GETs total: 7 startup + 7 explicitly selected
historical documents**, independent of page count. The smaller three-dataset
scenario makes **10 total**. Normal live/bootstrap/subscription startup stays at
**7**. Full navigation does not change the two-document transport cache, 2 MiB
HTTP document cap, historical parser limits, 60-second per-endpoint floor,
Cache-Control/validators, Retry-After or host backoff.

Separate preconstructed-model measurements isolate projection/index cost from
HTTP/service/calculation cost. First build and subsequent reads are timed
separately; traced allocation is a separate build:

| Stream | Build | First indexed read / subsequent read | JSON bytes | Accounted / retained traced / peak traced bytes |
| --- | ---: | ---: | ---: | ---: |
| 50,010 history records | 0.364 s | 0.00052 / 0.00050 s | 32,108 | 10,749,010 / 9,947,972 / 10,393,337 |
| 79,316 analytics records | 0.809 s | 0.00065 / 0.00080 s | 55,150 | 19,001,876 / 17,792,919 / 18,509,793 |

The original PR repeatedly projected/hashed the complete stream on every page
(previously measured roughly 0.43–0.61 s/history and 1.04–1.81 s/analytics page).
The corrected runtime pays that cost once. Continuation work scales with returned
rows and header size. Live 100-driver delivery/coalescing tests remain unchanged.

## Remaining limitations

Administrator-only access remains intentional. A token cannot resume after socket
loss, reload, expiry or restart. Clients should request 200 rows/page for large
streams and finish within five minutes while respecting rate limits. Extremely
small pages/long pauses can expire; no infinite retention is promised. At most two
simultaneous selections per user and four globally can be pinned; wait for expiry
or close the owning socket to release completed selections. There is no new release
endpoint. Explicit over-budget selections must be narrowed by the consumer; all
seven datasets remain supported within the declared budget.

Fresh selections still respect normal provider freshness/floor/backoff; snapshots
do not repair genuinely missing/partial source data. Existing snapshot tokens
from the uncorrected PR require starting over after this update/reload.

NASCAR rights, source units/sentinels, anonymous access, active-race validation,
broader historical coverage, faster cadence permission, public HACS/brands and
production HA OS acceptance remain open. MIT applies to code only. This change
makes the existing Phase 5A interface reliable within explicit finite resources;
it does not begin Phase 5B.
