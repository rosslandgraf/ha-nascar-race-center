# Schema reference — evidence status and field dictionary

## Actual current NASCAR observations

**No response body was obtained. There are no observed real JSON schemas in this
revision.** All 28 requests were blocked at proxy CONNECT. None of the field rows
below should be cited as an observed NASCAR requirement, nullability guarantee,
example value, timestamp format or unit verification. See the
[catalog](ENDPOINT_CATALOG.md) and [probe evidence](probes/2026-10-21.json).

| Endpoint group | Current real schema | Nested fields / timestamps / nullability |
| --- | --- | --- |
| Global live (5) | Not observed | Unverified |
| Schedule/reference (7) | Not observed | Unverified |
| Historical/statistical (8) | Not observed | Unverified |
| Legacy/race-specific (4) | Not observed | Unverified |
| Prior error/login (4) | Not observed; excluded | No guessed fields or protected-content samples |

## Reading the synthetic field dictionary

The following exhaustive tables describe **only the six existing handmade JSON
fixtures** now located in `tests/fixtures/nascar/`. They document exact spellings,
nested JSON bracket paths, literal JSON types, synthetic examples and what the
current software does. `[*]` unions every array element; boolean is distinct from
integer, and integer from nonintegral number. These are observation types in the
fictional file, not all types accepted by a parser or permitted by the provider.

Missing/null markers refer **only to the synthetic file**. “Not observed” never
means required/non-null in NASCAR. Requiredness and source optionality remain
unknown for every field. Empty arrays cannot establish their element schema.
Unknown extra fields are tolerated by production parsers. The field meanings and
units are interpretations from [pinned community evidence](../SCHEMA_EVIDENCE.md),
unless explicitly labeled implementation behavior; no unit/timezone was directly
verified in this audit. Examples are fictional and must never populate production.

For every fixture see [individual provenance](../../tests/fixtures/nascar/PROVENANCE.json).
The manual utility generates the same path/type/count dictionary from eligible
future real responses, without saving field values in its schema. Review all
array variants and missing/null values before updating this reference.

## Synthetic `drivers.json`

