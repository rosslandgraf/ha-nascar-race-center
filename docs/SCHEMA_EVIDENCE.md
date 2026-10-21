# Provider schema evidence

Current follow-up: the [API reference library](api/README.md) records October 21
attempts for all 28 URLs. Every attempt was proxy-blocked before an origin
response; there are no new observed real schemas. The field dictionary labels
synthetic types/examples separately from community interpretations. The older
statements below describe the original phase work, not this follow-up attempt.

Evidence reviewed on October 20, 2026. No NASCAR CF endpoint was requested in
this task: the cloud network policy does not allow that host. Owner-reported
browser success remains separate from field-shape references and synthetic
fixture tests. None of these establish data-use permission.

The explicitly requested third-party references were reviewed critically:

- [`TannerYohe/nascar-api` at `3ab85bb543528d76521417b5534a6eedb09dcdf3`](https://github.com/TannerYohe/nascar-api/tree/3ab85bb543528d76521417b5534a6eedb09dcdf3).
- [`ooohfascinating/NascarApi/NewEndpointsDiscovered.MD`](https://github.com/ooohfascinating/NascarApi/blob/main/NewEndpointsDiscovered.MD),
  GitHub file blob `acd3f16f485c81823d1cb6274a3ed75008bf7c73` when read.

The first reference supplies a consistent narrow parsing contract. No source
implementation or upstream dataset was copied. The second agrees with the live
field names but is not an official schema or an authorization document.

| Adapter | Narrow contract used | Pinned reference |
| --- | --- | --- |
| Global season list `/cacher/{year}/race_list_basic.json` | Object containing `series_1`, `series_2`, `series_3` lists | [`repos/historic.py`, `get_races`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/repos/historic.py) |
| Schedule row | `race_id`, `series_id`, `race_name`, `date_scheduled`, `track_name` | [`models/base_race_info.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/models/base_race_info.py) |
| Embedded race schedule | `race_season`, `track_id`, and `schedule` rows with `event_name`, `notes`, `start_time_utc`, `run_type` | Same pinned `models/base_race_info.py` |
| Per-series session feed `/cacher/{year}/{series}/schedule-feed.json` | Array of rows with `race_id`, `race_name`, `series_id`, `track_id`, `track_name`, `event_name`, `run_type`, `start_time_utc`, `end_time_utc`; local `start_time`/`end_time` are deliberately ignored | [`cbilling91/NascarPicks` model at `7dea94ab2da3dec67837dae92f599e7748956dcb`](https://github.com/cbilling91/NascarPicks/blob/7dea94ab2da3dec67837dae92f599e7748956dcb/app/models/nascar.py) and [consumer](https://github.com/cbilling91/NascarPicks/blob/7dea94ab2da3dec67837dae92f599e7748956dcb/app/dependencies/nascar.py) |
| Global live feed `/live/feeds/live-feed.json` | Object containing `race_id`, `series_id`, `lap_number`, `flag_state`, `run_type`, `time_of_day_os` | [`models/live_info.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/models/live_info.py) |
| Flag code | 1 green, 2 yellow, 3 red, 4 white, 5 checkered, 8 hot track, 9 cold track | [`enums/flag.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/enums/flag.py) |

The schedule-feed contract is also corroborated by
[`joegravelyn/nascar` at `a0b3b9ef10b0d242fa8230dda203eccef3384e83`, `mysql_db/sql_scripts/schedule.sql`](https://github.com/joegravelyn/nascar/blob/a0b3b9ef10b0d242fa8230dda203eccef3384e83/mysql_db/sql_scripts/schedule.sql).
These are community code/schema references, not a current CF capture or official
contract. A field's appearance in a typed client does not establish its timezone
or status semantics. Exact supported shapes are exercised with handmade records
and parser tests; see [`tests/fixtures/PHASE2_SCHEDULES.md`](../tests/fixtures/PHASE2_SCHEDULES.md).

`run_type` is a **session kind**, normalized to practice/qualifying/race using
the second reference; it does not prove that a session is currently running or
that results are final. Unknown codes remain unknown. A fresh transport response
does not prove fresh NASCAR data: the source timestamp remains separate from
the local observation time.

Only dates with an explicit timezone offset are normalized to UTC. A naive
`date_scheduled`, missing time, or invalid optional time remains unknown rather
than guessing a track timezone. Whether naive dates are actually UTC needs an
authorized real response capture and official clarification. This can limit
next-race entities with real feeds until the schema gate is resolved.

Missing series envelopes, wrong/missing identities, duplicate race IDs, and
unknown live envelopes raise a schema error; they do not become fabricated
empty schedules or zero-valued sensors. Unsupported optional fields are ignored.
A JSON `null` live payload is supported as an empty-provider representation for
mocked tests, **not claimed as a verified NASCAR off-season response**. Empty
objects and unrecognized off-season payloads fail explicitly pending evidence.

The experimental CF adapter is opt-in and remains unverified against a current
anonymous response. Default demonstration mode uses handmade examples, requires
no credentials, and makes no network requests. The broad endpoint inventory is
documented separately; a URL being listed does not mean an adapter exists.

## Schedule identity, enrichment and time limits

The Phase 1 identity and naive-time regression protections are retained.
`Race` now carries season/track identity and immutable sessions. Sessions normalize
the source event name, kind, known start/end and notes. For races represented in
the detailed feed, its sessions replace the embedded basic sessions, allowing
removed detailed rows to disappear. Races absent from that optional feed retain
the usable basic schedule. An empty detailed feed is treated as no enrichment;
it does not erase the basic season. A detailed feed can independently provide
races when the basic list fails. Failure of optional enrichment is reported in
diagnostics while retaining the usable schedule.

Neither documented shape exposes an authoritative session ID. Internal IDs derive
from series/season/race plus session kind and name; start/end and source ordering
are excluded. Time revisions preserve identity, while source renames can change
it. Indistinguishable duplicate sessions are a schema error. Status properties
exist in the normalized models for providers with reliable status evidence, but
the CF parsers do **not** invent `status`, cancellation or postponement fields.
Calendar cancellation tests use explicitly normalized synthetic status values,
not an asserted CF cancellation schema. Missing sessions are not interpreted as
proof of cancellation.

Malformed optional embedded-session rows do not discard an otherwise valid basic
race: the normalized race retains its identity/start/track with an empty session
tuple and `sessions_failed` flag. Successful detailed-feed enrichment clears
that flag. This distinguishes a usable race schedule from unavailable session
details; it does not synthesize omitted practice or qualifying data.

Detailed race-session timing takes precedence over an older basic-list start.
If the detailed feed identifies a race-kind session but its start is unknown,
naive or unpublished, the merged race start becomes unknown too. Multiple
ambiguous race-kind sessions likewise cannot select a single race start. An old
basic time is not reused to conceal a detailed TBD/postponement. Basic race-start
fallback applies only when the detailed feed supplies no race-kind session.

Defensive bounds are 500 basic races per series, 100 embedded events per race,
and 5,000 detailed-feed rows, within the transport's 2 MiB response limit. These
are implementation protection limits, not claims about provider maximums.

### Timestamp behavior

`date_scheduled` values with `Z` or an explicit numeric offset are converted to UTC. Date-only, timezone-free, missing, malformed, and out-of-range values become `None` without assigning a timezone. No current response or official source timezone contract has been obtained. A third-party datetime type alone cannot establish UTC or Eastern semantics.

The same rule applies to `start_time_utc` and `end_time_utc`: the field name alone
does not authorize assigning UTC to a naive value. Invalid or nonpositive
duration is never replaced with a guessed number of minutes. Calendars use a
clearly labeled all-day notice when only a valid start is known, and omit events
without a usable start. Weekend entries derive local date ranges from known
sessions rather than assuming a Friday-to-Sunday schedule. Home Assistant
performs local timezone display and DST conversion for known offset timestamps.

These races retain identity/name/track and contribute to the schedule count, but cannot drive next-race selection, local race-boundary timers, or race-window polling. If all dates lack offsets, next-race name/start stay unknown. In mixed schedules the next-race entities select only among timestamped races, so they can skip a race whose time is unknown. The scheduled-races sensor exposes the bounded `unknown_start_times` count, and diagnostics expose per-series `unknown_start_time_counts` plus `timestamp_policy: explicit_offset_required`. These counts include all unknown starts (including omissions and invalid values); they do not claim every omission was a timezone error. Resolving source semantics requires evidence before changing this policy.

## Driver and track reference contracts

The reference directory shapes and exact source spellings come from
[`ooohfascinating/NascarApi` at `1640846fddd82f39dd9bfa35433aa6f34ec70051`, `NewEndpointsDiscovered.MD`](https://github.com/ooohfascinating/NascarApi/blob/1640846fddd82f39dd9bfa35433aa6f34ec70051/NewEndpointsDiscovered.MD),
file blob `acd3f16f485c81823d1cb6274a3ed75008bf7c73`.

| Feed | Community-supported source fields | Normalized interpretation |
| --- | --- | --- |
| `drivers.json` | Object with `response` array; `Nascar_Driver_ID`, `Full_Name`, `Driver_Series`, `Badge`, `Team`, `Manufacturer` | Stable NASCAR ID/name, explicit series associations, optional numeric-string car number, team and textual manufacturer |
| `tracks.json` | Object with `items` array; `track_id`, `track_name`, `city`, `state`, `length`, `track_type`, `track_surface` | Track identity, supplied locality, length in miles, track type and surface |

The pinned community document explicitly describes `length` as track length in
miles; the normalized unit is based on that statement, not inferred from a venue.

`Badge` as a numeric-string car number is corroborated by
[`PyPlumber/Incorporator` at `2edf245288d144a42feedd3023f4a96183688a5e`, `examples/09-nascar-fantasy-fjord/nascar_fantasy.py`](https://github.com/PyPlumber/Incorporator/blob/2edf245288d144a42feedd3023f4a96183688a5e/examples/09-nascar-fantasy-fjord/nascar_fantasy.py),
blob `3ea7bcd15f3ffc13887bd91538a43028ecd0f0e3`.
Known series slugs `nascar-cup-series`, `nascar-xfinity-series` and
`nascar-craftsman-truck-series` are corroborated by
[`Harborofficial/Harbor` at `9b811556d13f6eb2ba7c524a5bb0d561c88fae94`, `src/lib/sports/nascar-data.ts`](https://github.com/Harborofficial/Harbor/blob/9b811556d13f6eb2ba7c524a5bb0d561c88fae94/src/lib/sports/nascar-data.ts),
blob `f343dd18ce370b423913587c22d825d115fa2ebf`. Unknown series labels remain
metadata without a guessed numeric series. Sponsor/slug changes need new evidence.

Rows sharing a NASCAR driver ID are grouped into one driver with explicit
associations. Name conflicts for the same ID fail rather than choosing an
arbitrary record. Top-level car/team/manufacturer values are exposed only when
all associations agree; leading zeroes in car numbers are preserved. A directory
entry does not prove an active roster, race entry or current team. `Manufacturer`
can contain a logo URL in community examples: URLs are omitted, never fetched or
converted into an inferred manufacturer. Images and other unsupported metadata
are ignored. No source data or implementation is copied into the integration.

Invalid driver/track rows without required identity/name are skipped. A nonempty
feed with no usable identities fails explicitly rather than pretending to be an
empty directory. Reference rows are bounded at 10,000 drivers and 1,000 tracks;
optional text/number validation also bounds malformed metadata. These are
defensive implementation limits. Synthetic `drivers.json` and `tracks.json`
fixtures validate the contract without claiming current provider compatibility.

## Focused final Phase 2 contract review (2026-10-20)

The pinned TannerYohe basic-race model, NascarPicks schedule model/consumer and
ooohfascinating reference document were reread through GitHub. No CF endpoint
was requested. These community references document parsing hypotheses; there
is still no verified official/current NASCAR response schema in this project.

| Boundary | Assumption and effect on real data |
| --- | --- |
| Basic season | Requires an object with the selected `series_N` array and valid `race_id`, `series_id`, `race_name` per row. A bare list, absent series, duplicate ID or contradictory season fails explicitly. Missing optional track/time/session data preserves race identity. |
| Weekend sessions | Reads embedded `schedule` and the per-series `schedule-feed.json` array; it does not fetch the separate historical `weekend-feed.json`. Detailed rows require race identity and `event_name`; malformed/ambiguous detail fails enrichment while usable basic races survive. Empty details cannot establish an empty season when the basic request failed. |
| Time | The pinned NascarPicks consumer parses `start_time_utc` using `%Y-%m-%dT%H:%M:%S`, and its model explicitly assigns UTC to naive input. This is concrete evidence that a community consumer expects offset-free values, but does not establish current NASCAR timezone semantics. Our explicit-offset policy rejects those values. A structurally accepted feed can therefore populate race counts/names yet provide no usable calendar or next-race times. No timezone inference was added. |
| Duration/status/identity | Embedded sessions have no supported end field. Missing/invalid detailed ends produce date notices, not timed sessions. No referenced authoritative session ID or cancellation/postponement status contract is implemented. Renames can change derived session IDs; indistinguishable kind/name duplicates fail enrichment. Timing revisions are supported, explicit CF cancellation detection is unverified. |
| Drivers | Requires a `response` array and `Nascar_Driver_ID` plus `Full_Name` for usable rows. It never substitutes secondary ID or car number. Unknown `Driver_Series` slugs preserve names/IDs/labels but cannot populate numeric series associations. Missing optional facts and manufacturer image URLs remain unknown. Conflicting names for one ID fail the directory. |
| Tracks | Requires an `items` array and `track_id` plus `track_name`. Missing locality/length/type/surface does not invalidate a venue. Schedule track names remain usable if the directory fails. No track timezone is inferred. |

A known start with unknown duration creates a date notice in the configured HA
timezone. Native calendar automations for that all-day notice follow local date
boundaries, not its known session start. Consumers needing exact session timing
must distinguish notices from timed events. Overlap queries return all sessions;
the calendar's single current-event state prefers a timed active session with the
earliest end, then a date notice/weekend, and updates locally at boundaries.

Future-season envelope/slug changes, publication timing, removal semantics and
cross-year source revisions remain live compatibility hypotheses. Passing
handmade fixtures does not close these gates or authorize provider access.

## Phase 3A live timing contract

The existing pinned live model and enhanced live-feed community document above
were reread before development. The exact supported fields, handmade fixture,
units/status limitations and timestamp policy are recorded in
[PHASE3A_LIVE.md](../tests/fixtures/PHASE3A_LIVE.md). No CF host was requested;
anonymous current schema, source timestamps, permitted cadence and data-use
rights remain unverified. This extends the experimental adapter only.
