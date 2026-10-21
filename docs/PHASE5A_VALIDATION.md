# Phase 5A — Authenticated dashboard transport validation

October 21, 2026 (America/New_York). Branch `feat/phase5a-dashboard-api` starts
from latest merged `origin/main`, Phase 4B / PR #10, squash commit
**926e6693be9250de5a2716d7d799fba901385a11**. A successful Git fetch confirmed this
base. The inherited 915 tests remain in the final suite. No separate untouched
baseline test execution is claimed.

The full product brief, AGENTS, roadmap, architecture, history/analytics/polling
contracts, Phase 4A/4B validation, endpoint catalog/field reference/audit and fixture
provenance were reviewed. Existing live/schedule/reference/scoring/event/history/
analytics boundaries were inspected before transport implementation. Official
[current WebSocket extension](https://contributors.home-assistant.io/frontend/extending/websocket-api/)
and [permission](https://contributors.home-assistant.io/core/internals/permissions/)
guidance were consulted, together with installed HA 2026.10.2 command schemas,
authenticated connections, native subscription cleanup and backpressure behavior.
Prepared Python **3.14.8**, HA **2026.10.2**, Ruff **0.17.1** and mypy **2.4.0** were
reused without onboarding, dependency reinstallation or production access.

## Delivered behavior

Eight namespaced commands provide cached bootstrap, retained schedule navigation,
current live projections, native push subscriptions, paged driver/scoring details,
on-demand history and on-demand analytics. API v1, normalized TypeScript model
projections, all command/response/page/record schemas, errors and Phase 5B usage
are documented in [DASHBOARD_API.md](DASHBOARD_API.md).

Every command requires an authenticated active administrator, a loaded NASCAR
entry and monitored series. This deliberately excludes non-administrators and
entity-restricted users: HA supplies no general config-entry read ACL authorizing
full race datasets. Permissions are checked before delivery and subscription
emissions. Native HA owns authentication, sockets, outgoing queues, slow-reader
disconnection and unsubscribe. The integration owns bounded per-entry/client
listeners and request resources, without global selected-series/subscriber state.

Bootstrap reads cached data and explicitly reports missing reference/time data.
Upcoming previews have at most two races per series and four sessions per race;
unknown race instants remain null, upcoming order uses earliest known future
activity, and canceled sessions cannot create an upcoming instant. Dedicated
schedule pages retain all supported sessions independently of live health.
Live timing uses existing matching fresh LiveViews and normalized models, retaining
nullable fields, exact string IDs and source namespaces. Full ordered leaderboards
remain outside entity state. Embedded/scoring previews explicitly identify their
completeness and supply paged detail commands. CF's unsupported standalone scoring
feeds remain unavailable and are never requested.

History/analytics call only the existing entry runtime APIs. Explicit allowlists
serialize normalized fields. Large collections become ordered parent-identified
record pages with byte/record limits and semantic snapshot continuation checks.
No formulas move to transport. Calculations and large page serialization/digests
run in HA's executor. Cancelled serializers keep their request slot until the
bounded worker drains. There is no completed-result cache, historical prefetch,
new persistence or extra polling loop. Stop callbacks remain removable after
firing, including when HA subsequently unloads the entry.

## Executed checks

| Check | Actual result |
| --- | --- |
| Final full `pytest -q` | **977 passed in 53.38 seconds**; inherited 915 plus 62 new cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |
| `mypy custom_components/nascar_race_center` | Passed; 43 integration source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid integrations |
| Independent prepared HA runtime smoke | 1 passed; authenticated REST/state/service checks, separate from NASCAR behavior |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| GitHub Actions | Hosted run/check results and links are tracked in the Phase 5A PR after push; no unexecuted hosted check is claimed here |
| HACS | Existing private-repository conditional skip and brands exception retained; no full HACS approval |
| NASCAR network access | Zero; tests use synthetic normalized observations or intercepted structural responses |
| Production HA OS / physical devices / visual dashboard | Not exercised; outside Phase 5A |

Hassfest ran official tag **2026.10.2**, commit
`8d7fd8b68677c2585be36ec86043308f403875b8`, under ignored
`work/home-assistant-core`. Git/public-source retrieval, local test-server sockets
and Hassfest multiprocessing used the supported network-enabled execution mode
with inherited proxy/TLS unchanged. Initial restricted-shell attempts could not
reach the proxy or bind local multiprocessing sockets; those interrupted attempts
are not reported as passing checks. No denied destination was bypassed.

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

## Actual HA WebSocket and regression findings

- Successful authenticated bootstrap/schedule/live/history/analytics/detail reads
  use the real HA WebSocket server. Unauthorized pre-auth messages, invalid tokens,
  read-only users, revoked admins, foreign/missing entries, unmonitored series,
  invalid versions/extra fields, Boolean/string IDs, duplicate/oversized selections
  and analytics complexity violations fail without unauthorized service access.
- Full leaderboards preserve order, favorite identity, leading-zero car numbers,
  nullable timing, derived position difference and embedded observations across
  practice, qualifying and race routing. Other series never inherit the global
  feed's field. Missing/unavailable/unsupported scoring remains explicit.
- Multiple actual clients receive initial revision 1. Unchanged observations emit
  no event. A burst of 100 local changes coalesces to its newest lap. Race/run and
  series transitions replace the snapshot with complete identity/health context.
  Existing source-expiry notifications deliver stale transitions without network
  calls, followed by offline/recovery states. Unsubscribe/disconnect remove the
  client's listeners and pending callbacks without disturbing peers.
- Four subscriptions per connection and the entry-wide subscription bound are
  enforced. Thirty commands per user/entry over ten seconds are shared across
  tabs; the next request is rejected and the window recovers. Two simultaneous
  user requests are enforced across tabs. Cancelling a serialization worker keeps
  that slot until its work drains, preventing cancellation-driven worker growth.
- Concurrent history and analytics clients share one existing history provider
  request. Disconnecting one retains the other's result. Entry unload/reload and
  actual HA stop drain blocked requests and release subscriptions/resources.
  Native socket shutdown may precede delivery of a terminal entry-unavailable
  event. No test disables integration timer/task cleanup assertions.
- Rejected-auth and actual-stop cases disable only aiohttp's native heartbeat in
  the test harness: HA's accelerated shutdown clock otherwise leaves an upstream
  WebSocketResponse heartbeat timer. All successful ordinary transport cases use
  native heartbeat behavior. Authentication, real sockets, HA dispatch and
  integration subscription/request cleanup remain exercised in every case.
- All seven historical dataset serializers preserve observations, parent identity,
  null versus empty, run namespaces, candidate sentinels and source provenance.
  Concatenated one-record pages equal the complete small synthetic stream.
  Oversized records, invalid offsets, absent continuation tokens and changed
  snapshots fail explicitly. Large streams provide complete continuation metadata.
- Analytics retains contract version, samples, coverage, gaps, recorded/derived
  metric definitions, reported performance, stage namespaces and finite JSON.
  Invalid time values retain analytics exclusions. No raw provider dictionary can
  pass the registered-model serializer.
- Two CF dashboard clients opening bootstrap and live subscriptions keep the
  existing **seven GET** startup count unchanged. No per-tab, per-driver, per-series
  refresh is introduced, including local stale notifications.
- Twenty dashboard reads (bootstrap/live/history/analytics) plus a live subscription
  add **zero actual Recorder state rows**. Entity registry IDs remain unchanged.
  The complete inherited suite retains prior event baseline/replay/durable
  deduplication/persistence-before-publication and adaptive provider-cadence,
  caching, Retry-After, startup, selected-series and Recorder protections.

## Synthetic measurements

Reproduce with `pytest -q -s tests/test_dashboard_performance.py`. Three untraced
page runs followed by a separate `tracemalloc` run use preconstructed immutable
normalized inputs. Allocations below cover page projection/hashing/output only;
they exclude source models, analytics calculations, HTTP/JSON decoding, HA,
network/TCP queues and whole-process memory. Source/model/computation bounds are
unchanged from Phase 4A/4B. Pages retain only the returned rows while scanning
all records for a stable digest; later pages repeat this bounded linear scan.

| Scenario | Full stream records / returned | Three elapsed seconds | Page JSON bytes | Retained / peak traced bytes |
| --- | --- | --- | --- | --- |
| 10 drivers × 5,000 historical laps | 50,010 / 200 | 0.4302 / 0.4283 / 0.6073 | 32,108 | 129,014 / 131,121 |
| Eight selected drivers, 1,250 laps, six windows: 60,000 projected windows | 79,316 / 200 | 1.5024 / 1.8149 / 1.0395 | 55,150 | 264,306 / 299,302 |

These page times include hashing the entire synthetic record stream. They are not
network request latency or a production service-level promise. A maximum accepted
analytics page is deliberately chunked even though the internal analytics result
can contain tens of thousands of samples/windows. A separate oversized-text case
verifies byte-driven page shortening below 200 rows without silent loss.

A **100-driver** synthetic live projection measured **70,669 bytes**. Five actual
local WebSocket update deliveries took **0.10467 / 0.10455 / 0.10479 / 0.10473 /
0.10507 seconds**, including the configured **0.100-second coalescing delay**.
This is local synthetic delivery behavior only. It establishes no NASCAR source
freshness, CDN behavior, real-race latency or permitted polling cadence.

There are at most 64 entry subscriptions, one pending callback and one previous
projection fingerprint per subscription; fingerprints are bounded by the payload
cap. Admission retains at most 128 user windows of 30 timestamps. At most eight
entry dashboard requests/two per user retain returned service models or draining
workers concurrently. Existing history/analytics/cache limits apply additionally.
There is no private WebSocket queue access or added unbounded application queue.

## Remaining evidence and delivery boundaries

V1 administrator-only access is an intentional product limitation documented for
Phase 5B. It supplies no delegated full-data permission or favorite-edit command.
Explicit historical keys remain evidence-limited selections, not discovered
coverage. Ambiguous source times, unverified timing units/sentinels, incomplete
identity, source failures and provisional scoring retain their existing meanings.
No official results, pit counts, stage completion, championship standings, rating
formula, video/media rights or unknown historical schedule is inferred.

NASCAR data-use/polling/retention/redistribution rights, current anonymous access,
active-session validation, broad historical coverage, permitted faster CF cadence,
HACS brands/publication and production HA OS acceptance remain open gates.
The MIT license remains code-only. No merge, deployment, release, publication,
visibility change, CF permission/cadence change or Phase 5B/5C visual implementation
is part of this change.
