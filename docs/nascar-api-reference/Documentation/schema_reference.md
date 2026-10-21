# Observed JSON schema reference

Profiles exhaustively walk every array member and object in every successful capture. Types reflect JSON decoding. Integer and number indicate observed representations, not a normative schema. Missing counts describe this capture only and do not establish optionality across time. All-present fields are not guaranteed required. Empty arrays have unknown item schemas. Field meaning and units remain unknown unless separately discussed in findings.

## 01 https://cf.nascar.com/live/feeds/live-feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.lap_number | integer:1 | 0 | 0 | 0 |  |
| $.elapsed_time | integer:1 | 0 | 0 | 0 |  |
| $.flag_state | integer:1 | 0 | 0 | 0 |  |
| $.race_id | integer:1 | 0 | 0 | 0 |  |
| $.laps_in_race | integer:1 | 0 | 0 | 0 |  |
| $.laps_to_go | integer:1 | 0 | 0 | 0 |  |
| $.vehicles | array:1 | 0 | 0 | 0 | [37, 37] |
| $.vehicles[] | object:37 | 0 | - | 0 |  |
| $.vehicles[].average_restart_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].average_running_position | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].average_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_manufacturer | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_number | string:37 | 0 | 0 | 0 | {'numeric string': 37} |
| $.vehicles[].driver | object:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.driver_id | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.full_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.first_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.last_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.is_in_chase | boolean:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_elapsed_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].fastest_laps_run | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_position_improved | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_completed | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_led | array:37 | 0 | 0 | 0 | [0, 6] |
| $.vehicles[].laps_led[] | object:22 | 0 | - | 0 |  |
| $.vehicles[].laps_led[].start_lap | integer:22 | 0 | 0 | 0 |  |
| $.vehicles[].laps_led[].end_lap | integer:22 | 0 | 0 | 0 |  |
| $.vehicles[].last_lap_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].last_lap_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].passes_made | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].passing_differential | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].position_differential_last_10_percent | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops | array:37 | 0 | 0 | 0 | [5, 11] |
| $.vehicles[].pit_stops[] | object:374 | 0 | - | 0 |  |
| $.vehicles[].pit_stops[].positions_gained_lossed | integer:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_elapsed_time | number:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_lap_count | integer:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_leader_lap | integer:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_out_elapsed_time | number:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_rank | integer:374 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_out_rank | integer:374 | 0 | 0 | 0 |  |
| $.vehicles[].qualifying_status | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].running_position | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].status | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].delta | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].sponsor_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].starting_position | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].times_passed | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].quality_passes | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].is_on_track | boolean:37 | 0 | 0 | 0 |  |
| $.vehicles[].is_on_dvp | boolean:37 | 0 | 0 | 0 |  |
| $.run_id | integer:1 | 0 | 0 | 0 |  |
| $.run_name | string:1 | 0 | 0 | 0 |  |
| $.series_id | integer:1 | 0 | 0 | 0 |  |
| $.time_of_day | integer:1 | 0 | 0 | 0 |  |
| $.time_of_day_os | string:1 | 0 | 0 | 0 | {'ISO-like datetime with offset': 1} |
| $.track_id | integer:1 | 0 | 0 | 0 |  |
| $.track_length | number:1 | 0 | 0 | 0 |  |
| $.track_name | string:1 | 0 | 0 | 0 |  |
| $.run_type | integer:1 | 0 | 0 | 0 |  |
| $.number_of_caution_segments | integer:1 | 0 | 0 | 0 |  |
| $.number_of_caution_laps | integer:1 | 0 | 0 | 0 |  |
| $.number_of_lead_changes | integer:1 | 0 | 0 | 0 |  |
| $.number_of_leaders | integer:1 | 0 | 0 | 0 |  |
| $.avg_diff_1to3 | integer:1 | 0 | 0 | 0 |  |
| $.stage | object:1 | 0 | 0 | 0 |  |
| $.stage.stage_num | integer:1 | 0 | 0 | 0 |  |
| $.stage.finish_at_lap | integer:1 | 0 | 0 | 0 |  |
| $.stage.laps_in_stage | integer:1 | 0 | 0 | 0 |  |

## 02 https://cf.nascar.com/live/feeds/live-flag-data.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [15, 15] |
| $[] | object:15 | 0 | - | 0 |  |
| $[].lap_number | integer:15 | 0 | 0 | 0 |  |
| $[].flag_state | integer:15 | 0 | 0 | 0 |  |
| $[].elapsed_time | number:15 | 0 | 0 | 0 |  |
| $[].comment | null:9, string:6 | 9 | 0 | 0 |  |
| $[].beneficiary | null:9, string:6 | 9 | 0 | 0 |  |
| $[].time_of_day | number:15 | 0 | 0 | 0 |  |
| $[].time_of_day_os | string:15 | 0 | 0 | 0 | {'ISO-like datetime with offset': 15} |

## 03 https://cf.nascar.com/live/feeds/live-pit-data.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [337, 337] |
| $[] | object:337 | 0 | - | 0 |  |
| $[].vehicle_number | string:337 | 0 | 0 | 0 | {'numeric string': 337} |
| $[].driver_name | string:337 | 0 | 0 | 0 |  |
| $[].vehicle_manufacturer | string:337 | 0 | 0 | 0 |  |
| $[].leader_lap | integer:337 | 0 | 0 | 0 |  |
| $[].lap_count | integer:337 | 0 | 0 | 0 |  |
| $[].pit_in_flag_status | integer:337 | 0 | 0 | 0 |  |
| $[].pit_out_flag_status | integer:337 | 0 | 0 | 0 |  |
| $[].pit_in_race_time | number:337 | 0 | 0 | 0 |  |
| $[].pit_out_race_time | number:337 | 0 | 0 | 0 |  |
| $[].total_duration | number:337 | 0 | 0 | 0 |  |
| $[].box_stop_race_time | number:337 | 0 | 0 | 0 |  |
| $[].box_leave_race_time | number:337 | 0 | 0 | 0 |  |
| $[].pit_stop_duration | number:337 | 0 | 0 | 0 |  |
| $[].in_travel_duration | number:337 | 0 | 0 | 0 |  |
| $[].out_travel_duration | number:337 | 0 | 0 | 0 |  |
| $[].pit_stop_type | string:337 | 0 | 0 | 0 |  |
| $[].left_front_tire_changed | boolean:337 | 0 | 0 | 0 |  |
| $[].left_rear_tire_changed | boolean:337 | 0 | 0 | 0 |  |
| $[].right_front_tire_changed | boolean:337 | 0 | 0 | 0 |  |
| $[].right_rear_tire_changed | boolean:337 | 0 | 0 | 0 |  |
| $[].previous_lap_time | number:337 | 0 | 0 | 0 |  |
| $[].next_lap_time | number:337 | 0 | 0 | 0 |  |
| $[].pit_in_rank | integer:337 | 0 | 0 | 0 |  |
| $[].pit_out_rank | integer:337 | 0 | 0 | 0 |  |
| $[].positions_gained_lost | integer:337 | 0 | 0 | 0 |  |

## 04 https://cf.nascar.com/live/feeds/live-points.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [58, 58] |
| $[] | object:58 | 0 | - | 0 |  |
| $[].bonus_points | integer:58 | 0 | 0 | 0 |  |
| $[].car_number | string:58 | 0 | 0 | 21 | {'numeric string': 37} |
| $[].delta_leader | integer:58 | 0 | 0 | 0 |  |
| $[].delta_next | integer:58 | 0 | 0 | 0 |  |
| $[].first_name | string:58 | 0 | 0 | 0 |  |
| $[].driver_id | integer:58 | 0 | 0 | 0 |  |
| $[].is_in_chase | boolean:58 | 0 | 0 | 0 |  |
| $[].is_points_eligible | boolean:58 | 0 | 0 | 0 |  |
| $[].is_fastest_lap_point | boolean:58 | 0 | 0 | 0 |  |
| $[].is_rookie | boolean:58 | 0 | 0 | 0 |  |
| $[].last_name | string:58 | 0 | 0 | 0 |  |
| $[].membership_id | integer:58 | 0 | 0 | 0 |  |
| $[].points | integer:58 | 0 | 0 | 0 |  |
| $[].points_position | integer:58 | 0 | 0 | 0 |  |
| $[].points_earned_this_race | integer:58 | 0 | 0 | 0 |  |
| $[].stage_1_points | integer:58 | 0 | 0 | 0 |  |
| $[].stage_1_winner | boolean:58 | 0 | 0 | 0 |  |
| $[].stage_2_points | integer:58 | 0 | 0 | 0 |  |
| $[].stage_2_winner | boolean:58 | 0 | 0 | 0 |  |
| $[].stage_3_points | integer:58 | 0 | 0 | 0 |  |
| $[].stage_3_winner | boolean:58 | 0 | 0 | 0 |  |
| $[].wins | integer:55, string:3 | 0 | 0 | 0 | {'numeric string': 3} |
| $[].top_5 | integer:55, string:3 | 0 | 0 | 0 | {'numeric string': 3} |
| $[].top_10 | integer:55, string:3 | 0 | 0 | 0 | {'numeric string': 3} |
| $[].poles | integer:55, string:3 | 0 | 0 | 0 | {'numeric string': 3} |
| $[].series_id | integer:58 | 0 | 0 | 0 |  |
| $[].race_id | integer:58 | 0 | 0 | 0 |  |
| $[].run_id | integer:58 | 0 | 0 | 0 |  |

## 05 https://cf.nascar.com/live/feeds/live-stage-points.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [2, 2] |
| $[] | object:2 | 0 | - | 0 |  |
| $[].race_id | integer:2 | 0 | 0 | 0 |  |
| $[].run_id | integer:2 | 0 | 0 | 0 |  |
| $[].stage_number | integer:2 | 0 | 0 | 0 |  |
| $[].results | array:2 | 0 | 0 | 0 | [36, 36] |
| $[].results[] | object:72 | 0 | - | 0 |  |
| $[].results[].position | integer:72 | 0 | 0 | 0 |  |
| $[].results[].vehicle_number | string:72 | 0 | 0 | 0 | {'numeric string': 72} |
| $[].results[].driver_id | integer:72 | 0 | 0 | 0 |  |
| $[].results[].full_name | string:72 | 0 | 0 | 0 |  |
| $[].results[].stage_points | integer:72 | 0 | 0 | 0 |  |

