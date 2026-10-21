# NASCAR API: Start Here

## Executive summary

**This is the complete human-readable entry point for this archive.** It consolidates all 28 endpoints, all 1,578 observed field paths, interpretation notes, identifier relationships and compatibility limits. Individual files remain available as supporting evidence.

The October 21, 2026 capture attempted 28 supplied URLs anonymously: **24 populated JSON documents, one successful empty article envelope, and three HTTP 403 Drive responses**. No fresh network requests were made for this documentation update. All observations refer to the existing snapshots, whose UTC request-start timestamps appear below.

**The samples are value-redacted structural representations derived from real responses, not original response fixtures.** Every scalar has a placeholder of the same type and duplicate redacted array shapes are collapsed. Use the field dictionary and format counts to interpret structure; placeholders cannot validate IDs, dates, code meanings, scoring or replay behavior. Raw-response redistribution permission remains unresolved.

Most consequential findings: global leaderboard and stage points refer to different races; global points have zero context IDs; driver IDs occupy multiple namespaces; schedule dates lack offsets; lap speeds can be strings; null/999/-1 values need explicit handling; session IDs cannot be interchanged. One Cup schedule race is missing from the race list.

## Navigation

- [Endpoint matrix](#endpoint-matrix)
- [Verified findings and interpretation](#verified-findings-and-interpretation)
- [Phase compatibility](#phase-compatibility)
- [Discrepancies and prior-assumption limits](#discrepancies-and-prior-assumption-limits)
- [Complete endpoint and field dictionary](#complete-endpoint-and-field-dictionary)
- [Supporting file index and Codex workflow](#supporting-file-index-and-codex-workflow)

## Endpoint matrix

All URLs use https://cf.nascar.com. Exact URLs are retained in the endpoint entries below. Path parameters are routing observations from supplied examples, not an official API contract. None of the supplied examples uses query parameters. No credentials/cookies were supplied; redirects were not followed.

| ID | Purpose | HTTP / content | Root and observed paths | Parameters | Detail |
|---|---|---|---|---|---|
| 01 | Live leaderboard and session | 200 / populated JSON | object; 73 paths | No path selectors | [Open](#endpoint-01) |
| 02 | Live flag history | 200 / populated JSON | array; 9 paths | No path selectors | [Open](#endpoint-02) |
| 03 | Live pit stops | 200 / populated JSON | array; 27 paths | No path selectors | [Open](#endpoint-03) |
| 04 | Live championship points | 200 / populated JSON | array; 30 paths | No path selectors | [Open](#endpoint-04) |
| 05 | Live stage points | 200 / populated JSON | array; 12 paths | No path selectors | [Open](#endpoint-05) |
| 06 | Combined season race list | 200 / populated JSON | object; 160 paths | season=2026 | [Open](#endpoint-06) |
| 07 | Driver directory | 200 / populated JSON | object; 61 paths | No path selectors | [Open](#endpoint-07) |
| 08 | Track directory | 200 / populated JSON | object; 33 paths | No path selectors | [Open](#endpoint-08) |
| 09 | Cup session schedule | 200 / populated JSON | array; 13 paths | season=2026, series=1 | [Open](#endpoint-09) |
| 10 | Series 2 session schedule | 200 / populated JSON | array; 13 paths | season=2026, series=2 | [Open](#endpoint-10) |
| 11 | Truck session schedule | 200 / populated JSON | array; 13 paths | season=2026, series=3 | [Open](#endpoint-11) |
| 12 | Cup race list | 200 / populated JSON | array; 53 paths | season=2026, series=1 | [Open](#endpoint-12) |
| 13 | Historical weekend/results | 200 / populated JSON | object; 142 paths | season=2024, series=1, race=5392 | [Open](#endpoint-13) |
| 14 | Historical lap times | 200 / populated JSON | object; 18 paths | season=2024, series=1, race=5392 | [Open](#endpoint-14) |
| 15 | Historical lap notes | 200 / populated JSON | object; 603 paths | season=2024, series=1, race=5392 | [Open](#endpoint-15) |
| 16 | Historical loop statistics | 200 / populated JSON | array; 27 paths | season=2024, series=1, race=5392 | [Open](#endpoint-16) |
| 17 | Historical lap averages | 200 / populated JSON | array; 27 paths | season=2024, series=1, race=5392 | [Open](#endpoint-17) |
| 18 | Archived pit stops | 200 / populated JSON | array; 27 paths | season=2026, series=1, race=5626 | [Open](#endpoint-18) |
| 19 | Archived stage points | 200 / populated JSON | array; 12 paths | season=2024, series=1, race=5392 | [Open](#endpoint-19) |
| 20 | SnappyTV metadata | 200 / populated JSON | object; 66 paths | season=2024, series=1, race=5392 | [Open](#endpoint-20) |
| 21 | Legacy leaderboard | 200 / populated JSON | object; 73 paths | series=1, race=5170 | [Open](#endpoint-21) |
| 22 | Legacy championship points | 200 / populated JSON | array; 29 paths | series=1, race=5170 | [Open](#endpoint-22) |
| 23 | Legacy pit stops | 200 / populated JSON | array; 27 paths | series=1, race=5170 | [Open](#endpoint-23) |
| 24 | Legacy practice averages | 200 / populated JSON | array; 24 paths | season=2019, series=2, race=4817 | [Open](#endpoint-24) |
| 25 | Driver recap/article envelope | 200 / empty articles | object; 6 paths | season=2024, series=1, race=5392 | [Open](#endpoint-25) |
| 26 | Series 1 Drive configuration | 403 / XML denial | unverified; 0 paths | series=1 | [Open](#endpoint-26) |
| 27 | Series 2 Drive configuration | 403 / XML denial | unverified; 0 paths | series=2 | [Open](#endpoint-27) |
| 28 | Series 3 Drive configuration | 403 / XML denial | unverified; 0 paths | series=3 | [Open](#endpoint-28) |

## Verified findings and interpretation


### Coverage and provenance
28 documented URLs attempted, 25 HTTP 200 JSON responses, comprising 24 populated documents and one empty article envelope. Three Drive URLs returned HTTP 403 XML: MissingKey, “Missing Key-Pair-Id query parameter or cookie value”. This is an access requirement reported by the endpoint/CDN, not a proxy CONNECT denial. No attempt was made to obtain a key, cookie or media asset. Each exact request outcome is retained. Captures were single snapshots, not synchronized; they do not prove active-session correctness. Raw data is excluded from this distribution; the package carries redacted structural samples, exhaustive observed-field profiles, safe request metadata and limited factual ID/enum evidence.

### Schedules and references (06–12)
06 is an object keyed series_1, series_2 and series_3, whereas 12 is a bare array. The series_1 value equals 12 exactly in these captures (see computed relationship checks). Series race counts are 40, 33 and 25 respectively. Schedule feeds 09–11 are arrays of 111, 91 and 72 sessions. Cup schedule race_id 5696 is absent from the combined season race list in 06; all other schedule race IDs join, and all schedule track IDs join to 08. Do not silently drop unmatched sessions. They report event_name, run_type, race_id, series_id, track_id and paired local/UTC start/end strings. Datetime strings lack offsets even in fields suffixed _utc. Attach UTC based on field semantics only; never interpret all naive strings as host local time. A local timezone remains a provider-contract question. 06/12 expose scheduled and actual dates, laps and distances, stage laps, results-related fields and nested schedule. The first Cup record has differing date_scheduled and race_date; do not treat them as interchangeable or infer a postponement reason.

07 has status/message/response wrapper with 915 driver records. Nascar_Driver_ID is a numeric NASCAR identity; Driver_ID is a different string identity. Example observed pair: NASCAR 4023 versus Driver_ID "374500". Match live driver.driver_id and historical NASCARDriverID to Nascar_Driver_ID, not blindly to Driver_ID. Blank metadata and year-0001 datetime strings exist, so parse dates defensively. 08 wraps 49 tracks in items, with numeric track_id, length, city/state and nullable races. No linked logos/photos were downloaded. All string values, including asset URLs, are redacted from samples.

### Live feed, flags and lifecycle (01–02)
01 is an object with 22 root keys. Observed race_id 5633, series_id 1, run_id 8 and track_id 84; 37 vehicles. vehicles[].driver is nested, with driver_id and names. Positions use running_position and starting_position; laps, best/last lap times and speeds, delta, elapsed times, Boolean is_on_track/is_on_dvp, and laps_led interval arrays exist. Preserve source vehicle_number as a string. stage is an object with stage_num, finish_at_lap and laps_in_stage. Numeric flag_state/status/run_type meanings are not established by field names; observed domains are supplied without invented mappings. The snapshot reports lap_number 312 and laps_to_go 0, so it is not evidence of an active green session.

02 is an array of 15 flag entries, including nullable comment/beneficiary. time_of_day is numeric; time_of_day_os is an offset-bearing ISO-like string with fractional seconds. 01 includes seven fractional digits. Parsers must tolerate subsecond precision without silently dropping timezone offsets. Numeric elapsed_time and time_of_day units are not formally documented here; do not assume Unix timestamps. Flag history may describe another event because 02 supplies no root race context. Fresh HTTP headers do not prove fresh race content.

### Pit stops and stages (03, 05, 18, 19, 23)
03 is a bare array of 337 pit rows with car number/name but no driver_id or explicit race_id. 18 has 300 archived rows for path race 5626; 23 has 180 legacy rows for path race 5170. Fields cover leader_lap/lap_count, in/out flags and race times, lane and box durations, changed-tire Booleans, type, ranks and positions_gained_lost. Zero and -1 values occur, including -1 box/duration values in 18. Treat them as candidate sentinel/unknown values until confirmed, not negative physical pit times. 01 embeds pit_stops with a different schema, including the source misspelling positions_gained_lossed. Embedded pit records include zero-time entries, so array length is not a verified count of completed stops. Manufacturer strings differ by source (abbreviations versus full names).

05 is an array of two stage objects with race_id 5168 and run_id 4, not race 5633 from 01. Each contains stage_number and results with driver_id, vehicle_number, position and stage_points. 19 has the same general nesting for historical race 5392, run_id 10. Never merge global stage points with the global leaderboard without a context check. Stage data supports stage scoring but does not by itself guarantee official final race results or chronology.

### Championship points (04, 22)
Both are arrays, with 58 and 59 rows. Fields include driver_id, membership_id, points_position, points, points_earned_this_race, bonus_points, stage points/winner flags, wins/top-five/top-ten/poles and delta fields. In these captures series_id, race_id and run_id are all zero. membership_id is a separate namespace. Presence of fields does not establish championship calculation rules or the event being scored. Do not infer current-series championship movement from these anonymous global rows. 04 has is_fastest_lap_point, absent in legacy 22.

### Historical statistics (13–17, 19–20)
13 wraps weekend_race and weekend_runs. Race 5392 is a 2024 Cup event at track 14. weekend_race[].results includes driver_id, result_id, finishing/starting positions, team identifiers, laps and points; caution_segments, race_leaders, stage_results, pit_reports and schedule are separately nested. weekend_runs expose weekend_run_id versus timing_run_id, and nested result run_id. Those IDs must not be equated with each other or with race_id. See verified_relationships.json for observed values and join checks.

14 wraps laps and flags. laps[] uses NASCARDriverID and Laps[] with Lap, LapTime, LapSpeed and RunningPos. LapSpeed is a string when populated, not uniformly numeric; lap-zero LapTime/LapSpeed are null. flags has per-lap LapsCompleted and FlagState. 15 stores lap notes under laps, an OBJECT with numeric string lap keys, not an array. Each lap maps to notes with FlagState, Note, NoteID and DriverIDs array. DriverIDs may repeat within a note. These notes lack enough event context to prove all commentary matches the path race, so retain provenance rather than infer identity from car references.

16 is an array of race objects with driver statistical rows (start_ps, mid_ps, ps, closing_ps, best_ps, worst_ps, avg_ps, passing metrics, fast_laps, top15_laps, lead_laps, laps, rating). Field names suggest interpretations but rating/closing-window formulas and units remain undocumented. Numeric 5392 race context matches 13, 19 and 20. 17 is an array of session objects with Title and Items, whereas legacy 24 is a direct array of driver average rows. Con5Lap through Con30Lap and their ranks contain 999 paired with null ranks; treat as likely unavailable comparisons pending confirmation. These are candidate long-run pace inputs, not a validated tire strategy model.

20 SnappyTV is metadata with event 5392, tracks object keyed by numeric strings, nested media descriptors, nullable properties, tags and integer created_at/updated_at values. Values of the timestamp magnitude are consistent with epoch milliseconds (inference, not an API contract). No videos/images were fetched or included; successful metadata access grants no playback permission.

### Legacy and empty responses (21–28)
21 returns the main live-feed object shape for race 5170, with different embedded pit fields from 01. 22 and 23 are points and pit arrays; successful retrieval proves archived availability only. 24 differs from 17 as described above. 25 driver-recap returned status 200, message 'Successfully invoked feed: articles', response.news.article: []. This verifies only an empty article envelope, not a driver recap schema. 26–28 require a signed-access parameter/cookie according to their 403 XML. They remain excluded and no authentication workaround was attempted.

### Universal parser guidance
Use exact source field casing, preserve identifier namespaces and string car numbers, and tolerate extra/missing/null fields and integer/float variation. A single snapshot cannot establish required fields, update cadence, enum meanings, all optional fields, finality, units or live transitions. Redacted samples are structural aids only: placeholders destroy value semantics, date formats and ID joins. Use profiles and observed relationships to write parsers; obtain approved original captures for replay tests, timing validation and event deduplication before claiming production readiness.

### Computed identifier and relationship checks

The following JSON is an actual computed comparison of captured identifiers, not an illustrative fixture. Empty unmatched-ID lists mean all IDs checked in that comparison were found. They do not establish universal completeness.

```json
{
  "09_schedule_to_06": {
    "rows": 111,
    "unmatched_race_ids": [
      5696
    ],
    "unmatched_track_ids": []
  },
  "10_schedule_to_06": {
    "rows": 91,
    "unmatched_race_ids": [],
    "unmatched_track_ids": []
  },
  "11_schedule_to_06": {
    "rows": 72,
    "unmatched_race_ids": [],
    "unmatched_track_ids": []
  },
  "06_series_1_equals_12": true,
  "01_driver_to_07": {
    "total": 37,
    "unmatched_driver_ids": []
  },
  "01_race_in_06": true,
  "01_track_in_08": true,
  "historical_driver_sets": {
    "13_results_count": 36,
    "14_lap_driver_count": 36,
    "14_missing_from_results": [],
    "16_missing_from_results": [],
    "19_missing_from_results": []
  },
  "historical_race_context": {
    "13": 5392,
    "16": 5392,
    "19": [
      5392
    ],
    "20_event": 5392
  },
  "session_identity": {
    "13_race_timing_run_id": 10,
    "13_runs": [
      {
        "weekend_run_id": 5497,
        "timing_run_id": 6,
        "race_id": 5392,
        "run_type": 1
      },
      {
        "weekend_run_id": 5498,
        "timing_run_id": 9,
        "race_id": 5392,
        "run_type": 2
      }
    ],
    "19_stage_run_ids": [
      10
    ]
  },
  "live_context": {
    "01": {
      "race_id": 5633,
      "series_id": 1,
      "run_id": 8,
      "run_type": 3,
      "flag_state": 9,
      "time_of_day_os": "2026-10-21T04:04:25.0191231-07:00"
    },
    "04_context_values": {
      "race_id": [
        0
      ],
      "series_id": [
        0
      ],
      "run_id": [
        0
      ]
    },
    "05_race_ids": [
      5168
    ]
  }
}
```


## Phase compatibility


The brief defines PR 1–6 and feature groups but does not define Phase 3A, 3B or 3C. The mappings below are provisional capability groupings, not a claim about the repository roadmap. Confirm phase definitions in the development project.

| Phase | Provisional scope | Useful verified endpoint IDs | Evidence and remaining gates |
|---|---|---|---|
| 1 | Foundation, schedule, basic status/flags | 01,02,06,08–12 | Structures captured; timestamps and code semantics need contract validation. Data rights unresolved. |
| 2 | Multi-series schedules/calendars, driver selection | 06–12 | Three series schedules and reference namespaces observed; UTC strings lack explicit offset, seasonal rollover and rescheduling behavior untested. |
| 3A | Live leaderboard and lifecycle | 01–02,21 | Positions, lap metrics, stage context and flags observed; no active-session replay or concurrent-series validation; global-feed context inconsistent. |
| 3B | Pits, stage points, championship movement/events | 03–05,18–19,22–23 | Structures usable as parser references; stage/global race mismatch, points zero IDs and context-free pit rows prevent safe automatic joins. Event transitions and official scoring remain unverified. |
| 3C | Historical analytics and comparisons | 13–17,19,24 | Historical results/laps/loop statistics/averages verified structurally; numeric strings, sentinels and session namespaces need normalization. Derived metrics need validation. |

Driver recap 25 provides no populated recap schema. SnappyTV 20 is optional metadata only. Drive 26–28 is access-controlled and outside core scope. No phase is declared release-ready from one snapshot. This package does not validate Home Assistant runtime behavior or HACS checks.


## Discrepancies and prior-assumption limits


No repository schemas or synthetic fixtures were attached, so a field-by-field diff against the earlier 91 synthetic paths is unavailable. Do not claim those assumptions were verified or corrected. The source brief provides feature wishes rather than a concrete response schema. The following are comparisons against its access observations and implementation expectations:

* Owner reported 24 working and four error/login URLs. Here those 24 returned populated JSON, driver recap returned an empty successful article envelope, and only the three Drive endpoints returned HTTP 403. These results are time/network specific.
* Prior conversation reported proxy CONNECT 403 for all URLs. That is not the result in this run: 25 origin-path HTTP 200 JSON responses and three MissingKey XML responses were observed.
* Global feeds do not share verified event context: leaderboard race 5633 versus stages 5168; points series/race/run IDs zero. HTTP success does not establish coherent current race data.
* Historical and live field shapes differ: numeric versus string lap speed, differing driver identity spellings, misspelled embedded pit positions_gained_lossed, and differing average-lap wrappers.
* Schedule strings do not carry timezone offsets, even *_utc. Live time_of_day_os does. Numeric time_of_day must not be assumed epoch seconds.
* Schedule/reference data and a driver directory are present, but team/manufacturer display values, car numbers and annotated names must not substitute for stable identity.
* 999 lap-average values, null ranks and -1 pit durations need unknown/sentinel handling; default zero conversion would fabricate facts.
* Exact Phase 3A/3B/3C definitions are absent from the attached brief; compatibility mapping is provisional.


## Complete endpoint and field dictionary

Every observed field path appears below. `$` means the response root; `[]` means an array item. Numeric-string object keys remain literal paths. **Types and counts are verified observations; field names alone do not verify semantics or units.** Missing counts are measured across observed parent objects, not across time. Zero missing does not prove requiredness. Null and empty-string counts are separate. Empty-array item types remain unknown. Integer/number variation describes source representations. General field semantics remain unknown unless explicitly discussed in the findings or per-endpoint note.

## Endpoint 01

**Live leaderboard and session**

- URL: [https://cf.nascar.com/live/feeds/live-feed.json](https://cf.nascar.com/live/feeds/live-feed.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:40.840243+00:00`
- HTTP: 200; source response size: 94832 bytes.
- Verified interpretation / limitation: Race context is explicit, but this snapshot is at zero laps remaining; it does not validate active-session transitions.
- [Request evidence](Documentation/01_request_evidence.json)
- [Structural sample](01_Live_Race_Data/01_live-feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.lap_number` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.elapsed_time` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.flag_state` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.race_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps_in_race` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps_to_go` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles` | array: 1 | 0 | 0 | 0 | array length [37, 37] |
| `$.vehicles[]` | object: 37 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].average_restart_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].average_running_position` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].average_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_manufacturer` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_number` | string: 37 | 0 | 0 | 0 | numeric string: 37 |
| `$.vehicles[].driver` | object: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.driver_id` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.full_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.first_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.last_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.is_in_chase` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_elapsed_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].fastest_laps_run` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_position_improved` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_completed` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_led` | array: 37 | 0 | 0 | 0 | array length [0, 6] |
| `$.vehicles[].laps_led[]` | object: 22 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].laps_led[].start_lap` | integer: 22 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_led[].end_lap` | integer: 22 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].last_lap_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].last_lap_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].passes_made` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].passing_differential` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].position_differential_last_10_percent` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops` | array: 37 | 0 | 0 | 0 | array length [5, 11] |
| `$.vehicles[].pit_stops[]` | object: 374 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].positions_gained_lossed` | integer: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_elapsed_time` | number: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_lap_count` | integer: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_leader_lap` | integer: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_out_elapsed_time` | number: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_rank` | integer: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_out_rank` | integer: 374 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].qualifying_status` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].running_position` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].status` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].delta` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].sponsor_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].starting_position` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].times_passed` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].quality_passes` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].is_on_track` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].is_on_dvp` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.time_of_day` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.time_of_day_os` | string: 1 | 0 | 0 | 0 | ISO-like datetime with offset: 1 |
| `$.track_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.track_length` | number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.track_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_type` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_caution_segments` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_caution_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_lead_changes` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_leaders` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.avg_diff_1to3` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.stage_num` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.finish_at_lap` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.laps_in_stage` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 02

**Live flag history**

- URL: [https://cf.nascar.com/live/feeds/live-flag-data.json](https://cf.nascar.com/live/feeds/live-flag-data.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:40.840679+00:00`
- HTTP: 200; source response size: 2586 bytes.
- Verified interpretation / limitation: No explicit race context. Nullable comment and beneficiary. Numeric flag meanings remain unverified.
- [Request evidence](Documentation/02_request_evidence.json)
- [Structural sample](01_Live_Race_Data/02_live-flag-data.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [15, 15] |
| `$[]` | object: 15 | 0 | n/a | 0 | Not established / not applicable |
| `$[].lap_number` | integer: 15 | 0 | 0 | 0 | Not established / not applicable |
| `$[].flag_state` | integer: 15 | 0 | 0 | 0 | Not established / not applicable |
| `$[].elapsed_time` | number: 15 | 0 | 0 | 0 | Not established / not applicable |
| `$[].comment` | null: 9, string: 6 | 9 | 0 | 0 | Not established / not applicable |
| `$[].beneficiary` | null: 9, string: 6 | 9 | 0 | 0 | Not established / not applicable |
| `$[].time_of_day` | number: 15 | 0 | 0 | 0 | Not established / not applicable |
| `$[].time_of_day_os` | string: 15 | 0 | 0 | 0 | ISO-like datetime with offset: 15 |

## Endpoint 03

**Live pit stops**

- URL: [https://cf.nascar.com/live/feeds/live-pit-data.json](https://cf.nascar.com/live/feeds/live-pit-data.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:43.802031+00:00`
- HTTP: 200; source response size: 222128 bytes.
- Verified interpretation / limitation: No driver ID or race ID in the pit rows. Join by car number only within a separately validated event context.
- [Request evidence](Documentation/03_request_evidence.json)
- [Structural sample](04_Pit_Stops_and_Stages/03_live-pit-data.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [337, 337] |
| `$[]` | object: 337 | 0 | n/a | 0 | Not established / not applicable |
| `$[].vehicle_number` | string: 337 | 0 | 0 | 0 | numeric string: 337 |
| `$[].driver_name` | string: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].vehicle_manufacturer` | string: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].leader_lap` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].lap_count` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_flag_status` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_flag_status` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_race_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_race_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].total_duration` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_stop_race_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_leave_race_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_duration` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].in_travel_duration` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].out_travel_duration` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_type` | string: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_front_tire_changed` | boolean: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_rear_tire_changed` | boolean: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_front_tire_changed` | boolean: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_rear_tire_changed` | boolean: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].previous_lap_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].next_lap_time` | number: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_rank` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_rank` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |
| `$[].positions_gained_lost` | integer: 337 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 04

**Live championship points**

- URL: [https://cf.nascar.com/live/feeds/live-points.json](https://cf.nascar.com/live/feeds/live-points.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:43.904740+00:00`
- HTTP: 200; source response size: 29872 bytes.
- Verified interpretation / limitation: Observed race, series and run IDs are zero. Do not attach these points to the current leaderboard without verification.
- [Request evidence](Documentation/04_request_evidence.json)
- [Structural sample](05_Points_and_Standings/04_live-points.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [58, 58] |
| `$[]` | object: 58 | 0 | n/a | 0 | Not established / not applicable |
| `$[].bonus_points` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].car_number` | string: 58 | 0 | 0 | 21 | numeric string: 37 |
| `$[].delta_leader` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].delta_next` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].first_name` | string: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].driver_id` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_in_chase` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_points_eligible` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_fastest_lap_point` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_rookie` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].last_name` | string: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].membership_id` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points_position` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points_earned_this_race` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_1_points` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_1_winner` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_2_points` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_2_winner` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_3_points` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_3_winner` | boolean: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].wins` | integer: 55, string: 3 | 0 | 0 | 0 | numeric string: 3 |
| `$[].top_5` | integer: 55, string: 3 | 0 | 0 | 0 | numeric string: 3 |
| `$[].top_10` | integer: 55, string: 3 | 0 | 0 | 0 | numeric string: 3 |
| `$[].poles` | integer: 55, string: 3 | 0 | 0 | 0 | numeric string: 3 |
| `$[].series_id` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_id` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_id` | integer: 58 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 05

**Live stage points**

- URL: [https://cf.nascar.com/live/feeds/live-stage-points.json](https://cf.nascar.com/live/feeds/live-stage-points.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:46.822138+00:00`
- HTTP: 200; source response size: 8950 bytes.
- Verified interpretation / limitation: Observed race 5168 differs from leaderboard race 5633.
- [Request evidence](Documentation/05_request_evidence.json)
- [Structural sample](04_Pit_Stops_and_Stages/05_live-stage-points.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [2, 2] |
| `$[]` | object: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$[].race_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_number` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results` | array: 2 | 0 | 0 | 0 | array length [36, 36] |
| `$[].results[]` | object: 72 | 0 | n/a | 0 | Not established / not applicable |
| `$[].results[].position` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].vehicle_number` | string: 72 | 0 | 0 | 0 | numeric string: 72 |
| `$[].results[].driver_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].full_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].stage_points` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 06

**Combined season race list**

- URL: [https://cf.nascar.com/cacher/2026/race_list_basic.json](https://cf.nascar.com/cacher/2026/race_list_basic.json)
- Parameters: season=2026. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:46.904987+00:00`
- HTTP: 200; source response size: 267292 bytes.
- Verified interpretation / limitation: Contains series_1, series_2 and series_3 arrays. Cup schedule race 5696 is absent here.
- [Request evidence](Documentation/06_request_evidence.json)
- [Structural sample](02_Schedules/06_race_list_basic.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_2` | array: 1 | 0 | 0 | 0 | array length [33, 33] |
| `$.series_2[]` | object: 33 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_2[].race_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].series_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].race_season` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].race_name` | string: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].race_type_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].restrictor_plate` | boolean: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].track_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].track_name` | string: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].date_scheduled` | string: 33 | 0 | 0 | 0 | ISO-like datetime without offset: 33 |
| `$.series_2[].race_date` | string: 33 | 0 | 0 | 0 | ISO-like datetime without offset: 33 |
| `$.series_2[].qualifying_date` | string: 33 | 0 | 0 | 0 | ISO-like datetime without offset: 33 |
| `$.series_2[].tunein_date` | string: 33 | 0 | 0 | 0 | ISO-like datetime without offset: 33 |
| `$.series_2[].scheduled_distance` | integer: 19, number: 14 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].actual_distance` | integer: 15, number: 18 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].scheduled_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].actual_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].stage_1_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].stage_2_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].stage_3_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].number_of_cars_in_field` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].pole_winner_driver_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].pole_winner_speed` | number: 22, integer: 11 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].number_of_lead_changes` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].number_of_leaders` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].number_of_cautions` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].number_of_caution_laps` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].average_speed` | number: 30, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].total_race_time` | string: 33 | 0 | 0 | 3 | clock/duration string: 30 |
| `$.series_2[].margin_of_victory` | string: 33 | 0 | 0 | 3 | numeric string: 19 |
| `$.series_2[].race_purse` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].race_comments` | string: 33 | 0 | 0 | 3 | Not established / not applicable |
| `$.series_2[].attendance` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].infractions` | array: 33 | 0 | 0 | 0 | array length [0, 0] |
| `$.series_2[].schedule` | array: 33 | 0 | 0 | 0 | array length [9, 14] |
| `$.series_2[].schedule[]` | object: 362 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_2[].schedule[].event_name` | string: 362 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].schedule[].notes` | string: 362 | 0 | 0 | 92 | Not established / not applicable |
| `$.series_2[].schedule[].start_time_utc` | string: 362 | 0 | 0 | 0 | ISO-like datetime without offset: 362 |
| `$.series_2[].schedule[].run_type` | integer: 362 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].radio_broadcaster` | string: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].television_broadcaster` | string: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].satellite_radio_broadcaster` | string: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].master_race_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].inspection_complete` | boolean: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].playoff_round` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].is_qualifying_race` | boolean: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].qualifying_race_no` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].qualifying_race_id` | integer: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].has_qualifying` | boolean: 33 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_2[].winner_driver_id` | integer: 30, null: 3 | 3 | 0 | 0 | Not established / not applicable |
| `$.series_2[].pole_winner_laptime` | null: 33 | 33 | 0 | 0 | Not established / not applicable |
| `$.series_3` | array: 1 | 0 | 0 | 0 | array length [25, 25] |
| `$.series_3[]` | object: 25 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_3[].race_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].series_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].race_season` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].race_name` | string: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].race_type_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].restrictor_plate` | boolean: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].track_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].track_name` | string: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].date_scheduled` | string: 25 | 0 | 0 | 0 | ISO-like datetime without offset: 25 |
| `$.series_3[].race_date` | string: 25 | 0 | 0 | 0 | ISO-like datetime without offset: 25 |
| `$.series_3[].qualifying_date` | string: 25 | 0 | 0 | 0 | ISO-like datetime without offset: 25 |
| `$.series_3[].tunein_date` | string: 25 | 0 | 0 | 0 | ISO-like datetime without offset: 25 |
| `$.series_3[].scheduled_distance` | integer: 11, number: 14 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].actual_distance` | integer: 11, number: 14 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].scheduled_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].actual_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].stage_1_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].stage_2_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].stage_3_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].number_of_cars_in_field` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].pole_winner_driver_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].pole_winner_speed` | number: 17, integer: 8 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].number_of_lead_changes` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].number_of_leaders` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].number_of_cautions` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].number_of_caution_laps` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].average_speed` | number: 22, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].total_race_time` | string: 25 | 0 | 0 | 3 | clock/duration string: 22 |
| `$.series_3[].margin_of_victory` | string: 25 | 0 | 0 | 3 | numeric string: 18 |
| `$.series_3[].race_purse` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].race_comments` | string: 25 | 0 | 0 | 3 | Not established / not applicable |
| `$.series_3[].attendance` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].infractions` | array: 25 | 0 | 0 | 0 | array length [0, 0] |
| `$.series_3[].schedule` | array: 25 | 0 | 0 | 0 | array length [10, 18] |
| `$.series_3[].schedule[]` | object: 297 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_3[].schedule[].event_name` | string: 297 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].schedule[].notes` | string: 297 | 0 | 0 | 82 | Not established / not applicable |
| `$.series_3[].schedule[].start_time_utc` | string: 297 | 0 | 0 | 0 | ISO-like datetime without offset: 297 |
| `$.series_3[].schedule[].run_type` | integer: 297 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].radio_broadcaster` | string: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].television_broadcaster` | string: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].satellite_radio_broadcaster` | string: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].master_race_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].inspection_complete` | boolean: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].playoff_round` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].is_qualifying_race` | boolean: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].qualifying_race_no` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].qualifying_race_id` | integer: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].has_qualifying` | boolean: 25 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_3[].winner_driver_id` | integer: 22, null: 3 | 3 | 0 | 0 | Not established / not applicable |
| `$.series_3[].pole_winner_laptime` | null: 25 | 25 | 0 | 0 | Not established / not applicable |
| `$.series_1` | array: 1 | 0 | 0 | 0 | array length [40, 40] |
| `$.series_1[]` | object: 40 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_1[].race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].series_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].race_season` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].race_name` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].race_type_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].restrictor_plate` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].track_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].track_name` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].date_scheduled` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$.series_1[].race_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$.series_1[].qualifying_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$.series_1[].tunein_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$.series_1[].scheduled_distance` | number: 21, integer: 19 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].actual_distance` | integer: 17, number: 23 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].scheduled_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].actual_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].stage_1_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].stage_2_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].stage_3_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].number_of_cars_in_field` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].pole_winner_driver_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].pole_winner_speed` | number: 24, integer: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].number_of_lead_changes` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].number_of_leaders` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].number_of_cautions` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].number_of_caution_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].average_speed` | number: 37, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].total_race_time` | string: 40 | 0 | 0 | 3 | clock/duration string: 37 |
| `$.series_1[].margin_of_victory` | string: 40 | 0 | 0 | 3 | numeric string: 13 |
| `$.series_1[].race_purse` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].race_comments` | string: 40 | 0 | 0 | 3 | Not established / not applicable |
| `$.series_1[].attendance` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].infractions` | array: 40 | 0 | 0 | 0 | array length [0, 0] |
| `$.series_1[].schedule` | array: 40 | 0 | 0 | 0 | array length [3, 21] |
| `$.series_1[].schedule[]` | object: 498 | 0 | n/a | 0 | Not established / not applicable |
| `$.series_1[].schedule[].event_name` | string: 498 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].schedule[].notes` | string: 498 | 0 | 0 | 161 | Not established / not applicable |
| `$.series_1[].schedule[].start_time_utc` | string: 498 | 0 | 0 | 0 | ISO-like datetime without offset: 498 |
| `$.series_1[].schedule[].run_type` | integer: 498 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].radio_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].television_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].satellite_radio_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].master_race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].inspection_complete` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].playoff_round` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].is_qualifying_race` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].qualifying_race_no` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].qualifying_race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].has_qualifying` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_1[].winner_driver_id` | integer: 37, null: 3 | 3 | 0 | 0 | Not established / not applicable |
| `$.series_1[].pole_winner_laptime` | null: 40 | 40 | 0 | 0 | Not established / not applicable |