[Fixture](../../tests/fixtures/nascar/drivers.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | object | not observed / not observed | `object` | Container of the values documented below; no source semantics verified. |
| `$["response"]` | array | not observed / not observed | `array` | Community driver-directory array envelope; missing/wrong type is a schema error. |
| `$["response"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Community driver-directory array envelope; missing/wrong type is a schema error. |
| `$["response"][*]["Badge"]` | string | yes / not observed | `"07"` | Community consumer interprets numeric-string car number; leading zeroes retained. Current meaning unverified. |
| `$["response"][*]["Driver_Series"]` | string | yes / not observed | `"nascar-cup-series"` | Community slugs map to 1/2/3; unknown/sponsor-renamed slugs remain labels without guessed series. |
| `$["response"][*]["Full_Name"]` | string | not observed / not observed | `"Example Multi Driver"` | Driver directory display name; required by parser, not evidence of required source field. |
| `$["response"][*]["Manufacturer"]` | string | yes / not observed | `"Example Manufacturer"` | Optional directory manufacturer text; media URL values ignored, never fetched. |
| `$["response"][*]["Nascar_Driver_ID"]` | integer | not observed / not observed | `99011` | NASCAR identity in directory; joins live driver_id. No secondary-ID/car/name fallback. |
| `$["response"][*]["Team"]` | string | yes / not observed | `"Example Cup Team"` | Optional directory team; association metadata, not active roster or race team proof. |

## Synthetic `live.json`

[Fixture](../../tests/fixtures/nascar/live.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | object | not observed / not observed | `object` | Container of the values documented below; no source semantics verified. |
| `$["flag_state"]` | integer | not observed / not observed | `2` | Community mapping: 1 green, 2 yellow, 3 red, 4 white, 5 checkered, 8 hot_track, 9 cold_track. Current codes unverified. |
| `$["lap_number"]` | integer | not observed / not observed | `42` | Reported current lap count, nonnegative integer; no zero substitution when absent. |
| `$["race_id"]` | integer | not observed / not observed | `9001` | Reported race identity; join series + season + race, never a car number. Source uniqueness unverified. |
| `$["run_id"]` | integer | not observed / not observed | `9901` | Reported run identity within live context; omission remains unknown; not derived from race name. |
| `$["run_name"]` | string | not observed / not observed | `"Fictional Cup Demonstration"` | Reported run display label; not identity or proof of activity. |
| `$["run_type"]` | integer | not observed / not observed | `3` | Community mapping: 1 practice, 2 qualifying, 3 race; session kind does not establish activity. |
| `$["series_id"]` | integer | not observed / not observed | `1` | Reported national series identity; production accepts 1/2/3 and routes only matching selected series. |
| `$["time_of_day_os"]` | string | not observed / not observed | `"2026-11-01T15:00:00-05:00"` | Source update time hypothesis. Explicit-offset string required by current parser. Numeric epoch and naive formats unresolved; HTTP time never substitutes. |
| `$["vehicles"]` | array | not observed / not observed | `array` | Reported field array; optional failure isolates scoring while independent lap/flag survives. Not proof of complete roster. |

## Synthetic `live_timing.json`

[Fixture](../../tests/fixtures/nascar/live_timing.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | object | not observed / not observed | `object` | Container of the values documented below; no source semantics verified. |
| `$["elapsed_time"]` | integer | not observed / not observed | `1234` | Elapsed seconds interpretation from community model; no current source verification. |
| `$["flag_state"]` | integer | not observed / not observed | `1` | Community mapping: 1 green, 2 yellow, 3 red, 4 white, 5 checkered, 8 hot_track, 9 cold_track. Current codes unverified. |
| `$["lap_number"]` | integer | not observed / not observed | `42` | Reported current lap count, nonnegative integer; no zero substitution when absent. |
| `$["laps_in_race"]` | integer | not observed / not observed | `100` | Reported lap total; practice sentinels are not interpreted as race distance. |
| `$["laps_to_go"]` | integer | not observed / not observed | `58` | Reported remaining laps; not derived from total/current and not final-result evidence. |
| `$["race_id"]` | integer | not observed / not observed | `99001` | Reported race identity; join series + season + race, never a car number. Source uniqueness unverified. |
| `$["run_id"]` | integer | not observed / not observed | `7` | Reported run identity within live context; omission remains unknown; not derived from race name. |
| `$["run_name"]` | string | not observed / not observed | `"Synthetic Race"` | Reported run display label; not identity or proof of activity. |
| `$["run_type"]` | integer | not observed / not observed | `3` | Community mapping: 1 practice, 2 qualifying, 3 race; session kind does not establish activity. |
| `$["series_id"]` | integer | not observed / not observed | `1` | Reported national series identity; production accepts 1/2/3 and routes only matching selected series. |
| `$["time_of_day_os"]` | string | not observed / not observed | `"2026-10-20T20:00:00Z"` | Source update time hypothesis. Explicit-offset string required by current parser. Numeric epoch and naive formats unresolved; HTTP time never substitutes. |
| `$["vehicles"]` | array | not observed / not observed | `array` | Reported field array; optional failure isolates scoring while independent lap/flag survives. Not proof of complete roster. |
| `$["vehicles"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Reported field array; optional failure isolates scoring while independent lap/flag survives. Not proof of complete roster. |
| `$["vehicles"][*]["average_speed"]` | number | yes / not observed | `170.0` | Reported speed retained; unit not independently verified; no conversion. |
| `$["vehicles"][*]["best_lap_speed"]` | number | yes / not observed | `177.0` | Community document describes MPH; current unit unverified; no conversion. |
| `$["vehicles"][*]["best_lap_time"]` | number | yes / not observed | `30.5` | Best lap seconds interpretation from community evidence; positive finite numbers only. Current unit unverified. |
| `$["vehicles"][*]["delta"]` | number | yes / not observed | `0.75` | Reported signed gap retained. Unit, negative values and lap-deficit conventions unresolved; sensor has no assigned unit. |
| `$["vehicles"][*]["driver"]` | object | not observed / not observed | `object` | Nested competitor identity object, community-supported shape. |
| `$["vehicles"][*]["driver"]["driver_id"]` | integer | not observed / not observed | `99002` | NASCAR driver identity, join favorite/reference ID. Names/car numbers never substitute. |
| `$["vehicles"][*]["driver"]["full_name"]` | string | not observed / not observed | `"Synthetic Driver B"` | Display name only; optional in live scoring. |
| `$["vehicles"][*]["is_on_track"]` | boolean | yes / not observed | `true` | Explicit JSON boolean only; not inferred from pit/status/speed. |
| `$["vehicles"][*]["laps_completed"]` | integer | yes / not observed | `41` | Reported completed lap count, not source timestamp or live-activity proof. |
| `$["vehicles"][*]["laps_led"]` | array | yes / not observed | `array` | Reported intervals only; no sum without verified inclusivity/overlap/unfinished-interval rules. |
| `$["vehicles"][*]["laps_led"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Reported intervals only; no sum without verified inclusivity/overlap/unfinished-interval rules. |
| `$["vehicles"][*]["laps_led"][*]["end_lap"]` | integer | not observed / not observed | `10` | Reported nonnegative interval end; source semantics unresolved. Reversed/invalid intervals omitted. |
| `$["vehicles"][*]["laps_led"][*]["start_lap"]` | integer | not observed / not observed | `5` | Reported nonnegative interval start; inclusive/exclusive semantics unresolved. |
| `$["vehicles"][*]["last_lap_speed"]` | number | yes / not observed | `172.8` | Reported speed retained; unit not independently verified; no conversion. |
| `$["vehicles"][*]["last_lap_time"]` | number | yes / not observed | `31.25` | Lap seconds interpretation from community evidence; positive finite numbers only. Current unit unverified. |
| `$["vehicles"][*]["running_position"]` | integer | not observed / not observed | `2` | Reported positive rank; unique first rank needed for leader, no guessed tie-breaker. |
| `$["vehicles"][*]["starting_position"]` | integer | yes / not observed | `5` | Reported positive start rank; positions gained = starting minus running when both known. |
| `$["vehicles"][*]["status"]` | integer | not observed / not observed | `1` | Raw vehicle status code; community code 1 maps to running. Other codes unknown; no inferred retirement. |
| `$["vehicles"][*]["vehicle_manufacturer"]` | string | yes / not observed | `"Tyt"` | Reported text/code retained; media-like values ignored; brand expansion unverified. |
| `$["vehicles"][*]["vehicle_number"]` | integer, string | not observed / not observed | `"07"` | Car display value; integer converted to text, string leading zeroes retained; not identity. |

## Synthetic `schedule.json`

[Fixture](../../tests/fixtures/nascar/schedule.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | object | not observed / not observed | `object` | Container of the values documented below; no source semantics verified. |
| `$["series_1"]` | array | not observed / not observed | `array` | Series-list envelope; selected series is read independently. |
| `$["series_1"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Series-list envelope; selected series is read independently. |
| `$["series_1"][*]["date_scheduled"]` | null, string | not observed / yes | `"2026-11-01T14:30:00-05:00"` | Race start hypothesis. Parser accepts only explicit offset/Z ISO strings; naive/date-only/null are unknown. Source timezone unverified. |
| `$["series_1"][*]["ignored_future_field"]` | string | yes / not observed | `"additional fields are permitted"` | Handmade extra-field tolerance case only; no NASCAR source claim. |
| `$["series_1"][*]["race_id"]` | integer | not observed / not observed | `9001` | Reported race identity; join series + season + race, never a car number. Source uniqueness unverified. |
| `$["series_1"][*]["race_name"]` | string | not observed / not observed | `"Fictional Cup Demonstration"` | Race display name; parser requires nonblank text. |
| `$["series_1"][*]["series_id"]` | integer | not observed / not observed | `1` | Reported national series identity; production accepts 1/2/3 and routes only matching selected series. |
| `$["series_1"][*]["track_name"]` | string | yes / not observed | `"Example Speedway"` | Venue display name; schedule value remains usable without directory. |
| `$["series_2"]` | array | not observed / not observed | `array` | Series-list envelope; selected series is read independently. |
| `$["series_2"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Series-list envelope; selected series is read independently. |
| `$["series_2"][*]["date_scheduled"]` | string | not observed / not observed | `"2026-11-01T19:30:00Z"` | Race start hypothesis. Parser accepts only explicit offset/Z ISO strings; naive/date-only/null are unknown. Source timezone unverified. |
| `$["series_2"][*]["race_id"]` | integer | not observed / not observed | `9101` | Reported race identity; join series + season + race, never a car number. Source uniqueness unverified. |
| `$["series_2"][*]["race_name"]` | string | not observed / not observed | `"Fictional National Demonstration"` | Race display name; parser requires nonblank text. |
| `$["series_2"][*]["series_id"]` | integer | not observed / not observed | `2` | Reported national series identity; production accepts 1/2/3 and routes only matching selected series. |
| `$["series_2"][*]["track_name"]` | string | not observed / not observed | `"Example Speedway"` | Venue display name; schedule value remains usable without directory. |
| `$["series_3"]` | array | not observed / not observed | `array` | Series-list envelope; selected series is read independently. |

## Synthetic `session_schedule.json`

[Fixture](../../tests/fixtures/nascar/session_schedule.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | array | not observed / not observed | `array` | Container of the values documented below; no source semantics verified. |
| `$[*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Container of the values documented below; no source semantics verified. |
| `$[*]["end_time_utc"]` | string | not observed / not observed | `"2026-12-31T19:00:00Z"` | Scheduled end hypothesis. Explicit offset/Z and later than start required; no estimated duration. |
| `$[*]["event_name"]` | string | not observed / not observed | `"Practice 1"` | Session display name; internal session ID hashes kind/name with series/season/race. Renames can change identity. |
| `$[*]["race_id"]` | integer | not observed / not observed | `9901` | Reported race identity; join series + season + race, never a car number. Source uniqueness unverified. |
| `$[*]["race_name"]` | string | not observed / not observed | `"Fictional Year Boundary Weekend"` | Race display name; parser requires nonblank text. |
| `$[*]["run_type"]` | integer | not observed / not observed | `1` | Community mapping: 1 practice, 2 qualifying, 3 race; session kind does not establish activity. |
| `$[*]["series_id"]` | integer | not observed / not observed | `1` | Reported national series identity; production accepts 1/2/3 and routes only matching selected series. |
| `$[*]["start_time_utc"]` | string | not observed / not observed | `"2026-12-31T18:00:00Z"` | Scheduled start hypothesis. Explicit offset/Z only; UTC in field name does not verify naive UTC semantics. |
| `$[*]["track_id"]` | integer | not observed / not observed | `99001` | Join to track directory identity; optional enrichment must not disable schedule. |
| `$[*]["track_name"]` | string | not observed / not observed | `"Demonstration Speedway"` | Venue display name; schedule value remains usable without directory. |

## Synthetic `tracks.json`

[Fixture](../../tests/fixtures/nascar/tracks.json); **not a capture**. Source requiredness/nullability: unknown for every row.

| Exact JSON path | JSON types in synthetic file | Missing / null observed in synthetic file | Fictional example | Current interpretation / relationship |
| --- | --- | --- | --- | --- |
| `$` | object | not observed / not observed | `object` | Container of the values documented below; no source semantics verified. |
| `$["items"]` | array | not observed / not observed | `array` | Community track-directory array envelope; missing/wrong type is a schema error. |
| `$["items"][*]` | object | not observed / not observed | `object` | Array element; union of all fictional rows. Community track-directory array envelope; missing/wrong type is a schema error. |
| `$["items"][*]["city"]` | string | yes / not observed | `"Example City"` | Supplied locality text; no geography/timezone inference. |
| `$["items"][*]["length"]` | string | yes / not observed | `"1.5"` | Track miles interpretation from community document; accepts positive finite numeric text or number. Current unit unverified. |
| `$["items"][*]["state"]` | string | yes / not observed | `"Example State"` | Supplied state/locality text; no geography/timezone inference. |
| `$["items"][*]["track_id"]` | integer | not observed / not observed | `99001` | Join to track directory identity; optional enrichment must not disable schedule. |
| `$["items"][*]["track_name"]` | string | not observed / not observed | `"Example Speedway"` | Venue display name; schedule value remains usable without directory. |
| `$["items"][*]["track_surface"]` | string | yes / not observed | `"Asphalt"` | Supplied surface text. |
| `$["items"][*]["track_type"]` | string | yes / not observed | `"Intermediate"` | Supplied venue type text; no inferred classification. |

## Community-supported fields not present in these stored files

These are consumed by existing adapters and covered by inline handmade tests.
They are not real observations and are not newly invented feed contracts.

| Exact path / scope | Parser expectation | Meaning and relationship | Missing/null behavior |
| --- | --- | --- | --- |
| `$["series_N"][*]["race_season"]` | integer or decimal integer string | Season checked against request year; 1948–9999 defense bound | Falls back to request year; not proof source field is optional |
| `$["series_N"][*]["track_id"]` | positive integer or decimal string | Optional track-directory join | Unknown without a usable value |
| `$["series_N"][*]["schedule"]` | array | Optional embedded session enrichment | Absent/null yields empty tuple; malformed enrichment records failure without dropping race |
| `$["series_N"][*]["schedule"][*]["event_name"]` | nonblank string | Session display name/internal identity input | Invalid name fails enrichment |
| `$["series_N"][*]["schedule"][*]["run_type"]` | nonnegative integer/string | Session kind, same community mapping as live | Unknown kind if absent/null/unknown code |
| `$["series_N"][*]["schedule"][*]["start_time_utc"]` | explicit-offset ISO string | Session start normalized to UTC; naive zone unverified | Unknown time |
| `$["series_N"][*]["schedule"][*]["notes"]` | nonblank string | Optional note; not a status contract | Unknown note |

Detailed local `start_time`/`end_time`, arbitrary cancellation/status fields, media
and unsupported fields are intentionally ignored. The historical `weekend-feed`
schema is not interchangeable with embedded/detailed season sessions. There is
no observed contract for historical, legacy, flag/pit/stage/points, recap or Drive
payloads; leave those schemas undocumented rather than inventing fields.

## Cross-series, season and session-state limits

The basic synthetic list contains series 1/2 and an empty series 3 array; detailed
session samples are fictional series 1. Replay tests mutate IDs and values to
exercise all three series, practices/races and run switches. This proves routing
logic only; no real cross-series schema equivalence is established. Old path race
IDs 5392/5170/4817 and archived pit ID 5626 are requested context only. No race
schedule mapping or active run was observed.

A global live feed supplies only its own reported series. Timestamp-free, numeric,
naive, invalid and far-future source times cannot prove freshness. HTTP cache
metadata and a successful request are transport evidence. Flag 5 is interpreted
as a checkered observation, not official final results. No active-race, off-season,
empty/inactive-session representation, timestamp unit/timezone, cancellation
semantics, source removal semantics or permitted cadence was verified.

The production JSON decoder now rejects duplicate object keys rather than letting
the last conflicting series/race/driver key silently overwrite earlier identity.
This is an independently reproduced malformed-input fix, not a discovered NASCAR
schema change. All normal samples and live network routing remain unchanged.