## 06 https://cf.nascar.com/cacher/2026/race_list_basic.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.series_2 | array:1 | 0 | 0 | 0 | [33, 33] |
| $.series_2[] | object:33 | 0 | - | 0 |  |
| $.series_2[].race_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].series_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].race_season | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].race_name | string:33 | 0 | 0 | 0 |  |
| $.series_2[].race_type_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].restrictor_plate | boolean:33 | 0 | 0 | 0 |  |
| $.series_2[].track_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].track_name | string:33 | 0 | 0 | 0 |  |
| $.series_2[].date_scheduled | string:33 | 0 | 0 | 0 | {'ISO-like datetime without offset': 33} |
| $.series_2[].race_date | string:33 | 0 | 0 | 0 | {'ISO-like datetime without offset': 33} |
| $.series_2[].qualifying_date | string:33 | 0 | 0 | 0 | {'ISO-like datetime without offset': 33} |
| $.series_2[].tunein_date | string:33 | 0 | 0 | 0 | {'ISO-like datetime without offset': 33} |
| $.series_2[].scheduled_distance | integer:19, number:14 | 0 | 0 | 0 |  |
| $.series_2[].actual_distance | integer:15, number:18 | 0 | 0 | 0 |  |
| $.series_2[].scheduled_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].actual_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].stage_1_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].stage_2_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].stage_3_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].number_of_cars_in_field | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].pole_winner_driver_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].pole_winner_speed | number:22, integer:11 | 0 | 0 | 0 |  |
| $.series_2[].number_of_lead_changes | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].number_of_leaders | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].number_of_cautions | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].number_of_caution_laps | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].average_speed | number:30, integer:3 | 0 | 0 | 0 |  |
| $.series_2[].total_race_time | string:33 | 0 | 0 | 3 | {'clock/duration string': 30} |
| $.series_2[].margin_of_victory | string:33 | 0 | 0 | 3 | {'numeric string': 19} |
| $.series_2[].race_purse | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].race_comments | string:33 | 0 | 0 | 3 |  |
| $.series_2[].attendance | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].infractions | array:33 | 0 | 0 | 0 | [0, 0] |
| $.series_2[].schedule | array:33 | 0 | 0 | 0 | [9, 14] |
| $.series_2[].schedule[] | object:362 | 0 | - | 0 |  |
| $.series_2[].schedule[].event_name | string:362 | 0 | 0 | 0 |  |
| $.series_2[].schedule[].notes | string:362 | 0 | 0 | 92 |  |
| $.series_2[].schedule[].start_time_utc | string:362 | 0 | 0 | 0 | {'ISO-like datetime without offset': 362} |
| $.series_2[].schedule[].run_type | integer:362 | 0 | 0 | 0 |  |
| $.series_2[].radio_broadcaster | string:33 | 0 | 0 | 0 |  |
| $.series_2[].television_broadcaster | string:33 | 0 | 0 | 0 |  |
| $.series_2[].satellite_radio_broadcaster | string:33 | 0 | 0 | 0 |  |
| $.series_2[].master_race_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].inspection_complete | boolean:33 | 0 | 0 | 0 |  |
| $.series_2[].playoff_round | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].is_qualifying_race | boolean:33 | 0 | 0 | 0 |  |
| $.series_2[].qualifying_race_no | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].qualifying_race_id | integer:33 | 0 | 0 | 0 |  |
| $.series_2[].has_qualifying | boolean:33 | 0 | 0 | 0 |  |
| $.series_2[].winner_driver_id | integer:30, null:3 | 3 | 0 | 0 |  |
| $.series_2[].pole_winner_laptime | null:33 | 33 | 0 | 0 |  |
| $.series_3 | array:1 | 0 | 0 | 0 | [25, 25] |
| $.series_3[] | object:25 | 0 | - | 0 |  |
| $.series_3[].race_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].series_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].race_season | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].race_name | string:25 | 0 | 0 | 0 |  |
| $.series_3[].race_type_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].restrictor_plate | boolean:25 | 0 | 0 | 0 |  |
| $.series_3[].track_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].track_name | string:25 | 0 | 0 | 0 |  |
| $.series_3[].date_scheduled | string:25 | 0 | 0 | 0 | {'ISO-like datetime without offset': 25} |
| $.series_3[].race_date | string:25 | 0 | 0 | 0 | {'ISO-like datetime without offset': 25} |
| $.series_3[].qualifying_date | string:25 | 0 | 0 | 0 | {'ISO-like datetime without offset': 25} |
| $.series_3[].tunein_date | string:25 | 0 | 0 | 0 | {'ISO-like datetime without offset': 25} |
| $.series_3[].scheduled_distance | integer:11, number:14 | 0 | 0 | 0 |  |
| $.series_3[].actual_distance | integer:11, number:14 | 0 | 0 | 0 |  |
| $.series_3[].scheduled_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].actual_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].stage_1_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].stage_2_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].stage_3_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].number_of_cars_in_field | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].pole_winner_driver_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].pole_winner_speed | number:17, integer:8 | 0 | 0 | 0 |  |
| $.series_3[].number_of_lead_changes | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].number_of_leaders | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].number_of_cautions | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].number_of_caution_laps | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].average_speed | number:22, integer:3 | 0 | 0 | 0 |  |
| $.series_3[].total_race_time | string:25 | 0 | 0 | 3 | {'clock/duration string': 22} |
| $.series_3[].margin_of_victory | string:25 | 0 | 0 | 3 | {'numeric string': 18} |
| $.series_3[].race_purse | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].race_comments | string:25 | 0 | 0 | 3 |  |
| $.series_3[].attendance | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].infractions | array:25 | 0 | 0 | 0 | [0, 0] |
| $.series_3[].schedule | array:25 | 0 | 0 | 0 | [10, 18] |
| $.series_3[].schedule[] | object:297 | 0 | - | 0 |  |
| $.series_3[].schedule[].event_name | string:297 | 0 | 0 | 0 |  |
| $.series_3[].schedule[].notes | string:297 | 0 | 0 | 82 |  |
| $.series_3[].schedule[].start_time_utc | string:297 | 0 | 0 | 0 | {'ISO-like datetime without offset': 297} |
| $.series_3[].schedule[].run_type | integer:297 | 0 | 0 | 0 |  |
| $.series_3[].radio_broadcaster | string:25 | 0 | 0 | 0 |  |
| $.series_3[].television_broadcaster | string:25 | 0 | 0 | 0 |  |
| $.series_3[].satellite_radio_broadcaster | string:25 | 0 | 0 | 0 |  |
| $.series_3[].master_race_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].inspection_complete | boolean:25 | 0 | 0 | 0 |  |
| $.series_3[].playoff_round | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].is_qualifying_race | boolean:25 | 0 | 0 | 0 |  |
| $.series_3[].qualifying_race_no | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].qualifying_race_id | integer:25 | 0 | 0 | 0 |  |
| $.series_3[].has_qualifying | boolean:25 | 0 | 0 | 0 |  |
| $.series_3[].winner_driver_id | integer:22, null:3 | 3 | 0 | 0 |  |
| $.series_3[].pole_winner_laptime | null:25 | 25 | 0 | 0 |  |
| $.series_1 | array:1 | 0 | 0 | 0 | [40, 40] |
| $.series_1[] | object:40 | 0 | - | 0 |  |
| $.series_1[].race_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].series_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].race_season | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].race_name | string:40 | 0 | 0 | 0 |  |
| $.series_1[].race_type_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].restrictor_plate | boolean:40 | 0 | 0 | 0 |  |
| $.series_1[].track_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].track_name | string:40 | 0 | 0 | 0 |  |
| $.series_1[].date_scheduled | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $.series_1[].race_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $.series_1[].qualifying_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $.series_1[].tunein_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $.series_1[].scheduled_distance | number:21, integer:19 | 0 | 0 | 0 |  |
| $.series_1[].actual_distance | integer:17, number:23 | 0 | 0 | 0 |  |
| $.series_1[].scheduled_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].actual_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].stage_1_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].stage_2_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].stage_3_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].number_of_cars_in_field | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].pole_winner_driver_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].pole_winner_speed | number:24, integer:16 | 0 | 0 | 0 |  |
| $.series_1[].number_of_lead_changes | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].number_of_leaders | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].number_of_cautions | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].number_of_caution_laps | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].average_speed | number:37, integer:3 | 0 | 0 | 0 |  |
| $.series_1[].total_race_time | string:40 | 0 | 0 | 3 | {'clock/duration string': 37} |
| $.series_1[].margin_of_victory | string:40 | 0 | 0 | 3 | {'numeric string': 13} |
| $.series_1[].race_purse | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].race_comments | string:40 | 0 | 0 | 3 |  |
| $.series_1[].attendance | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].infractions | array:40 | 0 | 0 | 0 | [0, 0] |
| $.series_1[].schedule | array:40 | 0 | 0 | 0 | [3, 21] |
| $.series_1[].schedule[] | object:498 | 0 | - | 0 |  |
| $.series_1[].schedule[].event_name | string:498 | 0 | 0 | 0 |  |
| $.series_1[].schedule[].notes | string:498 | 0 | 0 | 161 |  |
| $.series_1[].schedule[].start_time_utc | string:498 | 0 | 0 | 0 | {'ISO-like datetime without offset': 498} |
| $.series_1[].schedule[].run_type | integer:498 | 0 | 0 | 0 |  |
| $.series_1[].radio_broadcaster | string:40 | 0 | 0 | 0 |  |
| $.series_1[].television_broadcaster | string:40 | 0 | 0 | 0 |  |
| $.series_1[].satellite_radio_broadcaster | string:40 | 0 | 0 | 0 |  |
| $.series_1[].master_race_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].inspection_complete | boolean:40 | 0 | 0 | 0 |  |
| $.series_1[].playoff_round | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].is_qualifying_race | boolean:40 | 0 | 0 | 0 |  |
| $.series_1[].qualifying_race_no | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].qualifying_race_id | integer:40 | 0 | 0 | 0 |  |
| $.series_1[].has_qualifying | boolean:40 | 0 | 0 | 0 |  |
| $.series_1[].winner_driver_id | integer:37, null:3 | 3 | 0 | 0 |  |
| $.series_1[].pole_winner_laptime | null:40 | 40 | 0 | 0 |  |