## Endpoint 07

**Driver directory**

- URL: [https://cf.nascar.com/cacher/drivers.json](https://cf.nascar.com/cacher/drivers.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:49.283054+00:00`
- HTTP: 200; source response size: 1385555 bytes.
- Verified interpretation / limitation: Join Nascar_Driver_ID to timing driver IDs. Driver_ID is a separate namespace. Asset URLs are redacted.
- [Request evidence](Documentation/07_request_evidence.json)
- [Structural sample](03_Drivers_and_Tracks/07_drivers.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.status` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.message` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.response` | array: 1 | 0 | 0 | 0 | array length [915, 915] |
| `$.response[]` | object: 915 | 0 | n/a | 0 | Not established / not applicable |
| `$.response[].Nascar_Driver_ID` | integer: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Driver_ID` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Driver_Series` | string: 915 | 0 | 0 | 6 | Not established / not applicable |
| `$.response[].First_Name` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Last_Name` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Full_Name` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Series_Logo` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Short_Name` | string: 915 | 0 | 0 | 915 | Not established / not applicable |
| `$.response[].Description` | string: 915 | 0 | 0 | 915 | Not established / not applicable |
| `$.response[].DOB` | string: 915 | 0 | 0 | 706 | ISO-like datetime without offset: 209 |
| `$.response[].DOD` | string: 915 | 0 | 0 | 0 | ISO-like datetime without offset: 915 |
| `$.response[].Hometown_City` | string: 915 | 0 | 0 | 797 | Not established / not applicable |
| `$.response[].Crew_Chief` | string: 915 | 0 | 0 | 795 | Not established / not applicable |
| `$.response[].Hometown_State` | string: 915 | 0 | 0 | 802 | Not established / not applicable |
| `$.response[].Hometown_Country` | string: 915 | 0 | 0 | 797 | Not established / not applicable |
| `$.response[].Rookie_Year_Series_1` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Rookie_Year_Series_2` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Rookie_Year_Series_3` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Hobbies` | string: 915 | 0 | 0 | 895 | Not established / not applicable |
| `$.response[].Children` | string: 915 | 0 | 0 | 911 | Not established / not applicable |
| `$.response[].Twitter_Handle` | string: 915 | 0 | 0 | 868 | Not established / not applicable |
| `$.response[].Residing_City` | string: 915 | 0 | 0 | 892 | Not established / not applicable |
| `$.response[].Residing_State` | string: 915 | 0 | 0 | 893 | Not established / not applicable |
| `$.response[].Residing_Country` | string: 915 | 0 | 0 | 892 | Not established / not applicable |
| `$.response[].Badge` | string: 915 | 0 | 0 | 16 | numeric string: 899 |
| `$.response[].Badge_Image` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Manufacturer` | string: 915 | 0 | 0 | 641 | Not established / not applicable |
| `$.response[].Manufacturer_Small` | string: 915 | 0 | 0 | 641 | Not established / not applicable |
| `$.response[].Team` | string: 915 | 0 | 0 | 49 | numeric string: 653 |
| `$.response[].Image` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Image_Small` | string: 915 | 0 | 0 | 674 | Not established / not applicable |
| `$.response[].Image_Transparent` | string: 915 | 0 | 0 | 915 | Not established / not applicable |
| `$.response[].SecondaryImage` | string: 915 | 0 | 0 | 914 | Not established / not applicable |
| `$.response[].Firesuit_Image` | string: 915 | 0 | 0 | 765 | Not established / not applicable |
| `$.response[].Firesuit_Image_Small` | string: 915 | 0 | 0 | 765 | Not established / not applicable |
| `$.response[].Career_Stats` | string: 915 | 0 | 0 | 915 | Not established / not applicable |
| `$.response[].Driver_Page` | string: 915 | 0 | 0 | 819 | Not established / not applicable |
| `$.response[].Age` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Rank` | integer: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Points` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Points_Behind` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].No_Wins` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Poles` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Top5` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Top10` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Laps_Led` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Stage_Wins` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Playoff_Points` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Playoff_Rank` | string: 915 | 0 | 0 | 0 | numeric string: 915 |
| `$.response[].Integrated_Sponsor_Name` | string: 915 | 0 | 0 | 910 | Not established / not applicable |
| `$.response[].Integrated_Sponsor` | string: 915 | 0 | 0 | 910 | Not established / not applicable |
| `$.response[].Integrated_Sponsor_URL` | string: 915 | 0 | 0 | 910 | Not established / not applicable |
| `$.response[].Silly_Season_Change` | string: 915 | 0 | 0 | 908 | Not established / not applicable |
| `$.response[].Silly_Season_Change_Description` | string: 915 | 0 | 0 | 911 | Not established / not applicable |
| `$.response[].Driver_Post_Status` | string: 915 | 0 | 0 | 0 | Not established / not applicable |
| `$.response[].Driver_Part_Time` | string: 915 | 0 | 0 | 776 | Not established / not applicable |

## Endpoint 08

**Track directory**

- URL: [https://cf.nascar.com/cacher/tracks.json](https://cf.nascar.com/cacher/tracks.json)
- Parameters: No path selectors. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:49.312995+00:00`
- HTTP: 200; source response size: 54726 bytes.
- Verified interpretation / limitation: items wrapper. All schedule track IDs match the directory in this capture. Media was not downloaded.
- [Request evidence](Documentation/08_request_evidence.json)
- [Structural sample](03_Drivers_and_Tracks/08_tracks.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.items` | array: 1 | 0 | 0 | 0 | array length [49, 49] |
| `$.items[]` | object: 49 | 0 | n/a | 0 | Not established / not applicable |
| `$.items[].track_id` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_name` | string: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_surface` | string: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_type` | string: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_banking` | string: 49 | 0 | 0 | 12 | Not established / not applicable |
| `$.items[].year_built` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_description` | string: 49 | 0 | 0 | 14 | Not established / not applicable |
| `$.items[].city` | string: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].state` | string: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].frontstretch_length` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].backstretch_length` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].seating_capacity` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_owner` | string: 46, null: 3 | 3 | 0 | 0 | Not established / not applicable |
| `$.items[].races` | null: 49 | 49 | 0 | 0 | Not established / not applicable |
| `$.items[].length` | number: 46, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].zip` | string: 49 | 0 | 0 | 8 | numeric string: 37 |
| `$.items[].address` | string: 49 | 0 | 0 | 10 | Not established / not applicable |
| `$.items[].caution_car_speed` | integer: 49 | 0 | 0 | 0 | Not established / not applicable |
| `$.items[].track_image` | string: 47 | 0 | 2 | 0 | Not established / not applicable |
| `$.items[].track_image_thumbnail` | string: 47 | 0 | 2 | 0 | Not established / not applicable |
| `$.items[].track_logo` | string: 48 | 0 | 1 | 0 | Not established / not applicable |
| `$.items[].track_major_events` | string: 36 | 0 | 13 | 0 | Not established / not applicable |
| `$.items[].track_num_turns` | string: 36 | 0 | 13 | 0 | numeric string: 36 |
| `$.items[].capacity` | string: 36 | 0 | 13 | 0 | Not established / not applicable |
| `$.items[].tickets_url` | string: 44 | 0 | 5 | 0 | Not established / not applicable |
| `$.items[].tickets_url_new_window` | boolean: 44 | 0 | 5 | 0 | Not established / not applicable |
| `$.items[].track_url` | string: 48 | 0 | 1 | 0 | Not established / not applicable |
| `$.items[].track_url_new_window` | boolean: 48 | 0 | 1 | 0 | Not established / not applicable |
| `$.items[].hide_track_from_site` | boolean: 48 | 0 | 1 | 0 | Not established / not applicable |
| `$.items[].track_short_name` | string: 1 | 0 | 48 | 0 | Not established / not applicable |

## Endpoint 09

**Cup session schedule**

- URL: [https://cf.nascar.com/cacher/2026/1/schedule-feed.json](https://cf.nascar.com/cacher/2026/1/schedule-feed.json)
- Parameters: season=2026, series=1. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:51.611506+00:00`
- HTTP: 200; source response size: 33759 bytes.
- Verified interpretation / limitation: Contains race 5696, which is absent from combined race list. UTC-suffixed strings still lack explicit offsets.
- [Request evidence](Documentation/09_request_evidence.json)
- [Structural sample](02_Schedules/09_schedule-feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [111, 111] |
| `$[]` | object: 111 | 0 | n/a | 0 | Not established / not applicable |
| `$[].start_time` | string: 111 | 0 | 0 | 0 | ISO-like datetime without offset: 111 |
| `$[].end_time` | string: 111 | 0 | 0 | 0 | ISO-like datetime without offset: 111 |
| `$[].event_name` | string: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_id` | integer: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_id` | integer: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_name` | string: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_name` | string: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].series_id` | integer: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_type` | integer: 111 | 0 | 0 | 0 | Not established / not applicable |
| `$[].start_time_utc` | string: 111 | 0 | 0 | 0 | ISO-like datetime without offset: 111 |
| `$[].end_time_utc` | string: 111 | 0 | 0 | 0 | ISO-like datetime without offset: 111 |

## Endpoint 10

**Series 2 session schedule**

- URL: [https://cf.nascar.com/cacher/2026/2/schedule-feed.json](https://cf.nascar.com/cacher/2026/2/schedule-feed.json)
- Parameters: season=2026, series=2. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:51.729729+00:00`
- HTTP: 200; source response size: 27837 bytes.
- Verified interpretation / limitation: All observed race and track IDs match the combined race list and track directory.
- [Request evidence](Documentation/10_request_evidence.json)
- [Structural sample](02_Schedules/10_schedule-feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [91, 91] |
| `$[]` | object: 91 | 0 | n/a | 0 | Not established / not applicable |
| `$[].start_time` | string: 91 | 0 | 0 | 0 | ISO-like datetime without offset: 91 |
| `$[].end_time` | string: 91 | 0 | 0 | 0 | ISO-like datetime without offset: 91 |
| `$[].event_name` | string: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_id` | integer: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_id` | integer: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_name` | string: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_name` | string: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].series_id` | integer: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_type` | integer: 91 | 0 | 0 | 0 | Not established / not applicable |
| `$[].start_time_utc` | string: 91 | 0 | 0 | 0 | ISO-like datetime without offset: 91 |
| `$[].end_time_utc` | string: 91 | 0 | 0 | 0 | ISO-like datetime without offset: 91 |

## Endpoint 11

**Truck session schedule**

- URL: [https://cf.nascar.com/cacher/2026/3/schedule-feed.json](https://cf.nascar.com/cacher/2026/3/schedule-feed.json)
- Parameters: season=2026, series=3. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:54.348959+00:00`
- HTTP: 200; source response size: 22544 bytes.
- Verified interpretation / limitation: All observed race and track IDs match the combined race list and track directory.
- [Request evidence](Documentation/11_request_evidence.json)
- [Structural sample](02_Schedules/11_schedule-feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [72, 72] |
| `$[]` | object: 72 | 0 | n/a | 0 | Not established / not applicable |
| `$[].start_time` | string: 72 | 0 | 0 | 0 | ISO-like datetime without offset: 72 |
| `$[].end_time` | string: 72 | 0 | 0 | 0 | ISO-like datetime without offset: 72 |
| `$[].event_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].series_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_type` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].start_time_utc` | string: 72 | 0 | 0 | 0 | ISO-like datetime without offset: 72 |
| `$[].end_time_utc` | string: 72 | 0 | 0 | 0 | ISO-like datetime without offset: 72 |

## Endpoint 12

**Cup race list**

- URL: [https://cf.nascar.com/cacher/2026/1/race_list_basic.json](https://cf.nascar.com/cacher/2026/1/race_list_basic.json)
- Parameters: season=2026, series=1. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:54.356484+00:00`
- HTTP: 200; source response size: 111864 bytes.
- Verified interpretation / limitation: Exactly equals series_1 in combined race list for these captures.
- [Request evidence](Documentation/12_request_evidence.json)
- [Structural sample](02_Schedules/12_race_list_basic.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [40, 40] |
| `$[]` | object: 40 | 0 | n/a | 0 | Not established / not applicable |
| `$[].race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].series_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_season` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_name` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_type_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].restrictor_plate` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].track_name` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].date_scheduled` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$[].race_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$[].qualifying_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$[].tunein_date` | string: 40 | 0 | 0 | 0 | ISO-like datetime without offset: 40 |
| `$[].scheduled_distance` | number: 21, integer: 19 | 0 | 0 | 0 | Not established / not applicable |
| `$[].actual_distance` | integer: 17, number: 23 | 0 | 0 | 0 | Not established / not applicable |
| `$[].scheduled_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].actual_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_1_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_2_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_3_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].number_of_cars_in_field` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pole_winner_driver_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pole_winner_speed` | number: 24, integer: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$[].number_of_lead_changes` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].number_of_leaders` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].number_of_cautions` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].number_of_caution_laps` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].average_speed` | number: 37, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$[].total_race_time` | string: 40 | 0 | 0 | 3 | clock/duration string: 37 |
| `$[].margin_of_victory` | string: 40 | 0 | 0 | 3 | numeric string: 13 |
| `$[].race_purse` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_comments` | string: 40 | 0 | 0 | 3 | Not established / not applicable |
| `$[].attendance` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].infractions` | array: 40 | 0 | 0 | 0 | array length [0, 0] |
| `$[].schedule` | array: 40 | 0 | 0 | 0 | array length [3, 21] |
| `$[].schedule[]` | object: 498 | 0 | n/a | 0 | Not established / not applicable |
| `$[].schedule[].event_name` | string: 498 | 0 | 0 | 0 | Not established / not applicable |
| `$[].schedule[].notes` | string: 498 | 0 | 0 | 161 | Not established / not applicable |
| `$[].schedule[].start_time_utc` | string: 498 | 0 | 0 | 0 | ISO-like datetime without offset: 498 |
| `$[].schedule[].run_type` | integer: 498 | 0 | 0 | 0 | Not established / not applicable |
| `$[].radio_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].television_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].satellite_radio_broadcaster` | string: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].master_race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].inspection_complete` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].playoff_round` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_qualifying_race` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].qualifying_race_no` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].qualifying_race_id` | integer: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].has_qualifying` | boolean: 40 | 0 | 0 | 0 | Not established / not applicable |
| `$[].winner_driver_id` | integer: 37, null: 3 | 3 | 0 | 0 | Not established / not applicable |
| `$[].pole_winner_laptime` | null: 40 | 40 | 0 | 0 | Not established / not applicable |

## Endpoint 13

**Historical weekend/results**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json](https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:56.618180+00:00`
- HTTP: 200; source response size: 63624 bytes.
- Verified interpretation / limitation: weekend_run_id and timing_run_id differ. Race results include driver/team identities; nested run results use a run-specific identity.
- [Request evidence](Documentation/13_request_evidence.json)
- [Structural sample](06_Historical_Data/13_weekend-feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.weekend_race[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].race_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].series_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_season` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_type_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].restrictor_plate` | boolean: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].track_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].track_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].date_scheduled` | string: 1 | 0 | 0 | 0 | ISO-like datetime without offset: 1 |
| `$.weekend_race[].race_date` | string: 1 | 0 | 0 | 0 | ISO-like datetime without offset: 1 |
| `$.weekend_race[].qualifying_date` | string: 1 | 0 | 0 | 0 | ISO-like datetime without offset: 1 |
| `$.weekend_race[].tunein_date` | string: 1 | 0 | 0 | 0 | ISO-like datetime without offset: 1 |
| `$.weekend_race[].scheduled_distance` | number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].actual_distance` | number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].scheduled_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].actual_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_1_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_2_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_3_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_4_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].number_of_cars_in_field` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].pole_winner_driver_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].pole_winner_speed` | number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].number_of_lead_changes` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].number_of_leaders` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].number_of_cautions` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].number_of_caution_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].average_speed` | number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].total_race_time` | string: 1 | 0 | 0 | 0 | clock/duration string: 1 |
| `$.weekend_race[].margin_of_victory` | string: 1 | 0 | 0 | 0 | numeric string: 1 |
| `$.weekend_race[].race_purse` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_comments` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].attendance` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results` | array: 1 | 0 | 0 | 0 | array length [36, 36] |
| `$.weekend_race[].results[]` | object: 36 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].results[].result_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].finishing_position` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].starting_position` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].car_number` | string: 36 | 0 | 0 | 0 | numeric string: 36 |
| `$.weekend_race[].results[].driver_fullname` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].driver_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].driver_hometown` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].hometown_city` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].hometown_state` | string: 36 | 0 | 0 | 1 | Not established / not applicable |
| `$.weekend_race[].results[].hometown_country` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].team_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].team_name` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].qualifying_order` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].qualifying_position` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].qualifying_speed` | number: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].laps_led` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].times_led` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].car_make` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].car_model` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].sponsor` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].points_earned` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].playoff_points_earned` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].laps_completed` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].finishing_status` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].winnings` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].series_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].race_season` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].race_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].owner_fullname` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].crew_chief_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].crew_chief_fullname` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].points_position` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].points_delta` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].owner_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].official_car_number` | string: 36 | 0 | 0 | 0 | numeric string: 36 |
| `$.weekend_race[].results[].disqualified` | boolean: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].diff_laps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].diff_time` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].results[].pit_box` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments` | array: 1 | 0 | 0 | 0 | array length [9, 9] |
| `$.weekend_race[].caution_segments[]` | object: 9 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].race_id` | integer: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].start_lap` | integer: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].end_lap` | integer: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].reason` | string: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].comment` | string: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].caution_segments[].beneficiary_car_number` | null: 1, string: 8 | 1 | 0 | 0 | numeric string: 8 |
| `$.weekend_race[].caution_segments[].flag_state` | integer: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_leaders` | array: 1 | 0 | 0 | 0 | array length [55, 55] |
| `$.weekend_race[].race_leaders[]` | object: 55 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].race_leaders[].start_lap` | integer: 55 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_leaders[].end_lap` | integer: 55 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].race_leaders[].car_number` | string: 55 | 0 | 0 | 0 | numeric string: 55 |
| `$.weekend_race[].race_leaders[].race_id` | integer: 55 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].infractions` | array: 1 | 0 | 0 | 0 | array length [0, 0] |
| `$.weekend_race[].schedule` | array: 1 | 0 | 0 | 0 | array length [16, 16] |
| `$.weekend_race[].schedule[]` | object: 16 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].schedule[].event_name` | string: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].schedule[].notes` | string: 16 | 0 | 0 | 6 | Not established / not applicable |
| `$.weekend_race[].schedule[].start_time_utc` | string: 16 | 0 | 0 | 0 | ISO-like datetime without offset: 16 |
| `$.weekend_race[].schedule[].run_type` | integer: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.weekend_race[].stage_results[]` | object: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].stage_number` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].results` | array: 2 | 0 | 0 | 0 | array length [10, 10] |
| `$.weekend_race[].stage_results[].results[]` | object: 20 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].results[].driver_fullname` | string: 20 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].results[].driver_id` | integer: 20 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].results[].car_number` | string: 20 | 0 | 0 | 0 | numeric string: 20 |
| `$.weekend_race[].stage_results[].results[].finishing_position` | integer: 20 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].stage_results[].results[].stage_points` | integer: 20 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].pit_reports` | array: 1 | 0 | 0 | 0 | array length [0, 0] |
| `$.weekend_race[].radio_broadcaster` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].television_broadcaster` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].satellite_radio_broadcaster` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].master_race_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].timing_run_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].inspection_complete` | boolean: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_race[].playoff_round` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.weekend_runs[]` | object: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_runs[].weekend_run_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].race_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].timing_run_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].run_type` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].run_name` | string: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].run_date` | string: 2 | 0 | 0 | 0 | ISO-like datetime without offset: 2 |
| `$.weekend_runs[].run_date_utc` | string: 2 | 0 | 0 | 0 | ISO-like datetime without offset: 2 |
| `$.weekend_runs[].results` | array: 2 | 0 | 0 | 0 | array length [36, 36] |
| `$.weekend_runs[].results[]` | object: 72 | 0 | n/a | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].run_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].car_number` | string: 72 | 0 | 0 | 0 | numeric string: 72 |
| `$.weekend_runs[].results[].vehicle_number` | string: 72 | 0 | 0 | 0 | numeric string: 72 |
| `$.weekend_runs[].results[].manufacturer` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].driver_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].driver_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].finishing_position` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].best_lap_time` | number: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].best_lap_speed` | number: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].best_lap_number` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].laps_completed` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].comment` | string: 72 | 0 | 0 | 72 | Not established / not applicable |
| `$.weekend_runs[].results[].delta_leader` | integer: 2, number: 70 | 0 | 0 | 0 | Not established / not applicable |
| `$.weekend_runs[].results[].disqualified` | boolean: 72 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 14

**Historical lap times**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/lap-times.json](https://cf.nascar.com/cacher/2024/1/5392/lap-times.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:04:56.626063+00:00`
- HTTP: 200; source response size: 1171730 bytes.
- Verified interpretation / limitation: NASCARDriverID spelling; populated LapSpeed is a string. Lap-zero time/speed are null.
- [Request evidence](Documentation/14_request_evidence.json)
- [Structural sample](06_Historical_Data/14_lap-times.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps` | array: 1 | 0 | 0 | 0 | array length [36, 36] |
| `$.laps[]` | object: 36 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps[].Number` | string: 36 | 0 | 0 | 0 | numeric string: 36 |
| `$.laps[].FullName` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps[].Manufacturer` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps[].RunningPos` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps[].NASCARDriverID` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps[].Laps` | array: 36 | 0 | 0 | 0 | array length [193, 501] |
| `$.laps[].Laps[]` | object: 17647 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps[].Laps[].Lap` | integer: 17647 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps[].Laps[].LapTime` | null: 36, number: 17594, integer: 17 | 36 | 0 | 0 | Not established / not applicable |
| `$.laps[].Laps[].LapSpeed` | null: 36, string: 17611 | 36 | 0 | 0 | numeric string: 17611 |
| `$.laps[].Laps[].RunningPos` | integer: 17647 | 0 | 0 | 0 | Not established / not applicable |
| `$.flags` | array: 1 | 0 | 0 | 0 | array length [501, 501] |
| `$.flags[]` | object: 501 | 0 | n/a | 0 | Not established / not applicable |
| `$.flags[].LapsCompleted` | integer: 501 | 0 | 0 | 0 | Not established / not applicable |
| `$.flags[].FlagState` | integer: 501 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 15

**Historical lap notes**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json](https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:00.340888+00:00`
- HTTP: 200; source response size: 11368 bytes.
- Verified interpretation / limitation: laps is an object keyed by numeric strings, not an array. NoteID and DriverIDs are distinct identities. Commentary context still needs validation.
- [Request evidence](Documentation/15_request_evidence.json)
- [Structural sample](06_Historical_Data/15_lap-notes.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.0` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.0[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.0[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.0[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.0[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.0[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.0[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.1` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.1[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.1[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.1[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.1[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.1[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.1[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.3` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.3[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.3[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.3[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.3[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.3[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.3[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.14` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.14[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.14[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.14[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.14[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.14[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.14[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.19` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.19[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.19[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.19[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.19[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.19[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.19[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.20` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.20[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.20[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.20[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.20[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.20[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.20[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.23` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.23[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.23[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.23[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.23[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.23[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.23[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.25` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.25[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.25[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.25[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.25[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.25[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [10, 10] |
| `$.laps.25[].DriverIDs[]` | integer: 10 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.31` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.31[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.31[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.31[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.31[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.31[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [9, 9] |
| `$.laps.31[].DriverIDs[]` | integer: 9 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.33` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.33[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.33[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.33[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.33[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.33[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.33[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.39` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.39[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.39[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.39[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.39[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.39[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.39[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.41` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.41[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.41[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.41[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.41[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.41[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.41[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.53` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.53[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.53[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.53[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.53[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.53[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.53[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.54` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.54[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.54[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.54[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.54[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.54[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.54[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.61` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.61[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.61[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.61[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.61[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.61[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.61[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.62` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.62[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.62[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.62[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.62[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.62[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.62[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.65` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.65[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.65[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.65[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.65[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.65[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.65[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.68` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.68[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.68[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.68[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.68[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.68[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.68[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.70` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.70[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.70[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.70[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.70[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.70[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.70[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.71` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.71[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.71[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.71[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.71[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.71[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.71[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.74` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.74[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.74[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.74[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.74[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.74[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.74[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.80` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.80[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.80[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.80[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.80[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.80[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.80[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.83` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.83[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.83[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.83[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.83[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.83[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.83[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.89` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.89[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.89[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.89[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.89[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.89[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.89[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.107` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.107[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.107[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.107[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.107[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.107[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.107[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.111` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.111[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.111[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.111[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.111[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.111[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.111[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.116` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.116[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.116[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.116[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.116[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.116[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.116[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.120` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.120[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.120[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.120[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.120[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.120[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.120[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.124` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.124[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.124[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.124[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.124[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.124[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.124[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.125` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.125[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.125[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.125[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.125[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.125[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.125[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.130` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.130[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.130[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.130[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.130[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.130[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.130[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.131` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.131[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.131[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.131[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.131[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.131[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.131[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.141` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.141[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.141[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.141[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.141[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.141[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [5, 5] |
| `$.laps.141[].DriverIDs[]` | integer: 5 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.146` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.146[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.146[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.146[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.146[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.146[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.146[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.150` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.150[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.150[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.150[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.150[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.150[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.150[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.154` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.154[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.154[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.154[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.154[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.154[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.154[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.157` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.157[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.157[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.157[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.157[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.157[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.157[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.159` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.159[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.159[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.159[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.159[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.159[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.159[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.171` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.171[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.171[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.171[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.171[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.171[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.171[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.176` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.176[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.176[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.176[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.176[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.176[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [5, 5] |
| `$.laps.176[].DriverIDs[]` | integer: 5 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.177` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.177[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.177[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.177[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.177[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.177[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.177[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.181` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.181[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.181[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.181[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.181[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.181[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [6, 6] |
| `$.laps.181[].DriverIDs[]` | integer: 6 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.186` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.186[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.186[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.186[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.186[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.186[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.186[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.190` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.190[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.190[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.190[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.190[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.190[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [4, 4] |
| `$.laps.190[].DriverIDs[]` | integer: 4 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.200` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.200[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.200[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.200[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.200[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.200[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.200[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.202` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.202[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.202[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.202[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.202[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.202[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.202[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.206` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.206[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.206[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.206[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.206[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.206[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.206[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.224` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.224[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.224[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.224[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.224[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.224[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.224[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.228` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.228[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.228[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.228[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.228[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.228[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.228[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.229` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.229[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.229[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.229[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.229[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.229[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.229[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.234` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.234[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.234[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.234[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.234[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.234[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [8, 8] |
| `$.laps.234[].DriverIDs[]` | integer: 8 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.240` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.240[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.240[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.240[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.240[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.240[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.240[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.244` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.244[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.244[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.244[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.244[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.244[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.244[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.249` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.249[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.249[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.249[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.249[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.249[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.249[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.251` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.251[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.251[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.251[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.251[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.251[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.251[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.252` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.252[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.252[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.252[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.252[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.252[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.252[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.256` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.256[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.256[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.256[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.256[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.256[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [6, 6] |
| `$.laps.256[].DriverIDs[]` | integer: 6 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.261` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.261[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.261[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.261[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.261[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.261[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [0, 0] |
| `$.laps.265` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.265[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.265[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.265[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.265[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.265[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.265[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.285` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.285[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.285[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.285[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.285[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.285[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.285[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.310` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.310[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.310[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.310[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.310[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.310[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.310[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.311` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.311[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.311[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.311[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.311[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.311[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.311[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.316` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.316[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.316[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.316[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.316[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.316[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [5, 5] |
| `$.laps.316[].DriverIDs[]` | integer: 5 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.323` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.323[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.323[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.323[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.323[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.323[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [5, 5] |
| `$.laps.323[].DriverIDs[]` | integer: 5 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.359` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.359[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.359[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.359[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.359[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.359[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.359[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.361` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.361[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.361[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.361[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.361[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.361[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.361[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.365` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.365[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.365[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.365[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.365[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.365[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.365[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.368` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.368[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.368[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.368[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.368[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.368[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [6, 6] |
| `$.laps.368[].DriverIDs[]` | integer: 6 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.369` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.369[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.369[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.369[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.369[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.369[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.369[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.373` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.373[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.373[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.373[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.373[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.373[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [4, 4] |
| `$.laps.373[].DriverIDs[]` | integer: 4 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.380` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.380[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.380[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.380[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.380[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.380[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.380[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.395` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.395[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.395[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.395[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.395[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.395[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.395[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.399` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.399[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.399[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.399[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.399[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.399[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.399[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.426` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.426[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.426[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.426[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.426[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.426[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.426[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.431` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.431[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.431[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.431[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.431[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.431[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.431[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.435` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.435[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.435[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.435[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.435[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.435[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.435[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.440` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.440[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.440[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.440[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.440[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.440[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.440[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.444` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.444[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.444[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.444[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.444[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.444[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.444[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.446` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.446[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.446[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.446[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.446[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.446[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.446[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.447` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.447[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.447[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.447[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.447[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.447[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.447[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.448` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.448[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.448[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.448[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.448[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.448[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.448[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.449` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.449[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.449[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.449[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.449[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.449[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [3, 3] |
| `$.laps.449[].DriverIDs[]` | integer: 3 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.451` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.451[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.451[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.451[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.451[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.451[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [2, 2] |
| `$.laps.451[].DriverIDs[]` | integer: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.483` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.483[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.483[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.483[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.483[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.483[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.483[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.484` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.484[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.484[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.484[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.484[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.484[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.484[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.500` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.500[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.laps.500[].FlagState` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.500[].Note` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.500[].NoteID` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps.500[].DriverIDs` | array: 1 | 0 | 0 | 0 | array length [1, 1] |
| `$.laps.500[].DriverIDs[]` | integer: 1 | 0 | n/a | 0 | Not established / not applicable |

## Endpoint 16

**Historical loop statistics**

- URL: [https://cf.nascar.com/loopstats/prod/2024/1/5392.json](https://cf.nascar.com/loopstats/prod/2024/1/5392.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:00.464331+00:00`
- HTTP: 200; source response size: 9875 bytes.
- Verified interpretation / limitation: Historical driver IDs match weekend result driver set. Rating and statistical formulas remain undocumented.
- [Request evidence](Documentation/16_request_evidence.json)
- [Structural sample](06_Historical_Data/16_5392.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [1, 1] |
| `$[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$[].race_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].series_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].sch_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].act_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers` | array: 1 | 0 | 0 | 0 | array length [36, 36] |
| `$[].drivers[]` | object: 36 | 0 | n/a | 0 | Not established / not applicable |
| `$[].drivers[].driver_id` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].start_ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].mid_ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].closing_ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].closing_laps_diff` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].best_ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].worst_ps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].avg_ps` | number: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].passes_gf` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].passing_diff` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].passed_gf` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].quality_passes` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].fast_laps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].top15_laps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].lead_laps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].laps` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].drivers[].rating` | number: 36 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 17

**Historical lap averages**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json](https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:02.443947+00:00`
- HTTP: 200; source response size: 15264 bytes.
- Verified interpretation / limitation: Title/Items wrapper. 999 average values paired with null ranks are likely unavailability sentinels, pending confirmation.
- [Request evidence](Documentation/17_request_evidence.json)
- [Structural sample](06_Historical_Data/17_lap-averages.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [1, 1] |
| `$[]` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$[].Title` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items` | array: 1 | 0 | 0 | 0 | array length [36, 36] |
| `$[].Items[]` | object: 36 | 0 | n/a | 0 | Not established / not applicable |
| `$[].Items[].Number` | string: 36 | 0 | 0 | 0 | numeric string: 36 |
| `$[].Items[].NASCARDriverID` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Driver` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].FullName` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Manufacturer` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Sponsor` | string: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].OverAllAvg` | number: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].OverAllAvgRank` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].BestLapTime` | number: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].BestLapRank` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con5Lap` | number: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con5LapRank` | integer: 36 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con10Lap` | number: 27, integer: 9 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con10LapRank` | integer: 27, null: 9 | 9 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con15Lap` | number: 18, integer: 18 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con15LapRank` | integer: 18, null: 18 | 18 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con20Lap` | number: 12, integer: 24 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con20LapRank` | integer: 12, null: 24 | 24 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con25Lap` | number: 6, integer: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con25LapRank` | integer: 6, null: 30 | 30 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con30Lap` | number: 4, integer: 32 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Items[].Con30LapRank` | integer: 4, null: 32 | 32 | 0 | 0 | Not established / not applicable |

## Endpoint 18

**Archived pit stops**

- URL: [https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json](https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json)
- Parameters: season=2026, series=1, race=5626. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:02.468141+00:00`
- HTTP: 200; source response size: 191417 bytes.
- Verified interpretation / limitation: Negative duration/box values and zero-lap entries require sentinel handling. Path race differs from historical Bristol example.
- [Request evidence](Documentation/18_request_evidence.json)
- [Structural sample](04_Pit_Stops_and_Stages/18_live-pit-data.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [300, 300] |
| `$[]` | object: 300 | 0 | n/a | 0 | Not established / not applicable |
| `$[].vehicle_number` | string: 300 | 0 | 0 | 0 | numeric string: 300 |
| `$[].driver_name` | string: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].vehicle_manufacturer` | string: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].leader_lap` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].lap_count` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_flag_status` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_flag_status` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_race_time` | integer: 43, number: 257 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_race_time` | integer: 73, number: 227 | 0 | 0 | 0 | Not established / not applicable |
| `$[].total_duration` | integer: 39, number: 261 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_stop_race_time` | integer: 42, number: 258 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_leave_race_time` | integer: 87, number: 213 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_duration` | integer: 87, number: 213 | 0 | 0 | 0 | Not established / not applicable |
| `$[].in_travel_duration` | integer: 87, number: 213 | 0 | 0 | 0 | Not established / not applicable |
| `$[].out_travel_duration` | integer: 89, number: 211 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_type` | string: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_front_tire_changed` | boolean: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_rear_tire_changed` | boolean: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_front_tire_changed` | boolean: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_rear_tire_changed` | boolean: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].previous_lap_time` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].next_lap_time` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_rank` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_rank` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |
| `$[].positions_gained_lost` | integer: 300 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 19

**Archived stage points**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json](https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:04.562195+00:00`
- HTTP: 200; source response size: 7297 bytes.
- Verified interpretation / limitation: Race 5392 and run 10 agree with historical race timing_run_id. Stage data is not automatically final race results.
- [Request evidence](Documentation/19_request_evidence.json)
- [Structural sample](04_Pit_Stops_and_Stages/19_live-stage-points.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [2, 2] |
| `$[]` | object: 2 | 0 | n/a | 0 | Not established / not applicable |
| `$[].race_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_id` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_number` | integer: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results` | array: 2 | 0 | 0 | 0 | array length [36, 36] |
| `$[].results[]` | object: 72 | 0 | n/a | 0 | Not established / not applicable |
| `$[].results[].position` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].vehicle_number` | string: 72 | 0 | 0 | 0 | numeric string: 72 |
| `$[].results[].driver_id` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].full_name` | string: 72 | 0 | 0 | 0 | Not established / not applicable |
| `$[].results[].stage_points` | integer: 72 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 20

**SnappyTV metadata**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/snappytv.json](https://cf.nascar.com/cacher/2024/1/5392/snappytv.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:04.677765+00:00`
- HTTP: 200; source response size: 16444 bytes.
- Verified interpretation / limitation: Metadata access does not establish playback rights. No media downloaded. Epoch-millisecond interpretation is an inference.
- [Request evidence](Documentation/20_request_evidence.json)
- [Structural sample](06_Historical_Data/20_snappytv.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.event` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.external_id` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.mr` | null: 1 | 1 | 0 | 0 | Not established / not applicable |
| `$.social_volume` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.social_volume.total` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.social_volume.current10` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.social_volume.peak10` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.social_volume.current60` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.social_volume.peak60` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.tracks` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.tracks.0` | array: 1 | 0 | 0 | 0 | array length [16, 16] |
| `$.tracks.0[]` | object: 16 | 0 | n/a | 0 | Not established / not applicable |
| `$.tracks.0[].type` | string: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.tracks.0[].url_spec` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].id` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].title` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].description` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].snaptype` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].thumb_320x180` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].thumb_640x360` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].original_asset_url` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].friendly_id` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].embedable` | boolean: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].embed_code` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].youtube_id` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].twitter_post_id` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].fb_post_id` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].expired` | boolean: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].share_url_full` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].short_url` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].oembed_url_xml` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].tweet_text` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].created_at` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].updated_at` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].duration` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].video_duration` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].event_id` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].hash_tags` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].tags` | array: 8 | 0 | 8 | 0 | array length [5, 6] |
| `$.tracks.0[].tags[]` | string: 47 | 0 | n/a | 0 | Not established / not applicable |
| `$.tracks.0[].tweet_vol` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].trending_score` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].event_episode_title` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].event_episode_subtitle` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].event_time` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].event_duration_in_seconds` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].channel_friendly_name` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].username` | string: 8 | 0 | 8 | 8 | Not established / not applicable |
| `$.tracks.0[].user_avatar_url` | null: 8 | 8 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].show_id` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].show_title` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].featured` | boolean: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].inpoint_percent` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].outpoint_percent` | integer: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].status` | string: 8 | 0 | 8 | 0 | Not established / not applicable |
| `$.tracks.0[].downloads` | array: 8 | 0 | 8 | 0 | array length [4, 4] |
| `$.tracks.0[].downloads[]` | object: 32 | 0 | n/a | 0 | Not established / not applicable |
| `$.tracks.0[].downloads[].resolution` | string: 32 | 0 | 0 | 0 | Not established / not applicable |
| `$.tracks.0[].downloads[].bitrate` | string: 32 | 0 | 0 | 0 | numeric string: 32 |
| `$.tracks.0[].downloads[].url` | string: 32 | 0 | 0 | 0 | Not established / not applicable |
| `$.tracks.1` | array: 1 | 0 | 0 | 0 | array length [0, 0] |
| `$.start_time` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.end_time` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.title` | string: 1 | 0 | 0 | 1 | Not established / not applicable |
| `$.live_enabled` | boolean: 1 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 21

**Legacy leaderboard**

- URL: [https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json](https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json)
- Parameters: series=1, race=5170. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:07.078363+00:00`
- HTTP: 200; source response size: 86726 bytes.
- Verified interpretation / limitation: Archived race 5170 object, not proof of a current live feed. Embedded pit fields differ from current global feed.
- [Request evidence](Documentation/21_request_evidence.json)
- [Structural sample](07_Legacy_and_Unavailable/21_live_feed.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.lap_number` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.elapsed_time` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.flag_state` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.race_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps_in_race` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.laps_to_go` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles` | array: 1 | 0 | 0 | 0 | array length [37, 37] |
| `$.vehicles[]` | object: 37 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].average_restart_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].average_running_position` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].average_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].best_lap_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_manufacturer` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_number` | string: 37 | 0 | 0 | 0 | numeric string: 37 |
| `$.vehicles[].driver` | object: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.driver_id` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.full_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.first_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.last_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].driver.is_in_chase` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].vehicle_elapsed_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].fastest_laps_run` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_position_improved` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_completed` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_led` | array: 37 | 0 | 0 | 0 | array length [0, 3] |
| `$.vehicles[].laps_led[]` | object: 16 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].laps_led[].start_lap` | integer: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].laps_led[].end_lap` | integer: 16 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].last_lap_speed` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].last_lap_time` | number: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].passes_made` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].passing_differential` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].position_differential_last_10_percent` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops` | array: 37 | 0 | 0 | 0 | array length [3, 13] |
| `$.vehicles[].pit_stops[]` | object: 302 | 0 | n/a | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].positions_gained_lossed` | integer: 302 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_elapsed_time` | integer: 90, number: 212 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_lap_count` | integer: 302 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_in_leader_lap` | integer: 302 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_out_elapsed_time` | integer: 92, number: 210 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_stop_type` | string: 302 | 0 | 0 | 123 | Not established / not applicable |
| `$.vehicles[].pit_stops[].pit_stop_duration` | integer: 126, number: 176 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].qualifying_status` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].running_position` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].status` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].delta` | integer: 16, number: 21 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].sponsor_name` | string: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].starting_position` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].times_passed` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].quality_passes` | integer: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].is_on_track` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.vehicles[].is_on_dvp` | boolean: 37 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.series_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.time_of_day` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.time_of_day_os` | string: 1 | 0 | 0 | 0 | ISO-like datetime with offset: 1 |
| `$.track_id` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.track_length` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.track_name` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.run_type` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_caution_segments` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_caution_laps` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_lead_changes` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.number_of_leaders` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.avg_diff_1to3` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.stage_num` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.finish_at_lap` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.stage.laps_in_stage` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 22

**Legacy championship points**

- URL: [https://cf.nascar.com/live/feeds/series_1/5170/live_points.json](https://cf.nascar.com/live/feeds/series_1/5170/live_points.json)
- Parameters: series=1, race=5170. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:07.136687+00:00`
- HTTP: 200; source response size: 28526 bytes.
- Verified interpretation / limitation: Legacy points retain zero series/race/run IDs. is_fastest_lap_point is absent compared with global points.
- [Request evidence](Documentation/22_request_evidence.json)
- [Structural sample](07_Legacy_and_Unavailable/22_live_points.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [59, 59] |
| `$[]` | object: 59 | 0 | n/a | 0 | Not established / not applicable |
| `$[].bonus_points` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].car_number` | string: 59 | 0 | 0 | 22 | numeric string: 37 |
| `$[].delta_leader` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].delta_next` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].first_name` | string: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].driver_id` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_in_chase` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_points_eligible` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].is_rookie` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].last_name` | string: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].membership_id` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points_position` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].points_earned_this_race` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_1_points` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_1_winner` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_2_points` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_2_winner` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_3_points` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].stage_3_winner` | boolean: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].wins` | integer: 58, string: 1 | 0 | 0 | 0 | numeric string: 1 |
| `$[].top_5` | integer: 58, string: 1 | 0 | 0 | 0 | numeric string: 1 |
| `$[].top_10` | integer: 58, string: 1 | 0 | 0 | 0 | numeric string: 1 |
| `$[].poles` | integer: 58, string: 1 | 0 | 0 | 0 | numeric string: 1 |
| `$[].series_id` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].race_id` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |
| `$[].run_id` | integer: 59 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 23

**Legacy pit stops**

- URL: [https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json](https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json)
- Parameters: series=1, race=5170. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:10.340389+00:00`
- HTTP: 200; source response size: 117929 bytes.
- Verified interpretation / limitation: Archived pit rows do not carry an explicit driver ID. Manufacturer representations vary by source.
- [Request evidence](Documentation/23_request_evidence.json)
- [Structural sample](07_Legacy_and_Unavailable/23_live-pit-data.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [180, 180] |
| `$[]` | object: 180 | 0 | n/a | 0 | Not established / not applicable |
| `$[].vehicle_number` | string: 180 | 0 | 0 | 0 | numeric string: 180 |
| `$[].driver_name` | string: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].vehicle_manufacturer` | string: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].leader_lap` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].lap_count` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_flag_status` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_flag_status` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_race_time` | number: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_race_time` | number: 176, integer: 4 | 0 | 0 | 0 | Not established / not applicable |
| `$[].total_duration` | number: 175, integer: 5 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_stop_race_time` | number: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].box_leave_race_time` | number: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_duration` | number: 177, integer: 3 | 0 | 0 | 0 | Not established / not applicable |
| `$[].in_travel_duration` | number: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].out_travel_duration` | number: 176, integer: 4 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_stop_type` | string: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_front_tire_changed` | boolean: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].left_rear_tire_changed` | boolean: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_front_tire_changed` | boolean: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].right_rear_tire_changed` | boolean: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].previous_lap_time` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].next_lap_time` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_in_rank` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].pit_out_rank` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |
| `$[].positions_gained_lost` | integer: 180 | 0 | 0 | 0 | Not established / not applicable |

## Endpoint 24

**Legacy practice averages**

- URL: [https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json](https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json)
- Parameters: season=2019, series=2, race=4817. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:10.450270+00:00`
- HTTP: 200; source response size: 12262 bytes.
- Verified interpretation / limitation: Direct driver array differs from historical Title/Items wrapper. Null ranks and 999 values occur.
- [Request evidence](Documentation/24_request_evidence.json)
- [Structural sample](07_Legacy_and_Unavailable/24_lapAvg_nxs_practice_1.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | array: 1 | 0 | n/a | 0 | array length [30, 30] |
| `$[]` | object: 30 | 0 | n/a | 0 | Not established / not applicable |
| `$[].Number` | string: 30 | 0 | 0 | 0 | numeric string: 30 |
| `$[].NASCARDriverID` | integer: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Driver` | string: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].FullName` | string: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Manufacturer` | string: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Sponsor` | null: 30 | 30 | 0 | 0 | Not established / not applicable |
| `$[].OverAllAvg` | number: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].OverAllAvgRank` | integer: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].BestLapTime` | number: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].BestLapRank` | integer: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con5Lap` | number: 25, integer: 5 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con5LapRank` | integer: 25, null: 5 | 5 | 0 | 0 | Not established / not applicable |
| `$[].Con10Lap` | number: 11, integer: 19 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con10LapRank` | integer: 11, null: 19 | 19 | 0 | 0 | Not established / not applicable |
| `$[].Con15Lap` | integer: 25, number: 5 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con15LapRank` | null: 25, integer: 5 | 25 | 0 | 0 | Not established / not applicable |
| `$[].Con20Lap` | integer: 28, number: 2 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con20LapRank` | null: 28, integer: 2 | 28 | 0 | 0 | Not established / not applicable |
| `$[].Con25Lap` | integer: 29, number: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con25LapRank` | null: 29, integer: 1 | 29 | 0 | 0 | Not established / not applicable |
| `$[].Con30Lap` | integer: 30 | 0 | 0 | 0 | Not established / not applicable |
| `$[].Con30LapRank` | null: 30 | 30 | 0 | 0 | Not established / not applicable |

## Endpoint 25

**Driver recap/article envelope**

- URL: [https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json](https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json)
- Parameters: season=2024, series=1, race=5392. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:12.601320+00:00`
- HTTP: 200; source response size: 97 bytes.
- Verified interpretation / limitation: HTTP 200 but response.news.article is empty. Article item fields and useful recap content remain unknown.
- [Request evidence](Documentation/25_request_evidence.json)
- [Structural sample](07_Legacy_and_Unavailable/25_driver-recap.structural.json)

| Field path | Observed types and counts | Nulls | Missing in parents | Empty strings | Observed formats / array lengths |
|---|---|---:|---:|---:|---|
| `$` | object: 1 | 0 | n/a | 0 | Not established / not applicable |
| `$.status` | integer: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.message` | string: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.response` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.response.news` | object: 1 | 0 | 0 | 0 | Not established / not applicable |
| `$.response.news.article` | array: 1 | 0 | 0 | 0 | array length [0, 0] |

## Endpoint 26

**Series 1 Drive configuration**

- URL: [https://cf.nascar.com/drive/1/configs-ng.json](https://cf.nascar.com/drive/1/configs-ng.json)
- Parameters: series=1. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:12.679819+00:00`
- HTTP: 403; source response size: 146 bytes.
- Verified interpretation / limitation: HTTP 403 MissingKey. No JSON schema verified; no credential discovery or retry.
- [Request evidence](Documentation/26_request_evidence.json)
- [Exact XML failure](07_Legacy_and_Unavailable/26_error.xml)

No verified JSON fields. The 403 XML reports `MissingKey`: `Missing Key-Pair-Id query parameter or cookie value`.

## Endpoint 27

**Series 2 Drive configuration**

- URL: [https://cf.nascar.com/drive/2/configs-ng.json](https://cf.nascar.com/drive/2/configs-ng.json)
- Parameters: series=2. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:14.577339+00:00`
- HTTP: 403; source response size: 146 bytes.
- Verified interpretation / limitation: HTTP 403 MissingKey. No JSON schema verified; no credential discovery or retry.
- [Request evidence](Documentation/27_request_evidence.json)
- [Exact XML failure](07_Legacy_and_Unavailable/27_error.xml)

No verified JSON fields. The 403 XML reports `MissingKey`: `Missing Key-Pair-Id query parameter or cookie value`.

## Endpoint 28

**Series 3 Drive configuration**

- URL: [https://cf.nascar.com/drive/3/configs-ng.json](https://cf.nascar.com/drive/3/configs-ng.json)
- Parameters: series=3. No supplied query parameters.
- Snapshot request start (UTC): `2026-10-21T11:05:14.694553+00:00`
- HTTP: 403; source response size: 146 bytes.
- Verified interpretation / limitation: HTTP 403 MissingKey. No JSON schema verified; no credential discovery or retry.
- [Request evidence](Documentation/28_request_evidence.json)
- [Exact XML failure](07_Legacy_and_Unavailable/28_error.xml)

No verified JSON fields. The 403 XML reports `MissingKey`: `Missing Key-Pair-Id query parameter or cookie value`.

## Supporting file index and Codex workflow

Read this document first, then open supporting artifacts only when deeper source evidence is needed.

| File | Purpose |
|---|---|
| [README](README.md) | Package usage and provenance |
| [Manifest](Documentation/manifest.json) | Every URL, capture time, status, source hash and sample filename |
| [Machine-readable field profiles](Documentation/field_profiles.json) | Full profile metadata, including observed object keys |
| [Identifier observations](Documentation/identifier_observations.json) | Observed identifier values by endpoint/path |
| [Observed code domains](Documentation/observed_code_domains.json) | Flag/status/type codes observed, without invented semantic mappings |
| [Relationship checks](Documentation/verified_relationships.json) | Computed joins and namespace comparisons |
| [Standalone schema reference](Documentation/schema_reference.md) | Compact alternate full dictionary |
| [Source inspection](Documentation/inspection.md) | How the brief supplies access and routing dependencies |
| [Original brief](Documentation/source_brief.md) | User-supplied development requirements |
| [Checksums](Documentation/checksums.sha256) | Integrity of every distributed file except the checksum file itself |

Codex should compare the current repository models against the paths and types here, retain unknown or unavailable values explicitly, and check race/series/session identity before joining feeds. The repository was not inspected in this capture task. Use approved original captures for replay tests, timezone verification, gaps, lifecycle transitions and event deduplication. Do not treat redacted samples as current facts or a live fallback. No phase is certified production-ready by this archive.
