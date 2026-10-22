# CF session readiness: integration 0.1.2 / card 0.5.3

This change starts from merged PR #15, main commit
`68e917eab183a405a1f662ba49a71eb23dcc4fed`. Its snapshot ownership, release,
pagination and empty-state fixes are preserved. This is a separate review
candidate, with no release, deployment or owner configuration change.

## Existing pipeline and evidence

The production path already worked with supported structural inputs:
`endpoints.LIVE_FEED` → `NascarApiClient` (HA shared aiohttp session) →
`CFProvider._read` → `models.parse_live` / `timing.parse_leaderboard` → one
`LiveCoordinator` → per-series/favorite sensors and `LiveView` →
`dashboard_views.live` → authenticated native HA WebSocket → existing card / timing
tower. No fixture is a production fallback. History/analytics use their existing
independent on-demand services and immutable selection snapshots.

Already supported: 100 bounded vehicles, ordered positions and NASCAR driver-ID
lookup; names, car numbers (including leading zeroes), starting position and
derived position change, reported gap, laps completed, last/best times and speeds,
average speed, raw running-status code, conservative status interpretation,
laps-led intervals, embedded pit observations and favorites. Empty `vehicles: []`
was already valid; malformed/duplicate identities reject the optional board,
missing identities are omitted and counted, and core context remains separate.
A global series-2 feed never becomes series-1 or series-3 timing.

Evidence reviewed:

