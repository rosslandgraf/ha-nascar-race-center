# Phase 2 schedule fixture provenance

[`nascar/session_schedule.json`](nascar/session_schedule.json) is a handmade structural example. Race names, IDs,
venue, dates, and values are fictional. It is not a captured NASCAR payload.

The per-series `schedule-feed.json` array and field spellings are supported by
the `ScheduleItem` model and `get_full_schedule` consumer in
[`cbilling91/NascarPicks` at `7dea94ab2da3dec67837dae92f599e7748956dcb`](https://github.com/cbilling91/NascarPicks/tree/7dea94ab2da3dec67837dae92f599e7748956dcb),
`app/models/nascar.py` and `app/dependencies/nascar.py`. The eleven fields are
independently corroborated by
[`joegravelyn/nascar` at `a0b3b9ef10b0d242fa8230dda203eccef3384e83`](https://github.com/joegravelyn/nascar/blob/a0b3b9ef10b0d242fa8230dda203eccef3384e83/mysql_db/sql_scripts/schedule.sql).

Global race-list nested sessions use the existing pinned TannerYohe reference's
`BaseRaceInfo.schedule`: `event_name`, `notes`, `start_time_utc`, and `run_type`.
No current response, cancellation field, provider session ID, naive-time zone,
or automated data-use authorization has been verified. Explicit timestamp
offsets in fixtures test integration behavior and do not imply that current
NASCAR responses supply offsets.