## 07 https://cf.nascar.com/cacher/drivers.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.status | integer:1 | 0 | 0 | 0 |  |
| $.message | string:1 | 0 | 0 | 0 |  |
| $.response | array:1 | 0 | 0 | 0 | [915, 915] |
| $.response[] | object:915 | 0 | - | 0 |  |
| $.response[].Nascar_Driver_ID | integer:915 | 0 | 0 | 0 |  |
| $.response[].Driver_ID | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Driver_Series | string:915 | 0 | 0 | 6 |  |
| $.response[].First_Name | string:915 | 0 | 0 | 0 |  |
| $.response[].Last_Name | string:915 | 0 | 0 | 0 |  |
| $.response[].Full_Name | string:915 | 0 | 0 | 0 |  |
| $.response[].Series_Logo | string:915 | 0 | 0 | 0 |  |
| $.response[].Short_Name | string:915 | 0 | 0 | 915 |  |
| $.response[].Description | string:915 | 0 | 0 | 915 |  |
| $.response[].DOB | string:915 | 0 | 0 | 706 | {'ISO-like datetime without offset': 209} |
| $.response[].DOD | string:915 | 0 | 0 | 0 | {'ISO-like datetime without offset': 915} |
| $.response[].Hometown_City | string:915 | 0 | 0 | 797 |  |
| $.response[].Crew_Chief | string:915 | 0 | 0 | 795 |  |
| $.response[].Hometown_State | string:915 | 0 | 0 | 802 |  |
| $.response[].Hometown_Country | string:915 | 0 | 0 | 797 |  |
| $.response[].Rookie_Year_Series_1 | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Rookie_Year_Series_2 | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Rookie_Year_Series_3 | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Hobbies | string:915 | 0 | 0 | 895 |  |
| $.response[].Children | string:915 | 0 | 0 | 911 |  |
| $.response[].Twitter_Handle | string:915 | 0 | 0 | 868 |  |
| $.response[].Residing_City | string:915 | 0 | 0 | 892 |  |
| $.response[].Residing_State | string:915 | 0 | 0 | 893 |  |
| $.response[].Residing_Country | string:915 | 0 | 0 | 892 |  |
| $.response[].Badge | string:915 | 0 | 0 | 16 | {'numeric string': 899} |
| $.response[].Badge_Image | string:915 | 0 | 0 | 0 |  |
| $.response[].Manufacturer | string:915 | 0 | 0 | 641 |  |
| $.response[].Manufacturer_Small | string:915 | 0 | 0 | 641 |  |
| $.response[].Team | string:915 | 0 | 0 | 49 | {'numeric string': 653} |
| $.response[].Image | string:915 | 0 | 0 | 0 |  |
| $.response[].Image_Small | string:915 | 0 | 0 | 674 |  |
| $.response[].Image_Transparent | string:915 | 0 | 0 | 915 |  |
| $.response[].SecondaryImage | string:915 | 0 | 0 | 914 |  |
| $.response[].Firesuit_Image | string:915 | 0 | 0 | 765 |  |
| $.response[].Firesuit_Image_Small | string:915 | 0 | 0 | 765 |  |
| $.response[].Career_Stats | string:915 | 0 | 0 | 915 |  |
| $.response[].Driver_Page | string:915 | 0 | 0 | 819 |  |
| $.response[].Age | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Rank | integer:915 | 0 | 0 | 0 |  |
| $.response[].Points | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Points_Behind | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].No_Wins | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Poles | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Top5 | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Top10 | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Laps_Led | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Stage_Wins | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Playoff_Points | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Playoff_Rank | string:915 | 0 | 0 | 0 | {'numeric string': 915} |
| $.response[].Integrated_Sponsor_Name | string:915 | 0 | 0 | 910 |  |
| $.response[].Integrated_Sponsor | string:915 | 0 | 0 | 910 |  |
| $.response[].Integrated_Sponsor_URL | string:915 | 0 | 0 | 910 |  |
| $.response[].Silly_Season_Change | string:915 | 0 | 0 | 908 |  |
| $.response[].Silly_Season_Change_Description | string:915 | 0 | 0 | 911 |  |
| $.response[].Driver_Post_Status | string:915 | 0 | 0 | 0 |  |
| $.response[].Driver_Part_Time | string:915 | 0 | 0 | 776 |  |

## 08 https://cf.nascar.com/cacher/tracks.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.items | array:1 | 0 | 0 | 0 | [49, 49] |
| $.items[] | object:49 | 0 | - | 0 |  |
| $.items[].track_id | integer:49 | 0 | 0 | 0 |  |
| $.items[].track_name | string:49 | 0 | 0 | 0 |  |
| $.items[].track_surface | string:49 | 0 | 0 | 0 |  |
| $.items[].track_type | string:49 | 0 | 0 | 0 |  |
| $.items[].track_banking | string:49 | 0 | 0 | 12 |  |
| $.items[].year_built | integer:49 | 0 | 0 | 0 |  |
| $.items[].track_description | string:49 | 0 | 0 | 14 |  |
| $.items[].city | string:49 | 0 | 0 | 0 |  |
| $.items[].state | string:49 | 0 | 0 | 0 |  |
| $.items[].frontstretch_length | integer:49 | 0 | 0 | 0 |  |
| $.items[].backstretch_length | integer:49 | 0 | 0 | 0 |  |
| $.items[].seating_capacity | integer:49 | 0 | 0 | 0 |  |
| $.items[].track_owner | string:46, null:3 | 3 | 0 | 0 |  |
| $.items[].races | null:49 | 49 | 0 | 0 |  |
| $.items[].length | number:46, integer:3 | 0 | 0 | 0 |  |
| $.items[].zip | string:49 | 0 | 0 | 8 | {'numeric string': 37} |
| $.items[].address | string:49 | 0 | 0 | 10 |  |
| $.items[].caution_car_speed | integer:49 | 0 | 0 | 0 |  |
| $.items[].track_image | string:47 | 0 | 2 | 0 |  |
| $.items[].track_image_thumbnail | string:47 | 0 | 2 | 0 |  |
| $.items[].track_logo | string:48 | 0 | 1 | 0 |  |
| $.items[].track_major_events | string:36 | 0 | 13 | 0 |  |
| $.items[].track_num_turns | string:36 | 0 | 13 | 0 | {'numeric string': 36} |
| $.items[].capacity | string:36 | 0 | 13 | 0 |  |
| $.items[].tickets_url | string:44 | 0 | 5 | 0 |  |
| $.items[].tickets_url_new_window | boolean:44 | 0 | 5 | 0 |  |
| $.items[].track_url | string:48 | 0 | 1 | 0 |  |
| $.items[].track_url_new_window | boolean:48 | 0 | 1 | 0 |  |
| $.items[].hide_track_from_site | boolean:48 | 0 | 1 | 0 |  |
| $.items[].track_short_name | string:1 | 0 | 48 | 0 |  |

## 09 https://cf.nascar.com/cacher/2026/1/schedule-feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [111, 111] |
| $[] | object:111 | 0 | - | 0 |  |
| $[].start_time | string:111 | 0 | 0 | 0 | {'ISO-like datetime without offset': 111} |
| $[].end_time | string:111 | 0 | 0 | 0 | {'ISO-like datetime without offset': 111} |
| $[].event_name | string:111 | 0 | 0 | 0 |  |
| $[].race_id | integer:111 | 0 | 0 | 0 |  |
| $[].track_id | integer:111 | 0 | 0 | 0 |  |
| $[].track_name | string:111 | 0 | 0 | 0 |  |
| $[].race_name | string:111 | 0 | 0 | 0 |  |
| $[].series_id | integer:111 | 0 | 0 | 0 |  |
| $[].run_type | integer:111 | 0 | 0 | 0 |  |
| $[].start_time_utc | string:111 | 0 | 0 | 0 | {'ISO-like datetime without offset': 111} |
| $[].end_time_utc | string:111 | 0 | 0 | 0 | {'ISO-like datetime without offset': 111} |

## 10 https://cf.nascar.com/cacher/2026/2/schedule-feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [91, 91] |
| $[] | object:91 | 0 | - | 0 |  |
| $[].start_time | string:91 | 0 | 0 | 0 | {'ISO-like datetime without offset': 91} |
| $[].end_time | string:91 | 0 | 0 | 0 | {'ISO-like datetime without offset': 91} |
| $[].event_name | string:91 | 0 | 0 | 0 |  |
| $[].race_id | integer:91 | 0 | 0 | 0 |  |
| $[].track_id | integer:91 | 0 | 0 | 0 |  |
| $[].track_name | string:91 | 0 | 0 | 0 |  |
| $[].race_name | string:91 | 0 | 0 | 0 |  |
| $[].series_id | integer:91 | 0 | 0 | 0 |  |
| $[].run_type | integer:91 | 0 | 0 | 0 |  |
| $[].start_time_utc | string:91 | 0 | 0 | 0 | {'ISO-like datetime without offset': 91} |
| $[].end_time_utc | string:91 | 0 | 0 | 0 | {'ISO-like datetime without offset': 91} |

