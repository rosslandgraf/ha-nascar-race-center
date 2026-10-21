# NASCAR structural fixtures — synthetic only

All six JSON samples here are handmade, fictional regression examples moved
unchanged from `tests/fixtures/`. They are **not actual NASCAR captures**.
[PROVENANCE.json](PROVENANCE.json) records each file, source-evidence link and
content hash. Tests consume these files; production code never reads them.

| File | Contract exercised | Evidence |
| --- | --- | --- |
| `schedule.json` | Global season series envelopes, optional time/track | [Phase 1/2 evidence](../../../docs/SCHEMA_EVIDENCE.md) |
| `session_schedule.json` | Per-series detailed sessions, explicit-offset start/end | [Phase 2 notes](../PHASE2_SCHEDULES.md) |
| `drivers.json` | Driver directory, stable IDs, multi-series associations | [Reference evidence](../../../docs/SCHEMA_EVIDENCE.md#driver-and-track-reference-contracts) |
| `tracks.json` | Track directory and optional physical metadata | Same reference evidence |
| `live.json` | Minimal global live context | [Phase 1/2 evidence](../../../docs/SCHEMA_EVIDENCE.md) |
| `live_timing.json` | Nested vehicle/driver timing and laps-led intervals | [Phase 3A notes](../PHASE3A_LIVE.md) |

The one detailed-session file contains fictional Cup rows. Series 2/3 regression
cases explicitly change series IDs; it is not a separately observed response for
those series. No samples exist for unaccessed historical, legacy or excluded
endpoints. Do not create fake captures to fill the catalog.

See the [library](../../../docs/api/README.md) for retention policy and manual
schema checks. New raw responses stay in ignored `work/` until permission and
content review allow otherwise.
