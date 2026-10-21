# Phase 3A structural contract

[`nascar/live_timing.json`](nascar/live_timing.json) is handmade, with fictional identities, times and values. It
is not a CF capture. No NASCAR request was made: the managed destination policy
excludes `cf.nascar.com`. Replays in tests revise this structure for all three
series, runs, races, omissions and stale timestamps; they are not real races.

Evidence reread through GitHub before implementation:

- TannerYohe/nascar-api at `3ab85bb543528d76521417b5534a6eedb09dcdf3`,
  `src/nascar_api/models/live_info.py`: `vehicles`, numeric timing/position/speed
  fields, `laps_led` intervals (`start_lap`, `end_lap`), race lap totals,
  remaining laps, elapsed time, `run_id` and `run_name`.
- ooohfascinating/NascarApi at `1640846fddd82f39dd9bfa35433aa6f34ec70051`,
  `NewEndpointsDiscovered.MD`, ENHANCED LIVE FEED DATA: nested
  `driver.driver_id`/`full_name`, `status` 1 = running, `is_on_track`,
  `delta` = gap to leader, best lap in seconds and best lap speed in MPH.

These are community parsing hypotheses, not official/current CF verification.
Only status 1 is mapped; all other status codes remain numeric, without guessed
retirement labels. `delta` is preserved as a reported gap without assigning
units or converting negative values into laps. Speed values retain source field
names; no conversion is performed. Lap times use seconds, consistent with the
community timing model/documentation. Laps-led intervals remain reported
intervals: inclusive endpoints, overlaps and ongoing intervals are unverified,
so no total is calculated. Team and interval-to-next fields have no supported
contract here and are omitted. No pit/stage/points fields are consumed.

`time_of_day_os` still requires an explicit offset. An integer, naive string,
missing, invalid or far-future timestamp cannot establish source freshness.
A successful request and locally observed content changes cannot prove source
freshness. Missing `run_id` remains unknown, never a guessed session ID.
