# On-demand historical data contract (Phase 4A)

This is a Python internal API for future Phase 4B analytics and Phase 5 views.
It reports evidence-limited source facts; it implements no analytics, dashboard,
HTTP/WebSocket route, service, history entity, raw archive or season crawler.
CF operation still requires the existing explicit data-use acknowledgement.
No new NASCAR access or polling permission follows from this implementation.

## Consumer interface

```python
from custom_components.nascar_race_center.history_models import (
    HistoricalRaceKey,
    HistoryDataset,
    HistoryStatus,
)

# entry is the loaded, typed NascarConfigEntry; the consumer selects an actual
# race from its navigation context. These IDs are illustrative only.
response = await entry.runtime_data.history.async_get(
    HistoricalRaceKey(season=2024, series_id=1, race_id=5392),
    (HistoryDataset.WEEKEND, HistoryDataset.LAPS),
)
weekend = response.dataset(HistoryDataset.WEEKEND)
if (
    weekend is not None
    and weekend.status == HistoryStatus.AVAILABLE
    and weekend.data is not None
    and weekend.data.weekend is not None
):
    reported_results = weekend.data.weekend.results  # None differs from ()
```

The required race key validates exact integers: seasons 1948–9999, national
series 1/2/3, positive race IDs at most 10^10. Selected series must be monitored
by this entry. These are defensive bounds, not evidence of endpoint coverage.
The caller must explicitly supply a nonempty tuple of distinct `HistoryDataset`
members, at most seven. There is no race-ID discovery by guessing, range scan,
per-driver download, implicit adjacent-race lookup or bulk season request.

`HistoryResponse` contains immutable per-dataset `HistoryResult` objects in
request order. `data` is an immutable `HistoricalData` container for the selected
dataset. Unrelated datasets are kept separate even when fetched together. A
failed optional feed cannot remove valid peers. There is no automatic cross-feed
join, borrowing missing identities or finality inference. Future consumers must
check each result, its requested context and validation before comparing facts.
Caller cancellation is propagated, and use of an unloaded service raises
`RuntimeError`. Invalid selection raises `ValueError` before I/O.

## Endpoints, models and evidence

Only these allowlisted HTTPS paths are available. No query parameters or
redirects are accepted. Media, recap, Drive and legacy alternate URLs are excluded.
The supplied [field profiles](nascar-api-reference/Documentation/field_profiles.json),
[relationships](nascar-api-reference/Documentation/verified_relationships.json)
and [reference introduction](nascar-api-reference/START_HERE.md) establish the
observed shapes. They do not establish universal availability or semantics.

| Dataset | Path after `https://cf.nascar.com` | Implemented fields / model |
| --- | --- | --- |
| `WEEKEND` | `/cacher/{year}/{series}/{race}/weekend-feed.json` | `HistoricalWeekend`: complete requested race key checked against race_id/series_id/race_season; reported name, track ID/name, master race ID, race type code, timing run ID, scheduled/actual laps and distance, original date strings, inspection Boolean; result, session, leader, caution, stage and schedule models |
| `LAPS` | `/cacher/{year}/{series}/{race}/lap-times.json` | `DriverLaps`: NASCARDriverID, Number, FullName, Manufacturer, RunningPos; `HistoricalLap`: Lap/LapTime/LapSpeed/RunningPos; `HistoricalFlag`: LapsCompleted/FlagState |
| `NOTES` | `/cacher/{year}/{series}/{race}/lap-notes.json` | Object-keyed lap notes: numeric-string lap, NoteID, Note, FlagState and original ordered/repeated DriverIDs |
| `LOOP` | `/loopstats/prod/{year}/{series}/{race}.json` | Checked race_id/series_id, race_name, sch_laps/act_laps, NASCAR driver ID and exact reported metric field names |
| `AVERAGES` | `/cacher/{year}/{series}/{race}/lap-averages.json` | Title/Items wrapper; NASCAR driver ID, Number/FullName/Manufacturer/Sponsor; OverAllAvg/Rank, BestLapTime/Rank and Con5/10/15/20/25/30Lap plus respective Rank fields |
| `PITS` | `/cacher/{year}/{series}/{race}/live-pit-data.json` | Existing Phase 3B PitActivity/PitStop, manufacturer, original numeric observations including candidate sentinels; driver ID explicitly absent |
| `STAGES` | `/cacher/{year}/{series}/{race}/live-stage-points.json` | Existing Phase 3B StageClassification/StageResult; checked reported race ID, original stage_run namespace/run ID, stage number, NASCAR driver ID, vehicle number, position and stage points |