| Reference | What it establishes and what it does not |
| --- | --- |
| Repository's imported [observed package](nascar-api-reference/START_HERE.md), October 21, 2026 | Its request evidence records an anonymous HTTP 200 at `2026-10-21T11:04:40.840243+00:00`, 94,832 bytes, SHA-256 `645351f54c19d52a54656cbedc6126ecb9876b3663a2c374f1806aa005e4ed1c`: Cup series 1, race 5633, timing run 8, run type 3, flag 9, 37 vehicles, lap 312 / zero remaining. Redacted structural samples corroborate the vehicle shape and identifiers, **not active practice/qualifying/racing today**. No original feed body was copied into tests. |
| [ooohfascinating/NascarApi](https://github.com/ooohfascinating/NascarApi/tree/1640846fddd82f39dd9bfa35433aa6f34ec70051), pinned `1640846fddd82f39dd9bfa35433aa6f34ec70051` | `LiveFeed.MD` describes `run_type` 1 practice / 2 qualifying / 3 race; nested NASCAR driver IDs and vehicle metrics. `FlagState.MD`: 0 none, 1 green, 2 yellow, 3 red, 4 white, 5 checkered, 8 hot, 9 cold; 6/7 unknown. These are community meanings, not an independently confirmed active-session contract. Its practice example uses race-lap/stage sentinel 999. Claims of second-by-second source updates grant no client polling permission. |
| [api-evangelist/nascar](https://github.com/api-evangelist/nascar/tree/16e5462d347cdbe5e0fec2a3572b222bff145ccb), pinned `16e5462d347cdbe5e0fec2a3572b222bff145ccb` | Generated Swagger/OpenAPI reference points at **feed.nascar.com**, `/api/LiveFeed` / `/api/LiveQualifying`, with generic resource schemas. Its authored schemas explicitly identify themselves as derived. This is a different host/API, no proof of CF compatibility and no reason to request those hosts. |
| [Earlier endpoint audit](api/AUDIT_REPORT.md) | Earlier cloud attempts stopped at proxy CONNECT; that is not a NASCAR origin 403. For this change, policy still excludes CF and access permission is unconfirmed: **zero NASCAR requests made**. GitHub reference repositories were read through the normal permitted route. |

Identifier and semantic boundaries remain: NASCAR driver ID is identity, never
name/car/team; race ID and timing run ID are separate. Archived stage/loop run
namespaces cannot be substituted. Observed global stages identify a different
race/run; global points have zero identities; global pits lack a supported
race/driver join. They remain `unsupported_association`, unrequested and
unavailable. Embedded vehicle pits retain their own NASCAR identity. A source
clock requires an explicit offset (including the observed fractional-second
shape); numeric time-of-day is not a substitute. Naive schedule `*_utc` strings
remain unknown until timezone semantics have evidence.

## Corrections and current behavior

1. CF compares consecutive normalized observations within a full series/race/run
   key. Diagnostics distinguish first observation, source clock unchanged,
   timestamp/metadata only, changed observations and no session. A local cache read
   preserves the prior assessment; downloading/revalidating unchanged content is
   not a new racing observation. State is bounded to the existing previous model,
   one context tuple and a short outcome, with no timeline, payload or extra cache.
2. The first usable CF observation supplies **reported**, activity-unconfirmed
   timing. Supported activity plus a progressing source clock and changed lap,
   flag, driver field or stage observation establishes active progress on a later
   read. Name, car, run-name and elapsed-clock edits are excluded. A changed run type
   requires a new first observation even with reused run IDs. Source replay or
   misleading provider activity fields still require owner cross-checking.
3. Cold track and repeated unchanged/timestamp-only content withhold current
   timing and say **latest recorded**. Valid zero vehicles says **no active
   session**, without parser failure. Missing run/type, stale/unknown/regressed
   time, failed transport and rejected boards cannot establish active timing.
   A fresh checkered observation says **completed**, not official/final results;
   later unchanged completion stays completed while timing is withheld. Unknown
   flag codes remain numeric and cannot establish CF active progress.
4. Practice/qualifying use reported on-track evidence instead of requiring a
   positive race lap. Their race total/remaining laps and embedded stage are
   withheld, avoiding sentinel/race-scoring semantics. Driver timing remains
   source-reported: qualifying position is not promoted to official starting grid,
   practice position is not a race classification, gaps/units are not invented.
5. A fresh source clock that regresses below the coordinator high-water mark is
   `freshness_unknown`, including across a changed race/run/series. It cannot
   supply current timing. A current advancing clock recovers automatically.
6. The card shows calm distinct source/session badges and race/timing-run context,
   avoids race-lap totals in non-race timing, and refuses live details without a
   matching usable session and positive race/run. No-session and withheld views
   issue no pits/stages/points detail requests. Existing actual source-change
   protection and snapshot lifecycle are unchanged.
7. Diagnostics add a specific timing-unavailable reason, observation advancement,
   available/empty/rejected/withheld board status and next eligible seconds per
   attempted endpoint. Existing attempt/response/JSON/parser/context/count fields
   remain. No raw response, URL query, header, token or driver name is added.

**All nine series × session combinations pass offline through the actual CF
adapter, mocked HTTPS, real HA entities and authenticated WebSocket server.**
Practice and qualifying current-source semantics remain community-supported;
none of the nine combinations has been newly verified against an authorized
active real session in this work. Source currency is a conservative local
assessment, not confirmation from NASCAR's published results.

## Polling and resource decisions

No second polling loop, per-driver/per-card request or endpoint was added.
`CF_LIMITS` remains non-adaptive with minimum **300 seconds**; selecting Adaptive
cannot enable the synthetic 10-second path. The ordinary 300–3600-second setting
and transport reservation, shared cache, validators/304, Retry-After, cancellation,
reload/restart guard and response limits remain effective. The one cadence fix
lets on-track practice/qualifying use that same conservative minimum at zero
race laps. It never lowers the floor. First reported activity may select this
interval to obtain another observation; it still says activity-unconfirmed.

Exact conservative target order (all selected series share one decision):

| Evidence | CF target before existing constraints |
| --- | --- |
| Usable fresh supported on-track practice/qualifying | Configured conservative minimum, default 300 seconds |
| Usable fresh supported racing flag with positive race lap | Same minimum |
| Otherwise known race start from two hours before through eight hours after | At least 900 seconds |
| Otherwise a known future race within two days | At least 3,600 seconds |
| Otherwise, including no usable timestamped schedules | At least 21,600 seconds |

Cold/empty/withheld/clock-regressed CF content is excluded from the activity
choice. Completed sessions fall back to the race-window/nearby/off-season choice.
Between sessions CF keeps this conservative race-based discovery; it does **not**
activate adaptive five-minute gap/30–60-second approach discovery. All-unknown
schedule times can therefore mean a six-hour discovery wait, even near a weekend.
This remains a real limitation, not evidence of an empty racing calendar.
Existing stale-clock and failure exponential backoff can lengthen intervals;
server freshness, request-floor reservations and host/path cooldowns win.
`live.polling` records the exact target, effective interval, constraint and network
eligibility. A source-expiry timer changes local availability without HTTP.

These are engineering budgets, **not NASCAR-approved limits**. Source permission
must cover all selected endpoint classes and their effective cadence; a data-use
checkbox does not establish permission. No faster CF activation is included.
The adaptive synthetic framework's all-series/session, approach, between-session,
completion, idle, clock regression, cache/rate/restart and scheduled HTTP-budget
regressions remain in the complete suite.

Memory, response, concurrency and snapshot safeguards are unchanged: 4 global /
2 per user reserved selections, 300-second selection TTL, 100,000 records /
24 MiB per selection, 96 MiB reserved index budget, 256 KiB response envelopes,
200-record pages, 30 dashboard commands per user/entry per 10 seconds, 2 concurrent
requests per user / 8 per entry, two retained selections per card. These are
component accounting limits, not a process RSS cap. No persistent history format,
configuration version, entity identifier or household service changes.

## Executed validation

All automated source responses are explicitly handmade synthetic contracts.
No live network test or owner hardware test is claimed. Runtime: Python 3.14.8,
HA 2026.10.2, Ruff 0.17.1, mypy 2.4.0, Node 24.19.0, TypeScript 5.9.3,
Playwright 1.56.1.

| Check | Result |
| --- | --- |
| Complete Python suite | **1,038 passed**, 58.22 seconds (1,018 existing + 20 new) |
| Ruff lint / format | PASS |
| Strict mypy | PASS, 44 production files |
| Official Hassfest | PASS: one integration, zero invalid; Core tag 2026.10.2 `8d7fd8b68677c2585be36ec86043308f403875b8` |
| Independent HA runtime smoke / prepared configuration validation | **1 passed**, 0.19 seconds / PASS |
| Frontend ESLint / Prettier / TypeScript | PASS |
| Frontend unit/component suite | **84 passed**, 16.61 seconds |
| Production build and unchanged 180 kB raw / 50 kB gzip budgets | PASS; 155,321 raw / 38,831 gzip bytes |
| Lockfile reinstall and committed build reproduction | PASS: fresh offline lockfile install, production build and byte-for-byte comparison |
| Chromium / Firefox / WebKit | **174 passed**, 6.3 minutes; **58 per engine** (all 171 existing scenarios plus three new engine/scenario combinations) |
| Hosted PR workflows | Required PR workflows; the final PR description records the checked head and results |
| HACS | Private-repository skip and existing brands exception retained; no full HACS approval |

The new real-HA matrix uses complete 40-vehicle structural fields for each of
Cup/series 2/Trucks × practice/qualifying/race, including favorites, metric and
cross-series delivery, source progression, shared-cache reuse and 300-second
request counts. Additional cases cover empty/cold/retained timestamp-only,
unchanged and stale clocks, metadata-only edits, fresh regression, missing run, unknown flag,
transition to a different series/race/run, completion, local expiry and zero-GET
reload reuse. Existing suites cover duplicate/missing drivers, malformed flags,
transport failure/recovery, 429/Retry-After, restart reservations, supported scoring
associations, historical preservation and source-change rejection, disconnect,
shutdown, two cards, pagination and rapid exploration.

The three-engine addition replays the serializer's **synthetic** genuine-shaped
vehicle contract for all nine series/session combinations, conservative badges,
no fabricated empty field and zero withheld live-detail calls. It does not turn
community documentation into current real-response evidence.

One concurrent local run failed two existing timing-sensitive HA checks
(cancelled serializer drain and rapid light-color restoration). Their isolated
recheck passed all three parameterized cases, and the final complete serial run
passed all 1,038 tests. No dashboard drain, blueprint or household-control
implementation was changed to hide those assertions. Timing sensitivity under
competing local workloads remains a test-harness limitation.

The existing beta/household tests exercise native HA services, a separate event
automation, entity registries and reload/cleanup in the development test runtime.
They do not verify the owner's household, full HA OS boot, mobile companion,
physical devices, sustained source latency or long soak.

## Delivery and remaining gates

The integration directory is `custom_components/nascar_race_center/` version
**0.1.2**, and the separate committed module is
`frontend/dist/nascar-race-center-card-0.5.3.js`. Both change for actual backend /
source-status behavior. API remains v1 with additive session/observation fields.
See [artifact SHA-256 manifest](CF_READINESS_ARTIFACTS.sha256) and the
[precise owner update, acceptance and rollback procedure](CF_OWNER_ACCEPTANCE.md).
Historical PR #15 and Phase 6A evidence/manifests retain their original versions.

Shortest safe path: confirm source access/use/cadence scope → install the reviewed
pair with the existing entry preserved → verify Demonstration and household
baseline → switch that entry once to CF with legitimate real driver IDs → inspect
ordinary before/during/after diagnostics and compare to NASCAR's published session
results → return to Demo if any gate fails. That owner-operated test, all-series
active source semantics, allowed rate/storage/redistribution, naive schedule time
semantics, source units/status codes and unsupported standalone scoring joins
remain open. No NASCAR access, owner provider switch, release, public visibility,
HACS packaging change, merge or Phase 6B work was performed here.

| Artifact | SHA-256 |
| --- | --- |
| `frontend/dist/nascar-race-center-card-0.5.3.js` | `63870c73be14d1f97357c8d0c2e10d7eb7853412f0927164181a6f910646fd74` |
| `docs/CF_READINESS_ARTIFACTS.sha256` | `ad86f03ba2e75301208bb1e15d89ed19475b75781809be39e0fa1da0559dd78c` |