## 11 https://cf.nascar.com/cacher/2026/3/schedule-feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [72, 72] |
| $[] | object:72 | 0 | - | 0 |  |
| $[].start_time | string:72 | 0 | 0 | 0 | {'ISO-like datetime without offset': 72} |
| $[].end_time | string:72 | 0 | 0 | 0 | {'ISO-like datetime without offset': 72} |
| $[].event_name | string:72 | 0 | 0 | 0 |  |
| $[].race_id | integer:72 | 0 | 0 | 0 |  |
| $[].track_id | integer:72 | 0 | 0 | 0 |  |
| $[].track_name | string:72 | 0 | 0 | 0 |  |
| $[].race_name | string:72 | 0 | 0 | 0 |  |
| $[].series_id | integer:72 | 0 | 0 | 0 |  |
| $[].run_type | integer:72 | 0 | 0 | 0 |  |
| $[].start_time_utc | string:72 | 0 | 0 | 0 | {'ISO-like datetime without offset': 72} |
| $[].end_time_utc | string:72 | 0 | 0 | 0 | {'ISO-like datetime without offset': 72} |

## 12 https://cf.nascar.com/cacher/2026/1/race_list_basic.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [40, 40] |
| $[] | object:40 | 0 | - | 0 |  |
| $[].race_id | integer:40 | 0 | 0 | 0 |  |
| $[].series_id | integer:40 | 0 | 0 | 0 |  |
| $[].race_season | integer:40 | 0 | 0 | 0 |  |
| $[].race_name | string:40 | 0 | 0 | 0 |  |
| $[].race_type_id | integer:40 | 0 | 0 | 0 |  |
| $[].restrictor_plate | boolean:40 | 0 | 0 | 0 |  |
| $[].track_id | integer:40 | 0 | 0 | 0 |  |
| $[].track_name | string:40 | 0 | 0 | 0 |  |
| $[].date_scheduled | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $[].race_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $[].qualifying_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $[].tunein_date | string:40 | 0 | 0 | 0 | {'ISO-like datetime without offset': 40} |
| $[].scheduled_distance | number:21, integer:19 | 0 | 0 | 0 |  |
| $[].actual_distance | integer:17, number:23 | 0 | 0 | 0 |  |
| $[].scheduled_laps | integer:40 | 0 | 0 | 0 |  |
| $[].actual_laps | integer:40 | 0 | 0 | 0 |  |
| $[].stage_1_laps | integer:40 | 0 | 0 | 0 |  |
| $[].stage_2_laps | integer:40 | 0 | 0 | 0 |  |
| $[].stage_3_laps | integer:40 | 0 | 0 | 0 |  |
| $[].number_of_cars_in_field | integer:40 | 0 | 0 | 0 |  |
| $[].pole_winner_driver_id | integer:40 | 0 | 0 | 0 |  |
| $[].pole_winner_speed | number:24, integer:16 | 0 | 0 | 0 |  |
| $[].number_of_lead_changes | integer:40 | 0 | 0 | 0 |  |
| $[].number_of_leaders | integer:40 | 0 | 0 | 0 |  |
| $[].number_of_cautions | integer:40 | 0 | 0 | 0 |  |
| $[].number_of_caution_laps | integer:40 | 0 | 0 | 0 |  |
| $[].average_speed | number:37, integer:3 | 0 | 0 | 0 |  |
| $[].total_race_time | string:40 | 0 | 0 | 3 | {'clock/duration string': 37} |
| $[].margin_of_victory | string:40 | 0 | 0 | 3 | {'numeric string': 13} |
| $[].race_purse | integer:40 | 0 | 0 | 0 |  |
| $[].race_comments | string:40 | 0 | 0 | 3 |  |
| $[].attendance | integer:40 | 0 | 0 | 0 |  |
| $[].infractions | array:40 | 0 | 0 | 0 | [0, 0] |
| $[].schedule | array:40 | 0 | 0 | 0 | [3, 21] |
| $[].schedule[] | object:498 | 0 | - | 0 |  |
| $[].schedule[].event_name | string:498 | 0 | 0 | 0 |  |
| $[].schedule[].notes | string:498 | 0 | 0 | 161 |  |
| $[].schedule[].start_time_utc | string:498 | 0 | 0 | 0 | {'ISO-like datetime without offset': 498} |
| $[].schedule[].run_type | integer:498 | 0 | 0 | 0 |  |
| $[].radio_broadcaster | string:40 | 0 | 0 | 0 |  |
| $[].television_broadcaster | string:40 | 0 | 0 | 0 |  |
| $[].satellite_radio_broadcaster | string:40 | 0 | 0 | 0 |  |
| $[].master_race_id | integer:40 | 0 | 0 | 0 |  |
| $[].inspection_complete | boolean:40 | 0 | 0 | 0 |  |
| $[].playoff_round | integer:40 | 0 | 0 | 0 |  |
| $[].is_qualifying_race | boolean:40 | 0 | 0 | 0 |  |
| $[].qualifying_race_no | integer:40 | 0 | 0 | 0 |  |
| $[].qualifying_race_id | integer:40 | 0 | 0 | 0 |  |
| $[].has_qualifying | boolean:40 | 0 | 0 | 0 |  |
| $[].winner_driver_id | integer:37, null:3 | 3 | 0 | 0 |  |
| $[].pole_winner_laptime | null:40 | 40 | 0 | 0 |  |

## 13 https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.weekend_race | array:1 | 0 | 0 | 0 | [1, 1] |
| $.weekend_race[] | object:1 | 0 | - | 0 |  |
| $.weekend_race[].race_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].series_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].race_season | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].race_name | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].race_type_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].restrictor_plate | boolean:1 | 0 | 0 | 0 |  |
| $.weekend_race[].track_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].track_name | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].date_scheduled | string:1 | 0 | 0 | 0 | {'ISO-like datetime without offset': 1} |
| $.weekend_race[].race_date | string:1 | 0 | 0 | 0 | {'ISO-like datetime without offset': 1} |
| $.weekend_race[].qualifying_date | string:1 | 0 | 0 | 0 | {'ISO-like datetime without offset': 1} |
| $.weekend_race[].tunein_date | string:1 | 0 | 0 | 0 | {'ISO-like datetime without offset': 1} |
| $.weekend_race[].scheduled_distance | number:1 | 0 | 0 | 0 |  |
| $.weekend_race[].actual_distance | number:1 | 0 | 0 | 0 |  |
| $.weekend_race[].scheduled_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].actual_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_1_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_2_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_3_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_4_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].number_of_cars_in_field | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].pole_winner_driver_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].pole_winner_speed | number:1 | 0 | 0 | 0 |  |
| $.weekend_race[].number_of_lead_changes | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].number_of_leaders | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].number_of_cautions | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].number_of_caution_laps | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].average_speed | number:1 | 0 | 0 | 0 |  |
| $.weekend_race[].total_race_time | string:1 | 0 | 0 | 0 | {'clock/duration string': 1} |
| $.weekend_race[].margin_of_victory | string:1 | 0 | 0 | 0 | {'numeric string': 1} |
| $.weekend_race[].race_purse | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].race_comments | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].attendance | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].results | array:1 | 0 | 0 | 0 | [36, 36] |
| $.weekend_race[].results[] | object:36 | 0 | - | 0 |  |
| $.weekend_race[].results[].result_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].finishing_position | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].starting_position | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].car_number | string:36 | 0 | 0 | 0 | {'numeric string': 36} |
| $.weekend_race[].results[].driver_fullname | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].driver_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].driver_hometown | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].hometown_city | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].hometown_state | string:36 | 0 | 0 | 1 |  |
| $.weekend_race[].results[].hometown_country | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].team_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].team_name | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].qualifying_order | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].qualifying_position | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].qualifying_speed | number:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].laps_led | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].times_led | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].car_make | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].car_model | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].sponsor | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].points_earned | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].playoff_points_earned | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].laps_completed | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].finishing_status | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].winnings | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].series_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].race_season | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].race_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].owner_fullname | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].crew_chief_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].crew_chief_fullname | string:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].points_position | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].points_delta | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].owner_id | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].official_car_number | string:36 | 0 | 0 | 0 | {'numeric string': 36} |
| $.weekend_race[].results[].disqualified | boolean:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].diff_laps | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].diff_time | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].results[].pit_box | integer:36 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments | array:1 | 0 | 0 | 0 | [9, 9] |
| $.weekend_race[].caution_segments[] | object:9 | 0 | - | 0 |  |
| $.weekend_race[].caution_segments[].race_id | integer:9 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments[].start_lap | integer:9 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments[].end_lap | integer:9 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments[].reason | string:9 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments[].comment | string:9 | 0 | 0 | 0 |  |
| $.weekend_race[].caution_segments[].beneficiary_car_number | null:1, string:8 | 1 | 0 | 0 | {'numeric string': 8} |
| $.weekend_race[].caution_segments[].flag_state | integer:9 | 0 | 0 | 0 |  |
| $.weekend_race[].race_leaders | array:1 | 0 | 0 | 0 | [55, 55] |
| $.weekend_race[].race_leaders[] | object:55 | 0 | - | 0 |  |
| $.weekend_race[].race_leaders[].start_lap | integer:55 | 0 | 0 | 0 |  |
| $.weekend_race[].race_leaders[].end_lap | integer:55 | 0 | 0 | 0 |  |
| $.weekend_race[].race_leaders[].car_number | string:55 | 0 | 0 | 0 | {'numeric string': 55} |
| $.weekend_race[].race_leaders[].race_id | integer:55 | 0 | 0 | 0 |  |
| $.weekend_race[].infractions | array:1 | 0 | 0 | 0 | [0, 0] |
| $.weekend_race[].schedule | array:1 | 0 | 0 | 0 | [16, 16] |
| $.weekend_race[].schedule[] | object:16 | 0 | - | 0 |  |
| $.weekend_race[].schedule[].event_name | string:16 | 0 | 0 | 0 |  |
| $.weekend_race[].schedule[].notes | string:16 | 0 | 0 | 6 |  |
| $.weekend_race[].schedule[].start_time_utc | string:16 | 0 | 0 | 0 | {'ISO-like datetime without offset': 16} |
| $.weekend_race[].schedule[].run_type | integer:16 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_results | array:1 | 0 | 0 | 0 | [2, 2] |
| $.weekend_race[].stage_results[] | object:2 | 0 | - | 0 |  |
| $.weekend_race[].stage_results[].stage_number | integer:2 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_results[].results | array:2 | 0 | 0 | 0 | [10, 10] |
| $.weekend_race[].stage_results[].results[] | object:20 | 0 | - | 0 |  |
| $.weekend_race[].stage_results[].results[].driver_fullname | string:20 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_results[].results[].driver_id | integer:20 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_results[].results[].car_number | string:20 | 0 | 0 | 0 | {'numeric string': 20} |
| $.weekend_race[].stage_results[].results[].finishing_position | integer:20 | 0 | 0 | 0 |  |
| $.weekend_race[].stage_results[].results[].stage_points | integer:20 | 0 | 0 | 0 |  |
| $.weekend_race[].pit_reports | array:1 | 0 | 0 | 0 | [0, 0] |
| $.weekend_race[].radio_broadcaster | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].television_broadcaster | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].satellite_radio_broadcaster | string:1 | 0 | 0 | 0 |  |
| $.weekend_race[].master_race_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].timing_run_id | integer:1 | 0 | 0 | 0 |  |
| $.weekend_race[].inspection_complete | boolean:1 | 0 | 0 | 0 |  |
| $.weekend_race[].playoff_round | integer:1 | 0 | 0 | 0 |  |
| $.weekend_runs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.weekend_runs[] | object:2 | 0 | - | 0 |  |
| $.weekend_runs[].weekend_run_id | integer:2 | 0 | 0 | 0 |  |
| $.weekend_runs[].race_id | integer:2 | 0 | 0 | 0 |  |
| $.weekend_runs[].timing_run_id | integer:2 | 0 | 0 | 0 |  |
| $.weekend_runs[].run_type | integer:2 | 0 | 0 | 0 |  |
| $.weekend_runs[].run_name | string:2 | 0 | 0 | 0 |  |
| $.weekend_runs[].run_date | string:2 | 0 | 0 | 0 | {'ISO-like datetime without offset': 2} |
| $.weekend_runs[].run_date_utc | string:2 | 0 | 0 | 0 | {'ISO-like datetime without offset': 2} |
| $.weekend_runs[].results | array:2 | 0 | 0 | 0 | [36, 36] |
| $.weekend_runs[].results[] | object:72 | 0 | - | 0 |  |
| $.weekend_runs[].results[].run_id | integer:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].car_number | string:72 | 0 | 0 | 0 | {'numeric string': 72} |
| $.weekend_runs[].results[].vehicle_number | string:72 | 0 | 0 | 0 | {'numeric string': 72} |
| $.weekend_runs[].results[].manufacturer | string:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].driver_id | integer:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].driver_name | string:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].finishing_position | integer:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].best_lap_time | number:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].best_lap_speed | number:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].best_lap_number | integer:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].laps_completed | integer:72 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].comment | string:72 | 0 | 0 | 72 |  |
| $.weekend_runs[].results[].delta_leader | integer:2, number:70 | 0 | 0 | 0 |  |
| $.weekend_runs[].results[].disqualified | boolean:72 | 0 | 0 | 0 |  |

