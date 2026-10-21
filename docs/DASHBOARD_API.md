# Dashboard data API v1 (Phase 5A)

Phase 5B consumes this contract through Home Assistant's authenticated
`/api/websocket`. No card, frontend bundle, resource registration, custom server,
NASCAR polling loop or entity is installed by Phase 5A. The integration registers
commands with HA's supported `websocket_command` / `async_register_command`
extension and uses native result, event, unsubscribe and disconnect handling.

Reviewed against the installed **HA 2026.10.2** implementation and current official
[WebSocket extension documentation](https://contributors.home-assistant.io/frontend/extending/websocket-api/)
and [permissions documentation](https://contributors.home-assistant.io/core/internals/permissions/).
The native transport uses `probatio` schemas in this HA version.

## Authentication and scope

HA validates the access token before dispatch. **Every v1 command requires an
active administrator**, including subscriptions and continuation requests.
Non-administrators (including read-only and entity-restricted users) receive
`unauthorized`; entity visibility does not grant access to full race datasets or
entry-wide favorites. HA has no general config-entry read ACL that can authorize
these datasets. V1 deliberately supplies no partial entity-based delegation.
Phase 5B must show this access requirement; broader access needs a separately
reviewed authorization contract.

Each request explicitly supplies the loaded NASCAR `entry_id`. Foreign-domain,
missing and unloaded entries fail closed. Series must be monitored by that entry.
Configuration and favorites are read-only. Permissions are checked again before
asynchronous results and every subscription emission. A revoked subscription
terminates on its next notification. Previously delivered data cannot be revoked.
All subscription state, request work and request-window accounting belong to the
entry and authenticated connection/user, never a global current-series selection.

## Common wire schemas

All commands start with `nascar_race_center/dashboard/`. Every message has HA's
increasing positive integer `id`, the command `type`, `entry_id` (1–128 characters)
and **required integer `api_version: 1`**. Extra fields are rejected. Boolean,
string-coerced, duplicate, oversized and out-of-range numeric selections fail
before service access. Unsupported API versions fail validation.

Successful reads use HA's result wrapper:

```json
{"id":1,"type":"result","success":true,"result":{"api_version":1,"entry_id":"EXAMPLE","data":{}}}
```

Successful subscription registration acknowledges `result: null`; snapshots then
arrive as HA events with the same subscription `id`, with the same version/entry
 envelope in `event`. Errors use HA's `{id,type:"result",success:false,error:
{code,message}}` envelope. Messages contain fixed safe reasons, never upstream
bodies, credentials, headers, tokens, Store records or exception strings.

**Identifier convention:** race, run, session, NASCAR driver, team, track and other
`*_id` values in responses are lossless **strings or null**; `series_id` and
`season` are integers. Identifier arrays use strings. Request race/driver IDs are
strict JSON integers within the bounds below. Car numbers are strings preserving
leading zeroes. Run namespaces remain separate. Do not join by name, car number,
directory ID, equal run numbers or array position.

Known source instants are ISO 8601 strings with explicit offsets. Historical
`*_reported`, `run_date` and `run_date_utc` values are original source labels;
they are **not certified instants**. Missing/ambiguous timing stays null. No track
zone, end time, race duration or season is guessed. Optional fields are present
with null when unknown; empty arrays denote reported empty collections. Numeric
output is finite JSON only. Nonfinite optional numerical values serialize as null;
analytics also retains its exclusion/unavailable reason.

The exact normalized leaf-object field names, nullability, enum choices and
TypeScript types are in [DASHBOARD_API_MODELS.d.ts](DASHBOARD_API_MODELS.d.ts).
These declarations document selected projections, not an additional runtime or
frontend package. `dashboard_schema.py` explicitly allowlists each exported field;
new provider/model attributes never become public automatically.

## Command catalog and request bounds

Common fields above are required on every row. `series_id` is an exact integer
1/2/3 selected by the entry. History/analytics `season` is 1948–9999 and `race_id`
is 1–10^10. These defensive bounds do not establish endpoint coverage.

| Suffix | Additional parameters | `data` result |
| --- | --- | --- |
| `bootstrap` | none | Bootstrap schema below; cached reads only |
| `schedule` | `series_id`; optional `season`, `race_id`; page parameters | Retained schedule page: race and session records |
| `live` | `series_id` | Current live projection below |
| `subscribe_live` | `series_id` | Initial and changed live projections, with subscription-local revision |
| `live_driver` | `series_id`, `driver_id` (1–10^20), `collection`: `pit_stops` or `laps_led`; page parameters | Explicit live driver detail page |
| `live_scoring` | `series_id`, `collection`: `pits`, `stages` or `points`; page parameters | Supported associated scoring detail page |
| `history` | `series_id`, `season`, `race_id`, nonempty distinct `datasets` (1–7); page parameters | Historical page with independent dataset metadata |
| `analytics` | History parameters plus distinct `driver_ids` (1–8, IDs 1–10^10), explicit `first_lap`, `last_lap`, `windows`, `time_basis`; page parameters | Analytics v1 metadata and paged observations |

History dataset literals are `weekend`, `laps`, `notes`, `loop`, `averages`, `pits`,
`stages`. Analytics lap numbers are 0–10^10, an inclusive non-reversed span of at
most 5,000 numbers. Windows are distinct members of `[5,10,15,20,25,30]` (empty is
supported). `drivers * lap_span * window_count <= 60000`. `time_basis` is exactly
`all_available` or `overlapping_valid_laps`. No formula is implemented in the
transport: it calls `runtime_data.analytics.async_get` and retains contract v1,
metric method/unit/classification/reason, sample counts, gaps and provenance.

### Bootstrap data schema

| Field | Type and meaning |
| --- | --- |
| `series_ids`, `favorite_driver_ids` | Selected integer series and string NASCAR IDs |
| `references` | `drivers_status`, `tracks_status`: available/stale/unavailable; `unresolved_favorites`: driver ID/reason rows; compact selected-favorite `drivers` and relevant cached `tracks` |
| `references.drivers[]` | `{driver_id,name,associations}`; at most one metadata projection per selected series; ambiguous/missing associations have explicit reasons |
| `navigation[]` | `{series_id,seasons,race_count,unknown_start_count,failed_seasons}` for usable cached schedules |
| `upcoming`, `upcoming_complete` | At most two future race summaries per series, each with up to four `sessions` and `sessions_complete`; explicit incompleteness directs clients to schedule pages |
| `next_activity`, `next_activity_reason` | `{start_time,race,session}` or null with `no_known_future_instant`; session may be null for a known race start without session enrichment |
| `supported_sessions` | practice, qualifying, race |
| `capabilities` | History dataset literals, analytics contract version 1, administrator access requirement and live push support |
| `provider` | Configured demo/CF source label only |
| `source_state[]` | `{series_id,live,schedule}` independent health values |
| `limitations` | Stable reason labels, including unverified semantics, source units and standalone scoring association |

A race summary contains series/season/race identity, name, known start, track
name/ID, reported status, `sessions_failed`, `session_count`, `time_availability`.
Only fresh usable references are included. The driver directory is not a roster.
Bootstrap does not refresh any coordinator or prefetch history/analytics. Unknown
schedule start times remain navigable through `schedule`, not falsely upcoming.

### Schedule page schema

Headers: `series_id`, `seasons`, `availability`, `failed_seasons`, `catalog_scope:
"retained_supported_schedules"`, `updated_at`. Records are `{kind:"race",value:
RaceSummary}` and `{kind:"session",race_id,season,value:Session}` in cached source
order. A page can begin inside a race's session list; parent IDs always accompany
session rows. Calendar/session IDs are distinct from live timing run IDs.

This is a bounded retained-season catalog, not an invented historical catalog.
An absent selection yields zero rows. Failed retained seasons do not become
available through successful peers. Schedule reads remain independent of live
outages. Explicit valid history keys need not occur in the retained catalog.

### Live data schema

| Field | Type and meaning |
| --- | --- |
| `identity` | `{series_id,season,race_id,run_id,season_basis}`; season comes only from a unique cached schedule match, labeled `cached_schedule`, otherwise null/`not_reported` |
| `availability` | `ok`, `stale`, `freshness_unknown`, `offline`, `denied`, `not_reported`, `no_active_session` |
| `source_updated_at`, `stale` | Content clock or null, independently determined stale Boolean or null |
| `session` | null when unavailable; otherwise reported run_name/status(kind)/run_type_code, flag/flag_state_code, lap, total_laps, laps_remaining, elapsed_seconds, leaderboard_failed, stage_failed, stage and evidence-limited `progress` |
| `leader_driver_id` | Unique reported position-one NASCAR ID or null |
| `leaderboard` | Full ordered reported field of LiveReportedDriver projections, or null |
| `reported_count`, `omitted_count` | Source/normalizer counts, not an assertion of a complete official entry list |
| `scoring` | Independent pits/stages/points `{status,provenance,classification,records,total,complete,detail_command}` |
| `limitations` | Same supported source-boundary labels as bootstrap |

Each driver adds `favorite`, `running_status`, derived `position_change:
{value,classification:"derived",method:"starting_position_minus_position"}`,
and `pit_stops` / `laps_led` previews. These previews contain `records` (first two
observations or null), `total` (or null), `complete` and `detail_command`.
Use paged `live_driver` for every observation when `complete` is false. Laps-led
intervals retain source boundaries; no interval summation or pit total is inferred.
`gap` and timing/speed fields retain their original scale with unverified units.
Scoring previews similarly expose at most two groups; use `live_scoring` for all
associated groups. A detail page includes identity, collection and availability;
driver detail also has driver_id/reason; scoring detail retains provenance.

Only `LiveView`'s fresh, successful matching series can supply current timing.
Failed/stale observations retain identity and content-clock context but return
null current session/leaderboard. A global observation for series 2 never supplies
series 1 timing. CF's standalone scoring polling kinds remain empty: no new
pit/stage/points requests or unsupported associations are introduced. Supported
synthetic providers can expose independently associated provisional facts.
`completed` progress from a checkered observation is not official final results.

## Pagination, immutable selection and provenance

All paged commands accept `offset` (0–1,000,000; default 0), `limit` (1–200;
default 100) and optional `snapshot` (64 lowercase hex characters). A nonzero
offset **requires** the previous snapshot. Every page contains:

```typescript
interface Pagination {
  offset: number; limit: number; returned: number; total: number;
  next_offset: number | null; snapshot: string; complete: boolean;
}
```

`records` is a flat ordered stream of explicit row projections. Large nested
collections are split at row boundaries and preserve parent IDs, namespace and
source indexes as applicable. Nothing silently disappears. `total` counts stream
records (including header/driver/group rows), not lap rows only. `complete` means
the stream is exhausted **from this offset**; source coverage/status remains
independent. `next_offset: null` ends pagination. The byte budget can return fewer
than `limit` records. Even one oversized record fails explicitly.

For **history and analytics**, the first request reserves a bounded snapshot slot,
fetches only the explicitly selected datasets through the existing services, then
projects and hashes the entire normalized stream once in HA's executor. It stores
an index of serialized allowlisted rows, never raw provider bodies or source models.
The opaque 64-hex token identifies this immutable content version and is bound to
the entry runtime, authenticated user, originating WebSocket connection, command,
race key, ordered dataset selection and every analytics option. It grants no access
by itself: normal authentication/administrator/entry checks apply on every page.
Only `offset` and `limit` may change. A token with offset zero rereads that snapshot;
an offset-zero request without a token starts a new snapshot.

Continuation reads only indexed rows: **zero history calls, network GETs, analytics
recalculations or full-stream projection/hash passes**. Ordinary two-document HTTP
cache eviction and the 60-second floor cannot alter an admitted snapshot. Source
changes do not modify already issued snapshots; a new selection sees whatever the
existing HTTP freshness/cache/floor rules permit. Partial/unavailable source states
remain explicit and pinned too; snapshot completion does not assert source coverage.

Snapshots expire **300 seconds after construction**, without sliding renewal, and
are invalidated on disconnect, unload, reload or shutdown. Any active page worker
keeps its slot reserved until it drains, including after expiry/disconnect. Completed snapshots remain
replayable within that lifetime. Tokens cannot move between connections, users or
entries. Expired/released/modified/wrong-selection tokens return `snapshot_invalid`
(or `snapshot_expired` if expiry is detected before its cleanup callback); restart
without a token. Reopening a selection may still encounter the existing request
floor. There is no resumability across disconnect/restart. Use pages of 200 for
large selections and pace commands within 30 per 10 seconds; smaller pages or long
pauses can outlast the five-minute lifecycle.

There are four slots **shared across all entries/users**, including reserved slots
under construction, and at most two per user across tabs and entries. Each slot
allows 24 MiB of accounted serialized/index memory and 100,000 rows: at most 96 MiB
reserved in total, in addition to existing bounded source/service/HA resources.
The accounting includes bytes-object overhead, conservative index pointers and
metadata allowance; construction retains its reservation through cancellation drain.
No slot is evicted to admit another client. `snapshot_limit` fails before retrieval.
`snapshot_too_large`, `record_too_large` or `response_too_large` fails before any token
if the full selection cannot be indexed or any later record cannot fit a page.
All seven datasets remain selectable. There is no new endpoint or disk archive.

Schedule and live-detail commands retain their lightweight stateless content digest:
changed source/context returns `snapshot_changed`; discard assembled pages and
restart. Their tokens do not reserve history/analytics slots.

History headers: `race`, aggregate `status`, `datasets[]`, `records`, `pagination`.
Each dataset entry preserves status, fixed reason, classification and complete
`HistoryProvenance`: dataset, requested key, validation, coverage, delivery,
retrieved_at, response_at, http_status and retry_after. Status distinctions are
`available`, `empty`, `partial`, `not_yet_published`, `unsupported_unverified`,
`network_access_failure`, `invalid_schema_identity`. These are source/service
outcomes in a successful HA result, not transport errors.

| History record kind | Value / context |
| --- | --- |
| `weekend` | HistoricalWeekendHeader; `collections` has explicit presence Booleans for nullable results/sessions/leaders/cautions/stages/schedule |
| `result` | HistoricalResult |
| `session` | HistoricalSessionHeader; `results_available` distinguishes null from empty results |
| `session_result` | HistoricalResult with parent `weekend_run_id` |
| `leaders`, `cautions`, `schedule` | HistoricalLeader, HistoricalCaution, WeekendScheduleItem |
| `weekend_stage`, `stage` | Stage group header/number/result_count; archived stage also retains full context |
| `weekend_stage_result`, `stage_result` | StageResult plus parent number and archived context where applicable |
| `lap_driver` | DriverLapsHeader plus `lap_count` |
| `lap` | HistoricalLap plus NASCAR `driver_id` and original `source_index` |
| `flags`, `notes`, `pits` | HistoricalFlag, HistoricalNote, HistoricalPit |
| `loop`, `average` | Loop header or average title/source_index/driver_count |
| `loop_driver`, `average_driver` | HistoricalLoopDriver or HistoricalAverageDriver plus parent source_index |

Every history record also contains its `dataset`. Commentary IDs retain their
unverified namespace; archived pits retain null NASCAR driver identity. Reported
candidate-sentinel numbers and interpretation labels survive serialization.

Analytics headers preserve `contract_version`, `query`, `status`, `reason`,
`evidence`, `race_metrics`, `caveats`, `race_timing_run_id`. Records are:

| Analytics kind | Value / context |
| --- | --- |
| `driver` | AnalyticsDriverSummary + driver_id |
| `samples`, `gaps`, `consecutive_runs` | LapSample, LapGap, ConsecutiveRun + driver_id |
| `window_summary` | driver_id, size, best_mean Metric |
| `window` | RollingWindow + driver_id/size |
| `position_summary` | AnalyticsPositionSummary + driver_id |
| `position_points`, `position_gaps` | PositionPoint or LapGap + driver_id |
| `comparison` | DriverComparison (both NASCAR IDs, sample counts, metric definitions) |
| `performance` | AnalyticsPerformanceSummary + driver_id |
| `performance_stages`, `performance_reported_metrics`, `performance_sessions` | StageObservation, ReportedMetricGroup, SessionPerformance + driver_id |

Metric definitions and exact formulas remain in [ANALYTICS.md](ANALYTICS.md).
The API never computes statistics on the event loop or invents new formulas.
Source availability, selection gaps, recorded/derived distinctions and invalid
numeric exclusion reasons must remain visible in Phase 5B.

## Subscription and lifecycle contract

Use `hass.connection.subscribeMessage(callback, request)` and retain its returned
unsubscribe function. The initial current snapshot is event revision 1. Revisions
increase only for emitted meaningful projections and are local to this
subscription. Cached reconnects start a fresh revision sequence. Never compare
revisions across subscriptions or reuse an old entry/series selection.

Existing live, scoring and schedule coordinators notify the subscriber. The live
coordinator's existing local content-expiry timer supplies stale transitions
without a NASCAR request. A single 100 ms pending callback per subscriber
coalesces bursts to the newest snapshot; intermediate samples may be skipped.
This is a current-state stream, not an event ledger or lap archive. Duplicate
projections (including unchanged observations with newer transport retrieval
times) generate no event. Changing source content timestamps is observable.
Race/run/series identity and source health are included in every full projection.

HA's `unsubscribe_events` and connection close remove listeners/timers and cancel
only that connection's on-demand consumers. Entry reload/unload/stop closes every
entry subscriber and cancels/drains its work. An entry-unavailable terminal event
can arrive on reload/unload; shutdown may close the native socket first. Resubscribe
after a loaded entry/reconnection. Requests recheck current authorization before
publication. Shared HistoryService/AnalyticsService work survives another
client's cancellation. A cancelled pure serialization worker keeps its request
slot until drained; late results are discarded.

## Resource limits and errors

| Resource | Bound |
| --- | --- |
| Response result/event envelope | 256 KiB JSON plus small native HA wrapper |
| Page | 1–200 records, further reduced to fit bytes |
| History/analytics snapshots | 4 globally / 2 per user across entries; 24 MiB and 100,000 rows each; fixed 300 seconds; construction included |
| Bootstrap | At most two future races per selected series and four sessions per race; selected favorites only; at most three association projections per favorite |
| Live leaderboard | Existing maximum 100 competitors; two embedded/scoring preview records per collection, explicit detail pagination |
| Subscriptions | 4 per connection, 64 per entry |
| On-demand dashboard work | 2 per authenticated user across tabs; 8 per entry, including cancellation drain |
| Request window | 30 admitted commands per user/entry per 10 seconds; 128 retained user windows |
| Push scheduling | One replaceable callback per subscriber; 100 ms coalescing |
| Slow readers | HA native queue/backpressure/disconnect behavior; no integration-managed message queue |

HA 2026.10.2's native queue peaks at 1,024 pending messages for 10 seconds and
closes at 4,096 pending messages. These are HA-wide transport safeguards, not a
claim that this integration allocates or fills those queues. No private queue
inspection or custom socket management is used. Existing history eight-flight,
two-document cache, response/retention/request-floor/Retry-After limits and
analytics two-computation/driver/lap/window limits remain authoritative. See
[HISTORY.md](HISTORY.md), [POLLING.md](POLLING.md) and the validation report.

Transport codes: native `invalid_format`, `unknown_command`, `unauthorized`;
`entry_unavailable`, `invalid_selection`, `request_limit`, `subscription_limit`,
`rate_limited`, `snapshot_required`, `snapshot_changed`, `snapshot_invalid`,
`snapshot_expired`, `snapshot_limit`, `snapshot_too_large`, `invalid_offset`,
`record_too_large`, `response_too_large`. Correct malformed selections; restart
changed snapshots; reduce record/selection size where possible; release unused
subscriptions; retry request-window exhaustion after 10 seconds. History/scoring
failure statuses remain independent and retain their provenance/retry hints.
Opening dashboards or subscribing never requests refresh, bypasses cooldown,
changes CF cadence or adds Recorder attributes/rows.

## Synthetic Phase 5B examples

These invented identities and numbers are documentation, not NASCAR captures.
The frontend obtains the loaded entry ID through HA's authenticated configuration
UI/context; do not hardcode an installation's entry ID.

```javascript
const common = { entry_id: selectedEntryId, api_version: 1 };
const bootstrap = await hass.callWS({
  type: "nascar_race_center/dashboard/bootstrap", ...common,
});
const unsubscribe = await hass.connection.subscribeMessage(onLive, {
  type: "nascar_race_center/dashboard/subscribe_live", ...common, series_id: 1,
});
// Dispose on navigation/disconnect/component removal.
unsubscribe();
```

```json
{"id":2,"type":"nascar_race_center/dashboard/history","entry_id":"EXAMPLE","api_version":1,"series_id":1,"season":2024,"race_id":88001,"datasets":["laps"],"limit":100,"offset":0}
```

A representative lap record is
`{"dataset":"laps","kind":"lap","driver_id":"99002","source_index":0,
"value":{"lap":1,"lap_time":31.25,"lap_speed":null,"running_position":2}}`.
The page includes independent dataset provenance and pagination. Continue using
its exact snapshot and next_offset, retaining the same race/dataset selection.

```json
{"id":3,"type":"nascar_race_center/dashboard/analytics","entry_id":"EXAMPLE","api_version":1,"series_id":1,"season":2024,"race_id":88001,"datasets":["laps","weekend","stages","loop","averages"],"driver_ids":[99002,99003],"first_lap":1,"last_lap":200,"windows":[5,10],"time_basis":"overlapping_valid_laps","limit":100}
```

A representative derived Metric is
`{"name":"mean","value":14.0,"method":"arithmetic_mean","unit":
"source_lap_time_unit_unverified","classification":"derived","reason":null}`;
consult actual metric definitions rather than assigning seconds/green-flag pace.

Phase 5B should wrap these commands in a typed data module, render explicit
loading/empty/partial/stale/denied states, preserve unknowns, bound assembled page
retention, discard outdated selections and dispose subscriptions. It should
subscribe once for the selected live series and use on-demand paged history;
it should not poll the backend to detect live changes. Reconnect/reload reboots
from bootstrap. No visual layout, media access or frontend packaging decision is
part of this contract. Data-use, official finality, real source latency, coverage,
units and standalone scoring evidence limits remain open.