`HistoricalResult` retains NASCAR driver ID, name, car/manufacturer, result ID,
results run ID, finishing/starting position, reported laps completed/led,
points/playoff points, finishing-status text, disqualified Boolean, official car
number separately from car/vehicle number, team/owner/crew-chief IDs, team name
and session best lap time/speed when supplied. Ordering stays as reported; no
sorting or computed position change claims official classification.

`HistoricalSession` separates weekend_run_id, timing_run_id and nested
results_run_id. It also retains unknown run_type codes, name and original
local/UTC-labeled date strings. No timezone is inferred from a field suffix.
Race timing run 10, weekend run 5497 / timing run 6, and stage run 10 in the
supplied relationship evidence are different namespaces; integer equality alone
does not establish a general join. Session labels in lap averages are not IDs.

Leader/caution segments retain reported lap boundaries, car number or
beneficiary, text and unknown flag codes. Leader car numbers are not driver IDs.
Weekend stage rows use their observed finishing_position/car_number fields;
archived stage rows use position/vehicle_number. Existing scoring parsers remain
unchanged, with strict historical prevalidation before reuse.

Loop metric names are preserved: start_ps, mid_ps, ps, closing_ps,
closing_laps_diff, best_ps, worst_ps, avg_ps, passes_gf, passing_diff, passed_gf,
quality_passes, fast_laps, top15_laps, lead_laps, laps and rating. `ReportedMetric`
contains the exact field, numeric value or None and interpretation. No rating,
closing-window, passing, points, pace, speed-unit or strategy formula is supplied.

Results/laps/loop/stages NASCAR IDs use only the verified relationships. The
directory's Driver_ID and membership_id never substitute for NASCAR identity.
Note DriverIDs remain unverified commentary references. Archived pits have
no evidenced driver ID: even an identical name/car in weekend results cannot
attach a pit observation to a driver.

## Validation and availability

Known envelopes, array/object types, required identities, present context fields,
numeric types/ranges, duplicate driver/run/stage/lap identities and bounded text
are validated. Additional fields are tolerated, not exported as raw dictionaries.
Booleans do not become integers. Numeric strings are accepted only for observed
LapSpeed strings. Null/missing optional fields stay unknown; empty arrays remain
empty. Malformed present fields fail the selected dataset rather than fabricating
zero or silently clipping an oversized result. Independently requested peers
remain available. Missing result arrays differ from explicitly empty results.

Unknown signed enum codes are retained. Position/lap/score zero stays a reported
value without an inferred meaning. Candidate 999/-1/zero averages/pit values
retain their numeric value with `candidate_sentinel`; no confirmed unavailable
meaning has been established for those candidates. Phase 3B's physical pit
projection still omits nonpositive clocks, and the accompanying historical
reported metrics preserve the original values. No stop completion/count,
negative physical duration or missing comparison is derived from them.

| Status | Meaning |
| --- | --- |
| `available` | A supported shape yielded normalized reported facts |
| `empty` | Valid empty envelope/array; no assertion of unpublished/final results |
| `not_yet_published` | Reserved typed status for an evidenced publication signal; current CF profiles establish no such signal, so the CF adapter never guesses this state |
| `unsupported_unverified` | HTTP 404/410 with publication/coverage unknown; not a claim that all years/series lack this feed |
| `partial` | Aggregate of independently differing availability/failure states |
| `network_access_failure` | Network/denial/rate-limit/server error, active cooldown or exhausted request budget; fixed reason and retry metadata distinguish these |
| `invalid_schema_identity` | Invalid JSON, excessive size/structure, malformed numeric/schema field or conflicting identity |