## 14 https://cf.nascar.com/cacher/2024/1/5392/lap-times.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.laps | array:1 | 0 | 0 | 0 | [36, 36] |
| $.laps[] | object:36 | 0 | - | 0 |  |
| $.laps[].Number | string:36 | 0 | 0 | 0 | {'numeric string': 36} |
| $.laps[].FullName | string:36 | 0 | 0 | 0 |  |
| $.laps[].Manufacturer | string:36 | 0 | 0 | 0 |  |
| $.laps[].RunningPos | integer:36 | 0 | 0 | 0 |  |
| $.laps[].NASCARDriverID | integer:36 | 0 | 0 | 0 |  |
| $.laps[].Laps | array:36 | 0 | 0 | 0 | [193, 501] |
| $.laps[].Laps[] | object:17647 | 0 | - | 0 |  |
| $.laps[].Laps[].Lap | integer:17647 | 0 | 0 | 0 |  |
| $.laps[].Laps[].LapTime | null:36, number:17594, integer:17 | 36 | 0 | 0 |  |
| $.laps[].Laps[].LapSpeed | null:36, string:17611 | 36 | 0 | 0 | {'numeric string': 17611} |
| $.laps[].Laps[].RunningPos | integer:17647 | 0 | 0 | 0 |  |
| $.flags | array:1 | 0 | 0 | 0 | [501, 501] |
| $.flags[] | object:501 | 0 | - | 0 |  |
| $.flags[].LapsCompleted | integer:501 | 0 | 0 | 0 |  |
| $.flags[].FlagState | integer:501 | 0 | 0 | 0 |  |