Every result carries source endpoint kind (`dataset`), requested race key,
`reported_identity` versus `path_context_only` validation, coverage,
local retrieval time, transport delivery/cache outcome, successful HTTP response
time, status and optional Retry-After. These times are not a content clock.
No unverified field certifies official final classification, including
inspection_complete, finishing_position, checkered or the URL's historical path.

Only the supplied 2024/1/5392 examples (all except pits) and 2026/1/5626 pit
example receive `observed_example` coverage. Explicit other selections receive
`unverified_context` even if their response validates. Laps/notes/averages/pits
have no complete reported race context; path provenance cannot certify content
identity. STAGES reports race/run, LOOP race/series, WEEKEND race/series/season;
absent fields are never filled in as source facts. No cross-feed join is automatic.

## Memory, HTTP and lifecycle budgets

- Startup and ordinary live/schedule/reference/scoring refreshes request **zero**
  historical detail feeds. Explicit selection performs at most one attempt per
  requested feed: up to seven for all datasets; no automatic retry loop.
- At most eight distinct history keys are in flight per entry. Excess keys
  return `request_budget` without I/O. Concurrent identical keys share the same
  task/result even with no-cache/no-store responses. Identical waiters do not
  multiply upstream requests.
- History reuses the shared session, 15-second transport timeout, serialized
  request lock, 2 MiB decompressed response cap, validators, Retry-After and
  host-wide 429 controls (including the existing compact durable host guard).
  This lock can delay other transport consumers behind on-demand reads;
  it does not change live scheduling or permit faster CF polling.
- A separate two-document LRU retains decoded historical responses/validators;
  history cannot evict live/schedule cache entries. Each response is at most
  2 MiB of JSON bytes (4 MiB combined input size; decoded Python objects use
  additional memory). Normalized results are not retained by the broker after
  the final waiter returns. Consumers own and must bound their retained results.
- Fallback freshness is one hour; server no-store/no-cache, max-age, Age,
  Date/Expires, ETag and Last-Modified semantics take precedence. A 304 requires
  an existing body. Expiry means revalidation, not deletion: bodies may remain
  until two-entry LRU eviction or lifecycle cleanup. Invalid parsed bodies are
  discarded. No-store responses retain no body/validator after delivery.
- A 60-second per-path request floor also applies to explicit on-demand reads,
  within the transport's bounded 24-slot deadline table. Server/failure
  cooldowns can lengthen it. Churning more than 24 paths can evict older local
  floor slots; this is not an installation-wide/hourly rate guarantee. These
  engineering limits do not establish NASCAR-permitted request rates.
- Limits per dataset: 100 drivers; 5,000 laps per driver and 50,000 lap rows
  total; 5,000 flag/segment/note-lap entries; 10,000 notes, up to 100 references
  per note; 2,000 pits; 30 weekend/average sessions; 20 stages; 2,048 characters
  per text field. Oversized datasets are explicitly unavailable; no truncation,
  pagination/alternate URL guessing or partial-row reconstruction occurs.
- Cancelling one consumer leaves another's shared request active. The last
  cancellation aborts/drains upstream I/O. Failed/cancelled setup, entry unload,
  options reload and HA stop cancel/drain history tasks and clear historical
  response bodies/validators. Normal reload keeps existing non-history HTTP
  cache/backoff; restart restores only existing compact polling/event state.
  It restores no historical body, validator or normalized result.

No historical data is written to Recorder, state attributes, HA Store, logs or
raw diagnostics. Diagnostics retain only the existing bounded transport metadata.
Offline demonstration constructs a tiny clearly fictional weekend and empty
other datasets without network or bundled-fixture fallback. Test fixtures are
handmade; no value-redacted placeholder is treated as functional race data.

See [validation](PHASE4A_VALIDATION.md) and [data-use limits](DATA_USE.md).