## 15 https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.laps | object:1 | 0 | 0 | 0 |  |
| $.laps.0 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.0[] | object:1 | 0 | - | 0 |  |
| $.laps.0[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.0[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.0[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.0[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.0[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.1 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.1[] | object:1 | 0 | - | 0 |  |
| $.laps.1[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.1[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.1[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.1[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.1[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.3 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.3[] | object:1 | 0 | - | 0 |  |
| $.laps.3[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.3[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.3[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.3[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.3[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.14 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.14[] | object:1 | 0 | - | 0 |  |
| $.laps.14[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.14[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.14[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.14[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.14[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.19 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.19[] | object:1 | 0 | - | 0 |  |
| $.laps.19[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.19[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.19[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.19[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.19[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.20 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.20[] | object:1 | 0 | - | 0 |  |
| $.laps.20[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.20[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.20[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.20[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.20[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.23 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.23[] | object:1 | 0 | - | 0 |  |
| $.laps.23[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.23[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.23[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.23[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.23[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.25 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.25[] | object:1 | 0 | - | 0 |  |
| $.laps.25[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.25[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.25[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.25[].DriverIDs | array:1 | 0 | 0 | 0 | [10, 10] |
| $.laps.25[].DriverIDs[] | integer:10 | 0 | - | 0 |  |
| $.laps.31 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.31[] | object:1 | 0 | - | 0 |  |
| $.laps.31[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.31[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.31[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.31[].DriverIDs | array:1 | 0 | 0 | 0 | [9, 9] |
| $.laps.31[].DriverIDs[] | integer:9 | 0 | - | 0 |  |
| $.laps.33 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.33[] | object:1 | 0 | - | 0 |  |
| $.laps.33[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.33[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.33[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.33[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.33[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.39 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.39[] | object:1 | 0 | - | 0 |  |
| $.laps.39[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.39[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.39[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.39[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.39[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.41 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.41[] | object:1 | 0 | - | 0 |  |
| $.laps.41[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.41[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.41[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.41[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.41[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.53 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.53[] | object:1 | 0 | - | 0 |  |
| $.laps.53[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.53[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.53[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.53[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.53[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.54 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.54[] | object:1 | 0 | - | 0 |  |
| $.laps.54[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.54[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.54[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.54[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.54[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.61 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.61[] | object:1 | 0 | - | 0 |  |
| $.laps.61[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.61[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.61[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.61[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.61[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.62 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.62[] | object:1 | 0 | - | 0 |  |
| $.laps.62[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.62[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.62[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.62[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.62[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.65 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.65[] | object:1 | 0 | - | 0 |  |
| $.laps.65[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.65[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.65[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.65[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.65[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.68 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.68[] | object:1 | 0 | - | 0 |  |
| $.laps.68[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.68[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.68[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.68[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.68[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.70 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.70[] | object:1 | 0 | - | 0 |  |
| $.laps.70[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.70[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.70[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.70[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.70[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.71 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.71[] | object:1 | 0 | - | 0 |  |
| $.laps.71[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.71[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.71[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.71[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.71[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.74 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.74[] | object:1 | 0 | - | 0 |  |
| $.laps.74[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.74[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.74[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.74[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.74[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.80 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.80[] | object:1 | 0 | - | 0 |  |
| $.laps.80[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.80[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.80[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.80[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.80[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.83 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.83[] | object:1 | 0 | - | 0 |  |
| $.laps.83[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.83[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.83[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.83[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.83[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.89 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.89[] | object:1 | 0 | - | 0 |  |
| $.laps.89[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.89[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.89[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.89[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.89[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.107 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.107[] | object:1 | 0 | - | 0 |  |
| $.laps.107[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.107[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.107[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.107[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.107[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.111 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.111[] | object:1 | 0 | - | 0 |  |
| $.laps.111[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.111[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.111[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.111[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.111[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.116 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.116[] | object:1 | 0 | - | 0 |  |
| $.laps.116[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.116[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.116[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.116[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.116[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.120 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.120[] | object:1 | 0 | - | 0 |  |
| $.laps.120[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.120[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.120[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.120[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.120[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.124 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.124[] | object:1 | 0 | - | 0 |  |
| $.laps.124[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.124[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.124[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.124[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.124[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.125 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.125[] | object:1 | 0 | - | 0 |  |
| $.laps.125[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.125[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.125[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.125[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.125[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.130 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.130[] | object:1 | 0 | - | 0 |  |
| $.laps.130[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.130[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.130[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.130[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.130[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.131 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.131[] | object:1 | 0 | - | 0 |  |
| $.laps.131[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.131[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.131[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.131[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.131[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.141 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.141[] | object:1 | 0 | - | 0 |  |
| $.laps.141[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.141[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.141[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.141[].DriverIDs | array:1 | 0 | 0 | 0 | [5, 5] |
| $.laps.141[].DriverIDs[] | integer:5 | 0 | - | 0 |  |
| $.laps.146 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.146[] | object:1 | 0 | - | 0 |  |
| $.laps.146[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.146[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.146[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.146[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.146[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.150 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.150[] | object:1 | 0 | - | 0 |  |
| $.laps.150[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.150[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.150[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.150[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.150[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.154 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.154[] | object:1 | 0 | - | 0 |  |
| $.laps.154[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.154[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.154[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.154[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.154[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.157 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.157[] | object:1 | 0 | - | 0 |  |
| $.laps.157[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.157[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.157[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.157[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.157[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.159 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.159[] | object:1 | 0 | - | 0 |  |
| $.laps.159[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.159[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.159[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.159[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.159[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.171 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.171[] | object:1 | 0 | - | 0 |  |
| $.laps.171[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.171[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.171[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.171[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.171[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.176 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.176[] | object:1 | 0 | - | 0 |  |
| $.laps.176[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.176[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.176[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.176[].DriverIDs | array:1 | 0 | 0 | 0 | [5, 5] |
| $.laps.176[].DriverIDs[] | integer:5 | 0 | - | 0 |  |
| $.laps.177 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.177[] | object:1 | 0 | - | 0 |  |
| $.laps.177[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.177[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.177[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.177[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.177[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.181 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.181[] | object:1 | 0 | - | 0 |  |
| $.laps.181[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.181[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.181[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.181[].DriverIDs | array:1 | 0 | 0 | 0 | [6, 6] |
| $.laps.181[].DriverIDs[] | integer:6 | 0 | - | 0 |  |
| $.laps.186 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.186[] | object:1 | 0 | - | 0 |  |
| $.laps.186[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.186[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.186[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.186[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.186[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.190 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.190[] | object:1 | 0 | - | 0 |  |
| $.laps.190[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.190[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.190[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.190[].DriverIDs | array:1 | 0 | 0 | 0 | [4, 4] |
| $.laps.190[].DriverIDs[] | integer:4 | 0 | - | 0 |  |
| $.laps.200 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.200[] | object:1 | 0 | - | 0 |  |
| $.laps.200[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.200[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.200[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.200[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.200[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.202 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.202[] | object:1 | 0 | - | 0 |  |
| $.laps.202[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.202[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.202[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.202[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.202[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.206 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.206[] | object:1 | 0 | - | 0 |  |
| $.laps.206[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.206[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.206[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.206[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.206[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.224 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.224[] | object:1 | 0 | - | 0 |  |
| $.laps.224[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.224[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.224[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.224[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.224[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.228 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.228[] | object:1 | 0 | - | 0 |  |
| $.laps.228[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.228[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.228[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.228[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.228[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.229 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.229[] | object:1 | 0 | - | 0 |  |
| $.laps.229[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.229[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.229[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.229[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.229[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.234 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.234[] | object:1 | 0 | - | 0 |  |
| $.laps.234[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.234[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.234[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.234[].DriverIDs | array:1 | 0 | 0 | 0 | [8, 8] |
| $.laps.234[].DriverIDs[] | integer:8 | 0 | - | 0 |  |
| $.laps.240 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.240[] | object:1 | 0 | - | 0 |  |
| $.laps.240[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.240[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.240[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.240[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.240[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.244 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.244[] | object:1 | 0 | - | 0 |  |
| $.laps.244[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.244[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.244[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.244[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.244[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.249 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.249[] | object:1 | 0 | - | 0 |  |
| $.laps.249[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.249[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.249[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.249[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.249[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.251 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.251[] | object:1 | 0 | - | 0 |  |
| $.laps.251[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.251[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.251[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.251[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.251[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.252 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.252[] | object:1 | 0 | - | 0 |  |
| $.laps.252[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.252[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.252[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.252[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.252[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.256 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.256[] | object:1 | 0 | - | 0 |  |
| $.laps.256[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.256[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.256[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.256[].DriverIDs | array:1 | 0 | 0 | 0 | [6, 6] |
| $.laps.256[].DriverIDs[] | integer:6 | 0 | - | 0 |  |
| $.laps.261 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.261[] | object:1 | 0 | - | 0 |  |
| $.laps.261[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.261[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.261[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.261[].DriverIDs | array:1 | 0 | 0 | 0 | [0, 0] |
| $.laps.265 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.265[] | object:1 | 0 | - | 0 |  |
| $.laps.265[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.265[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.265[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.265[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.265[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.285 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.285[] | object:1 | 0 | - | 0 |  |
| $.laps.285[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.285[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.285[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.285[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.285[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.310 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.310[] | object:1 | 0 | - | 0 |  |
| $.laps.310[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.310[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.310[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.310[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.310[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.311 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.311[] | object:1 | 0 | - | 0 |  |
| $.laps.311[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.311[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.311[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.311[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.311[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.316 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.316[] | object:1 | 0 | - | 0 |  |
| $.laps.316[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.316[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.316[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.316[].DriverIDs | array:1 | 0 | 0 | 0 | [5, 5] |
| $.laps.316[].DriverIDs[] | integer:5 | 0 | - | 0 |  |
| $.laps.323 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.323[] | object:1 | 0 | - | 0 |  |
| $.laps.323[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.323[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.323[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.323[].DriverIDs | array:1 | 0 | 0 | 0 | [5, 5] |
| $.laps.323[].DriverIDs[] | integer:5 | 0 | - | 0 |  |
| $.laps.359 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.359[] | object:1 | 0 | - | 0 |  |
| $.laps.359[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.359[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.359[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.359[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.359[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.361 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.361[] | object:1 | 0 | - | 0 |  |
| $.laps.361[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.361[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.361[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.361[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.361[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.365 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.365[] | object:1 | 0 | - | 0 |  |
| $.laps.365[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.365[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.365[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.365[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.365[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.368 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.368[] | object:1 | 0 | - | 0 |  |
| $.laps.368[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.368[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.368[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.368[].DriverIDs | array:1 | 0 | 0 | 0 | [6, 6] |
| $.laps.368[].DriverIDs[] | integer:6 | 0 | - | 0 |  |
| $.laps.369 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.369[] | object:1 | 0 | - | 0 |  |
| $.laps.369[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.369[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.369[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.369[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.369[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.373 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.373[] | object:1 | 0 | - | 0 |  |
| $.laps.373[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.373[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.373[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.373[].DriverIDs | array:1 | 0 | 0 | 0 | [4, 4] |
| $.laps.373[].DriverIDs[] | integer:4 | 0 | - | 0 |  |
| $.laps.380 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.380[] | object:1 | 0 | - | 0 |  |
| $.laps.380[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.380[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.380[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.380[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.380[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.395 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.395[] | object:1 | 0 | - | 0 |  |
| $.laps.395[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.395[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.395[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.395[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.395[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.399 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.399[] | object:1 | 0 | - | 0 |  |
| $.laps.399[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.399[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.399[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.399[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.399[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.426 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.426[] | object:1 | 0 | - | 0 |  |
| $.laps.426[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.426[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.426[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.426[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.426[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.431 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.431[] | object:1 | 0 | - | 0 |  |
| $.laps.431[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.431[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.431[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.431[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.431[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.435 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.435[] | object:1 | 0 | - | 0 |  |
| $.laps.435[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.435[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.435[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.435[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.435[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.440 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.440[] | object:1 | 0 | - | 0 |  |
| $.laps.440[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.440[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.440[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.440[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.440[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.444 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.444[] | object:1 | 0 | - | 0 |  |
| $.laps.444[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.444[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.444[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.444[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.444[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.446 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.446[] | object:1 | 0 | - | 0 |  |
| $.laps.446[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.446[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.446[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.446[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.446[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.447 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.447[] | object:1 | 0 | - | 0 |  |
| $.laps.447[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.447[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.447[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.447[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.447[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.448 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.448[] | object:1 | 0 | - | 0 |  |
| $.laps.448[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.448[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.448[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.448[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.448[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.449 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.449[] | object:1 | 0 | - | 0 |  |
| $.laps.449[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.449[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.449[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.449[].DriverIDs | array:1 | 0 | 0 | 0 | [3, 3] |
| $.laps.449[].DriverIDs[] | integer:3 | 0 | - | 0 |  |
| $.laps.451 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.451[] | object:1 | 0 | - | 0 |  |
| $.laps.451[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.451[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.451[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.451[].DriverIDs | array:1 | 0 | 0 | 0 | [2, 2] |
| $.laps.451[].DriverIDs[] | integer:2 | 0 | - | 0 |  |
| $.laps.483 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.483[] | object:1 | 0 | - | 0 |  |
| $.laps.483[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.483[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.483[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.483[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.483[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.484 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.484[] | object:1 | 0 | - | 0 |  |
| $.laps.484[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.484[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.484[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.484[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.484[].DriverIDs[] | integer:1 | 0 | - | 0 |  |
| $.laps.500 | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.500[] | object:1 | 0 | - | 0 |  |
| $.laps.500[].FlagState | integer:1 | 0 | 0 | 0 |  |
| $.laps.500[].Note | string:1 | 0 | 0 | 0 |  |
| $.laps.500[].NoteID | integer:1 | 0 | 0 | 0 |  |
| $.laps.500[].DriverIDs | array:1 | 0 | 0 | 0 | [1, 1] |
| $.laps.500[].DriverIDs[] | integer:1 | 0 | - | 0 |  |

## 16 https://cf.nascar.com/loopstats/prod/2024/1/5392.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [1, 1] |
| $[] | object:1 | 0 | - | 0 |  |
| $[].race_id | integer:1 | 0 | 0 | 0 |  |
| $[].race_name | string:1 | 0 | 0 | 0 |  |
| $[].series_id | integer:1 | 0 | 0 | 0 |  |
| $[].sch_laps | integer:1 | 0 | 0 | 0 |  |
| $[].act_laps | integer:1 | 0 | 0 | 0 |  |
| $[].drivers | array:1 | 0 | 0 | 0 | [36, 36] |
| $[].drivers[] | object:36 | 0 | - | 0 |  |
| $[].drivers[].driver_id | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].start_ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].mid_ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].closing_ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].closing_laps_diff | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].best_ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].worst_ps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].avg_ps | number:36 | 0 | 0 | 0 |  |
| $[].drivers[].passes_gf | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].passing_diff | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].passed_gf | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].quality_passes | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].fast_laps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].top15_laps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].lead_laps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].laps | integer:36 | 0 | 0 | 0 |  |
| $[].drivers[].rating | number:36 | 0 | 0 | 0 |  |

## 17 https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [1, 1] |
| $[] | object:1 | 0 | - | 0 |  |
| $[].Title | string:1 | 0 | 0 | 0 |  |
| $[].Items | array:1 | 0 | 0 | 0 | [36, 36] |
| $[].Items[] | object:36 | 0 | - | 0 |  |
| $[].Items[].Number | string:36 | 0 | 0 | 0 | {'numeric string': 36} |
| $[].Items[].NASCARDriverID | integer:36 | 0 | 0 | 0 |  |
| $[].Items[].Driver | string:36 | 0 | 0 | 0 |  |
| $[].Items[].FullName | string:36 | 0 | 0 | 0 |  |
| $[].Items[].Manufacturer | string:36 | 0 | 0 | 0 |  |
| $[].Items[].Sponsor | string:36 | 0 | 0 | 0 |  |
| $[].Items[].OverAllAvg | number:36 | 0 | 0 | 0 |  |
| $[].Items[].OverAllAvgRank | integer:36 | 0 | 0 | 0 |  |
| $[].Items[].BestLapTime | number:36 | 0 | 0 | 0 |  |
| $[].Items[].BestLapRank | integer:36 | 0 | 0 | 0 |  |
| $[].Items[].Con5Lap | number:36 | 0 | 0 | 0 |  |
| $[].Items[].Con5LapRank | integer:36 | 0 | 0 | 0 |  |
| $[].Items[].Con10Lap | number:27, integer:9 | 0 | 0 | 0 |  |
| $[].Items[].Con10LapRank | integer:27, null:9 | 9 | 0 | 0 |  |
| $[].Items[].Con15Lap | number:18, integer:18 | 0 | 0 | 0 |  |
| $[].Items[].Con15LapRank | integer:18, null:18 | 18 | 0 | 0 |  |
| $[].Items[].Con20Lap | number:12, integer:24 | 0 | 0 | 0 |  |
| $[].Items[].Con20LapRank | integer:12, null:24 | 24 | 0 | 0 |  |
| $[].Items[].Con25Lap | number:6, integer:30 | 0 | 0 | 0 |  |
| $[].Items[].Con25LapRank | integer:6, null:30 | 30 | 0 | 0 |  |
| $[].Items[].Con30Lap | number:4, integer:32 | 0 | 0 | 0 |  |
| $[].Items[].Con30LapRank | integer:4, null:32 | 32 | 0 | 0 |  |

## 18 https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [300, 300] |
| $[] | object:300 | 0 | - | 0 |  |
| $[].vehicle_number | string:300 | 0 | 0 | 0 | {'numeric string': 300} |
| $[].driver_name | string:300 | 0 | 0 | 0 |  |
| $[].vehicle_manufacturer | string:300 | 0 | 0 | 0 |  |
| $[].leader_lap | integer:300 | 0 | 0 | 0 |  |
| $[].lap_count | integer:300 | 0 | 0 | 0 |  |
| $[].pit_in_flag_status | integer:300 | 0 | 0 | 0 |  |
| $[].pit_out_flag_status | integer:300 | 0 | 0 | 0 |  |
| $[].pit_in_race_time | integer:43, number:257 | 0 | 0 | 0 |  |
| $[].pit_out_race_time | integer:73, number:227 | 0 | 0 | 0 |  |
| $[].total_duration | integer:39, number:261 | 0 | 0 | 0 |  |
| $[].box_stop_race_time | integer:42, number:258 | 0 | 0 | 0 |  |
| $[].box_leave_race_time | integer:87, number:213 | 0 | 0 | 0 |  |
| $[].pit_stop_duration | integer:87, number:213 | 0 | 0 | 0 |  |
| $[].in_travel_duration | integer:87, number:213 | 0 | 0 | 0 |  |
| $[].out_travel_duration | integer:89, number:211 | 0 | 0 | 0 |  |
| $[].pit_stop_type | string:300 | 0 | 0 | 0 |  |
| $[].left_front_tire_changed | boolean:300 | 0 | 0 | 0 |  |
| $[].left_rear_tire_changed | boolean:300 | 0 | 0 | 0 |  |
| $[].right_front_tire_changed | boolean:300 | 0 | 0 | 0 |  |
| $[].right_rear_tire_changed | boolean:300 | 0 | 0 | 0 |  |
| $[].previous_lap_time | integer:300 | 0 | 0 | 0 |  |
| $[].next_lap_time | integer:300 | 0 | 0 | 0 |  |
| $[].pit_in_rank | integer:300 | 0 | 0 | 0 |  |
| $[].pit_out_rank | integer:300 | 0 | 0 | 0 |  |
| $[].positions_gained_lost | integer:300 | 0 | 0 | 0 |  |

## 19 https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [2, 2] |
| $[] | object:2 | 0 | - | 0 |  |
| $[].race_id | integer:2 | 0 | 0 | 0 |  |
| $[].run_id | integer:2 | 0 | 0 | 0 |  |
| $[].stage_number | integer:2 | 0 | 0 | 0 |  |
| $[].results | array:2 | 0 | 0 | 0 | [36, 36] |
| $[].results[] | object:72 | 0 | - | 0 |  |
| $[].results[].position | integer:72 | 0 | 0 | 0 |  |
| $[].results[].vehicle_number | string:72 | 0 | 0 | 0 | {'numeric string': 72} |
| $[].results[].driver_id | integer:72 | 0 | 0 | 0 |  |
| $[].results[].full_name | string:72 | 0 | 0 | 0 |  |
| $[].results[].stage_points | integer:72 | 0 | 0 | 0 |  |

## 20 https://cf.nascar.com/cacher/2024/1/5392/snappytv.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.event | integer:1 | 0 | 0 | 0 |  |
| $.external_id | string:1 | 0 | 0 | 0 |  |
| $.mr | null:1 | 1 | 0 | 0 |  |
| $.social_volume | object:1 | 0 | 0 | 0 |  |
| $.social_volume.total | integer:1 | 0 | 0 | 0 |  |
| $.social_volume.current10 | integer:1 | 0 | 0 | 0 |  |
| $.social_volume.peak10 | integer:1 | 0 | 0 | 0 |  |
| $.social_volume.current60 | integer:1 | 0 | 0 | 0 |  |
| $.social_volume.peak60 | integer:1 | 0 | 0 | 0 |  |
| $.tracks | object:1 | 0 | 0 | 0 |  |
| $.tracks.0 | array:1 | 0 | 0 | 0 | [16, 16] |
| $.tracks.0[] | object:16 | 0 | - | 0 |  |
| $.tracks.0[].type | string:16 | 0 | 0 | 0 |  |
| $.tracks.0[].url_spec | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].id | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].title | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].description | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].snaptype | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].thumb_320x180 | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].thumb_640x360 | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].original_asset_url | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].friendly_id | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].embedable | boolean:8 | 0 | 8 | 0 |  |
| $.tracks.0[].embed_code | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].youtube_id | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].twitter_post_id | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].fb_post_id | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].expired | boolean:8 | 0 | 8 | 0 |  |
| $.tracks.0[].share_url_full | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].short_url | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].oembed_url_xml | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].tweet_text | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].created_at | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].updated_at | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].duration | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].video_duration | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].event_id | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].hash_tags | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].tags | array:8 | 0 | 8 | 0 | [5, 6] |
| $.tracks.0[].tags[] | string:47 | 0 | - | 0 |  |
| $.tracks.0[].tweet_vol | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].trending_score | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].event_episode_title | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].event_episode_subtitle | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].event_time | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].event_duration_in_seconds | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].channel_friendly_name | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].username | string:8 | 0 | 8 | 8 |  |
| $.tracks.0[].user_avatar_url | null:8 | 8 | 8 | 0 |  |
| $.tracks.0[].show_id | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].show_title | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].featured | boolean:8 | 0 | 8 | 0 |  |
| $.tracks.0[].inpoint_percent | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].outpoint_percent | integer:8 | 0 | 8 | 0 |  |
| $.tracks.0[].status | string:8 | 0 | 8 | 0 |  |
| $.tracks.0[].downloads | array:8 | 0 | 8 | 0 | [4, 4] |
| $.tracks.0[].downloads[] | object:32 | 0 | - | 0 |  |
| $.tracks.0[].downloads[].resolution | string:32 | 0 | 0 | 0 |  |
| $.tracks.0[].downloads[].bitrate | string:32 | 0 | 0 | 0 | {'numeric string': 32} |
| $.tracks.0[].downloads[].url | string:32 | 0 | 0 | 0 |  |
| $.tracks.1 | array:1 | 0 | 0 | 0 | [0, 0] |
| $.start_time | integer:1 | 0 | 0 | 0 |  |
| $.end_time | integer:1 | 0 | 0 | 0 |  |
| $.title | string:1 | 0 | 0 | 1 |  |
| $.live_enabled | boolean:1 | 0 | 0 | 0 |  |

## 21 https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.lap_number | integer:1 | 0 | 0 | 0 |  |
| $.elapsed_time | integer:1 | 0 | 0 | 0 |  |
| $.flag_state | integer:1 | 0 | 0 | 0 |  |
| $.race_id | integer:1 | 0 | 0 | 0 |  |
| $.laps_in_race | integer:1 | 0 | 0 | 0 |  |
| $.laps_to_go | integer:1 | 0 | 0 | 0 |  |
| $.vehicles | array:1 | 0 | 0 | 0 | [37, 37] |
| $.vehicles[] | object:37 | 0 | - | 0 |  |
| $.vehicles[].average_restart_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].average_running_position | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].average_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].best_lap_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_manufacturer | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_number | string:37 | 0 | 0 | 0 | {'numeric string': 37} |
| $.vehicles[].driver | object:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.driver_id | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.full_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.first_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.last_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].driver.is_in_chase | boolean:37 | 0 | 0 | 0 |  |
| $.vehicles[].vehicle_elapsed_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].fastest_laps_run | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_position_improved | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_completed | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].laps_led | array:37 | 0 | 0 | 0 | [0, 3] |
| $.vehicles[].laps_led[] | object:16 | 0 | - | 0 |  |
| $.vehicles[].laps_led[].start_lap | integer:16 | 0 | 0 | 0 |  |
| $.vehicles[].laps_led[].end_lap | integer:16 | 0 | 0 | 0 |  |
| $.vehicles[].last_lap_speed | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].last_lap_time | number:37 | 0 | 0 | 0 |  |
| $.vehicles[].passes_made | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].passing_differential | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].position_differential_last_10_percent | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops | array:37 | 0 | 0 | 0 | [3, 13] |
| $.vehicles[].pit_stops[] | object:302 | 0 | - | 0 |  |
| $.vehicles[].pit_stops[].positions_gained_lossed | integer:302 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_elapsed_time | integer:90, number:212 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_lap_count | integer:302 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_in_leader_lap | integer:302 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_out_elapsed_time | integer:92, number:210 | 0 | 0 | 0 |  |
| $.vehicles[].pit_stops[].pit_stop_type | string:302 | 0 | 0 | 123 |  |
| $.vehicles[].pit_stops[].pit_stop_duration | integer:126, number:176 | 0 | 0 | 0 |  |
| $.vehicles[].qualifying_status | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].running_position | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].status | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].delta | integer:16, number:21 | 0 | 0 | 0 |  |
| $.vehicles[].sponsor_name | string:37 | 0 | 0 | 0 |  |
| $.vehicles[].starting_position | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].times_passed | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].quality_passes | integer:37 | 0 | 0 | 0 |  |
| $.vehicles[].is_on_track | boolean:37 | 0 | 0 | 0 |  |
| $.vehicles[].is_on_dvp | boolean:37 | 0 | 0 | 0 |  |
| $.run_id | integer:1 | 0 | 0 | 0 |  |
| $.run_name | string:1 | 0 | 0 | 0 |  |
| $.series_id | integer:1 | 0 | 0 | 0 |  |
| $.time_of_day | integer:1 | 0 | 0 | 0 |  |
| $.time_of_day_os | string:1 | 0 | 0 | 0 | {'ISO-like datetime with offset': 1} |
| $.track_id | integer:1 | 0 | 0 | 0 |  |
| $.track_length | integer:1 | 0 | 0 | 0 |  |
| $.track_name | string:1 | 0 | 0 | 0 |  |
| $.run_type | integer:1 | 0 | 0 | 0 |  |
| $.number_of_caution_segments | integer:1 | 0 | 0 | 0 |  |
| $.number_of_caution_laps | integer:1 | 0 | 0 | 0 |  |
| $.number_of_lead_changes | integer:1 | 0 | 0 | 0 |  |
| $.number_of_leaders | integer:1 | 0 | 0 | 0 |  |
| $.avg_diff_1to3 | integer:1 | 0 | 0 | 0 |  |
| $.stage | object:1 | 0 | 0 | 0 |  |
| $.stage.stage_num | integer:1 | 0 | 0 | 0 |  |
| $.stage.finish_at_lap | integer:1 | 0 | 0 | 0 |  |
| $.stage.laps_in_stage | integer:1 | 0 | 0 | 0 |  |

## 22 https://cf.nascar.com/live/feeds/series_1/5170/live_points.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [59, 59] |
| $[] | object:59 | 0 | - | 0 |  |
| $[].bonus_points | integer:59 | 0 | 0 | 0 |  |
| $[].car_number | string:59 | 0 | 0 | 22 | {'numeric string': 37} |
| $[].delta_leader | integer:59 | 0 | 0 | 0 |  |
| $[].delta_next | integer:59 | 0 | 0 | 0 |  |
| $[].first_name | string:59 | 0 | 0 | 0 |  |
| $[].driver_id | integer:59 | 0 | 0 | 0 |  |
| $[].is_in_chase | boolean:59 | 0 | 0 | 0 |  |
| $[].is_points_eligible | boolean:59 | 0 | 0 | 0 |  |
| $[].is_rookie | boolean:59 | 0 | 0 | 0 |  |
| $[].last_name | string:59 | 0 | 0 | 0 |  |
| $[].membership_id | integer:59 | 0 | 0 | 0 |  |
| $[].points | integer:59 | 0 | 0 | 0 |  |
| $[].points_position | integer:59 | 0 | 0 | 0 |  |
| $[].points_earned_this_race | integer:59 | 0 | 0 | 0 |  |
| $[].stage_1_points | integer:59 | 0 | 0 | 0 |  |
| $[].stage_1_winner | boolean:59 | 0 | 0 | 0 |  |
| $[].stage_2_points | integer:59 | 0 | 0 | 0 |  |
| $[].stage_2_winner | boolean:59 | 0 | 0 | 0 |  |
| $[].stage_3_points | integer:59 | 0 | 0 | 0 |  |
| $[].stage_3_winner | boolean:59 | 0 | 0 | 0 |  |
| $[].wins | integer:58, string:1 | 0 | 0 | 0 | {'numeric string': 1} |
| $[].top_5 | integer:58, string:1 | 0 | 0 | 0 | {'numeric string': 1} |
| $[].top_10 | integer:58, string:1 | 0 | 0 | 0 | {'numeric string': 1} |
| $[].poles | integer:58, string:1 | 0 | 0 | 0 | {'numeric string': 1} |
| $[].series_id | integer:59 | 0 | 0 | 0 |  |
| $[].race_id | integer:59 | 0 | 0 | 0 |  |
| $[].run_id | integer:59 | 0 | 0 | 0 |  |

## 23 https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [180, 180] |
| $[] | object:180 | 0 | - | 0 |  |
| $[].vehicle_number | string:180 | 0 | 0 | 0 | {'numeric string': 180} |
| $[].driver_name | string:180 | 0 | 0 | 0 |  |
| $[].vehicle_manufacturer | string:180 | 0 | 0 | 0 |  |
| $[].leader_lap | integer:180 | 0 | 0 | 0 |  |
| $[].lap_count | integer:180 | 0 | 0 | 0 |  |
| $[].pit_in_flag_status | integer:180 | 0 | 0 | 0 |  |
| $[].pit_out_flag_status | integer:180 | 0 | 0 | 0 |  |
| $[].pit_in_race_time | number:180 | 0 | 0 | 0 |  |
| $[].pit_out_race_time | number:176, integer:4 | 0 | 0 | 0 |  |
| $[].total_duration | number:175, integer:5 | 0 | 0 | 0 |  |
| $[].box_stop_race_time | number:180 | 0 | 0 | 0 |  |
| $[].box_leave_race_time | number:180 | 0 | 0 | 0 |  |
| $[].pit_stop_duration | number:177, integer:3 | 0 | 0 | 0 |  |
| $[].in_travel_duration | number:180 | 0 | 0 | 0 |  |
| $[].out_travel_duration | number:176, integer:4 | 0 | 0 | 0 |  |
| $[].pit_stop_type | string:180 | 0 | 0 | 0 |  |
| $[].left_front_tire_changed | boolean:180 | 0 | 0 | 0 |  |
| $[].left_rear_tire_changed | boolean:180 | 0 | 0 | 0 |  |
| $[].right_front_tire_changed | boolean:180 | 0 | 0 | 0 |  |
| $[].right_rear_tire_changed | boolean:180 | 0 | 0 | 0 |  |
| $[].previous_lap_time | integer:180 | 0 | 0 | 0 |  |
| $[].next_lap_time | integer:180 | 0 | 0 | 0 |  |
| $[].pit_in_rank | integer:180 | 0 | 0 | 0 |  |
| $[].pit_out_rank | integer:180 | 0 | 0 | 0 |  |
| $[].positions_gained_lost | integer:180 | 0 | 0 | 0 |  |

## 24 https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | array:1 | 0 | - | 0 | [30, 30] |
| $[] | object:30 | 0 | - | 0 |  |
| $[].Number | string:30 | 0 | 0 | 0 | {'numeric string': 30} |
| $[].NASCARDriverID | integer:30 | 0 | 0 | 0 |  |
| $[].Driver | string:30 | 0 | 0 | 0 |  |
| $[].FullName | string:30 | 0 | 0 | 0 |  |
| $[].Manufacturer | string:30 | 0 | 0 | 0 |  |
| $[].Sponsor | null:30 | 30 | 0 | 0 |  |
| $[].OverAllAvg | number:30 | 0 | 0 | 0 |  |
| $[].OverAllAvgRank | integer:30 | 0 | 0 | 0 |  |
| $[].BestLapTime | number:30 | 0 | 0 | 0 |  |
| $[].BestLapRank | integer:30 | 0 | 0 | 0 |  |
| $[].Con5Lap | number:25, integer:5 | 0 | 0 | 0 |  |
| $[].Con5LapRank | integer:25, null:5 | 5 | 0 | 0 |  |
| $[].Con10Lap | number:11, integer:19 | 0 | 0 | 0 |  |
| $[].Con10LapRank | integer:11, null:19 | 19 | 0 | 0 |  |
| $[].Con15Lap | integer:25, number:5 | 0 | 0 | 0 |  |
| $[].Con15LapRank | null:25, integer:5 | 25 | 0 | 0 |  |
| $[].Con20Lap | integer:28, number:2 | 0 | 0 | 0 |  |
| $[].Con20LapRank | null:28, integer:2 | 28 | 0 | 0 |  |
| $[].Con25Lap | integer:29, number:1 | 0 | 0 | 0 |  |
| $[].Con25LapRank | null:29, integer:1 | 29 | 0 | 0 |  |
| $[].Con30Lap | integer:30 | 0 | 0 | 0 |  |
| $[].Con30LapRank | null:30 | 30 | 0 | 0 |  |

## 25 https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json

| Path | Types (count) | Nulls | Missing in parent | Empty strings | Formats / array length range |
|---|---|---:|---:|---:|---|
| $ | object:1 | 0 | - | 0 |  |
| $.status | integer:1 | 0 | 0 | 0 |  |
| $.message | string:1 | 0 | 0 | 0 |  |
| $.response | object:1 | 0 | 0 | 0 |  |
| $.response.news | object:1 | 0 | 0 | 0 |  |
| $.response.news.article | array:1 | 0 | 0 | 0 | [0, 0] |

## 26 https://cf.nascar.com/drive/1/configs-ng.json

No verified JSON schema. See request evidence.

## 27 https://cf.nascar.com/drive/2/configs-ng.json

No verified JSON schema. See request evidence.

## 28 https://cf.nascar.com/drive/3/configs-ng.json

No verified JSON schema. See request evidence.
