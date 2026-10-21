# Endpoint catalog — all 28 original URLs

Historical development audit date: **October 21, 2026 (America/New_York)**.
The later [supplied observed package](../nascar-api-reference/START_HERE.md) records
separate successful snapshots and is the primary Phase 3B structural source.
See [current adapter boundaries](../PHASE3B_EVIDENCE.md); the request outcomes
below remain unchanged historical evidence. Exact request times below
are UTC. Source: the root [brief](../../NASCAR_Race_Center_Codex_Brief.md).
The prior 24-working/four-error browser reports remain owner evidence, not
current origin statuses.

**28 attempted; 28 proxy CONNECT denials; 0 origin HTTP responses; 0 usable
real JSON samples; 0 real captures committed or retained locally.** A proxy
CONNECT 403 is not an HTTP 403 from NASCAR. No current Cloudflare determination
or global service-inaccessibility claim follows from these results.

Machine evidence: [per-request report](probes/2026-10-21.json),
[inventory](endpoints.json). See [manual workflow](README.md) and
[schema reference](SCHEMA_REFERENCE.md).

| ID / URL details below | Category | URL series context | Owner report | Current origin HTTP | Real fixture |
| --- | --- | --- | --- | --- | --- |
| [live_feed](#live-feed) | live | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [live_flags](#live-flags) | live | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [live_pits](#live-pits) | live | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [live_points](#live-points) | live | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [live_stage_points](#live-stage-points) | live | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [season_races](#season-races) | schedule_reference | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [drivers](#drivers) | schedule_reference | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [tracks](#tracks) | schedule_reference | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [cup_schedule](#cup-schedule) | schedule_reference | 1 | working | none; proxy CONNECT 403 | none |
| [series2_schedule](#series2-schedule) | schedule_reference | 2 | working | none; proxy CONNECT 403 | none |
| [trucks_schedule](#trucks-schedule) | schedule_reference | 3 | working | none; proxy CONNECT 403 | none |
| [cup_races](#cup-races) | schedule_reference | 1 | working | none; proxy CONNECT 403 | none |
| [weekend](#weekend) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [lap_times](#lap-times) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [lap_notes](#lap-notes) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [loop_stats](#loop-stats) | historical | global / unverified coverage | working | none; proxy CONNECT 403 | none |
| [lap_averages](#lap-averages) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [archived_pits](#archived-pits) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [archived_stages](#archived-stages) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [video_metadata](#video-metadata) | historical | 1 | working | none; proxy CONNECT 403 | none |
| [legacy_live](#legacy-live) | legacy | 1 | working | none; proxy CONNECT 403 | none |
| [legacy_points](#legacy-points) | legacy | 1 | working | none; proxy CONNECT 403 | none |
| [legacy_pits](#legacy-pits) | legacy | 1 | working | none; proxy CONNECT 403 | none |
| [legacy_practice_averages](#legacy-practice-averages) | legacy | 2 | working | none; proxy CONNECT 403 | none |
| [driver_recap](#driver-recap) | excluded | 1 | error_login | none; proxy CONNECT 403 | none |
| [drive_cup](#drive-cup) | excluded | 1 | error_login | none; proxy CONNECT 403 | none |
| [drive_series2](#drive-series2) | excluded | 2 | error_login | none; proxy CONNECT 403 | none |
| [drive_trucks](#drive-trucks) | excluded | 3 | error_login | none; proxy CONNECT 403 | none |

## Interpretation and alternatives

All URL season/series/race context below is parsed from the **requested path**,
not supplied by a response. Global endpoints list national series as intended
application scope, not proof that every series is represented. No session/run ID
was observed. No origin response type, content freshness, JSON structure, cache
age, source timezone, or active-session status could be inspected.

The browser retrieval tool was also tried for global live and season-list URLs.
It exposed a JSON content-type label for live but no inspectable body/status or
retrieval headers; the schedule attempt returned an internal retrieval error.
These are inconclusive tool observations, not usable captures or direct GET
successes. No alternate proxy, host/IP substitution, login, token discovery,
Swagger or media URL was used. Legitimate next steps are allowing the documented
host through normal environment configuration or reviewing owner-supplied JSON
from an authorized ordinary client with provenance. Pinned community references
can guide synthetic tests but cannot replace real response inspection.

Synthetic links below refer to existing regression contracts only. They do not
correspond to successfully retrieved endpoint samples. Historical and legacy URL
success would still not prove a currently active session.

## live-feed

- **Full URL:** `https://cf.nascar.com/live/feeds/live-feed.json`
- **Purpose/category:** Global reported live session and vehicle scoring; `live`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:54.167552+00:00` → `2026-10-21T10:20:54.177614+00:00`; 10 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** global live path; may contain archived/inactive content. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [season_races](#season-races), [cup_schedule](#cup-schedule), [drivers](#drivers), [tracks](#tracks).
- **Integration dependencies:** Live context, flag/lap, leaderboard and favorites (Phases 1/3A).
- **Fixture:** [live_timing.json](../../tests/fixtures/nascar/live_timing.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## live-flags

- **Full URL:** `https://cf.nascar.com/live/feeds/live-flag-data.json`
- **Purpose/category:** Reported flag observations; `live`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:55.177982+00:00` → `2026-10-21T10:20:55.186492+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** global live path; may contain archived/inactive content. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## live-pits

- **Full URL:** `https://cf.nascar.com/live/feeds/live-pit-data.json`
- **Purpose/category:** Reported pit activity; `live`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:56.186624+00:00` → `2026-10-21T10:20:56.194506+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** global live path; may contain archived/inactive content. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## live-points

- **Full URL:** `https://cf.nascar.com/live/feeds/live-points.json`
- **Purpose/category:** Reported championship points; `live`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:57.194646+00:00` → `2026-10-21T10:20:57.202318+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** global live path; may contain archived/inactive content. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## live-stage-points

- **Full URL:** `https://cf.nascar.com/live/feeds/live-stage-points.json`
- **Purpose/category:** Reported stage points; `live`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:58.202458+00:00` → `2026-10-21T10:20:58.210035+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** global live path; may contain archived/inactive content. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## season-races

- **Full URL:** `https://cf.nascar.com/cacher/2026/race_list_basic.json`
- **Purpose/category:** Global season race and embedded session list; `schedule_reference`.
- **Series and URL context:** intended national series [1, 2, 3]; season=2026, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:20:59.210174+00:00` → `2026-10-21T10:20:59.219054+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [cup_schedule](#cup-schedule), [series2_schedule](#series2-schedule), [trucks_schedule](#trucks-schedule), [cup_races](#cup-races).
- **Integration dependencies:** Schedules, calendars, next race (Phases 1/2).
- **Fixture:** [schedule.json](../../tests/fixtures/nascar/schedule.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## drivers

- **Full URL:** `https://cf.nascar.com/cacher/drivers.json`
- **Purpose/category:** Driver reference directory; `schedule_reference`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:00.219194+00:00` → `2026-10-21T10:21:00.228225+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Favorite metadata (Phase 2).
- **Fixture:** [drivers.json](../../tests/fixtures/nascar/drivers.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## tracks

- **Full URL:** `https://cf.nascar.com/cacher/tracks.json`
- **Purpose/category:** Track reference directory; `schedule_reference`.
- **Series and URL context:** intended national series [1, 2, 3]; season=unknown, series_id=unknown, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:01.228386+00:00` → `2026-10-21T10:21:01.238139+00:00`; 10 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Optional track/calendar metadata (Phase 2).
- **Fixture:** [tracks.json](../../tests/fixtures/nascar/tracks.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## cup-schedule

- **Full URL:** `https://cf.nascar.com/cacher/2026/1/schedule-feed.json`
- **Purpose/category:** Cup session schedule; `schedule_reference`.
- **Series and URL context:** intended national series [1]; season=2026, series_id=1, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:02.238304+00:00` → `2026-10-21T10:21:02.250246+00:00`; 12 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Schedules, calendars, next race (Phases 1/2).
- **Fixture:** [session_schedule.json](../../tests/fixtures/nascar/session_schedule.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## series2-schedule

- **Full URL:** `https://cf.nascar.com/cacher/2026/2/schedule-feed.json`
- **Purpose/category:** Series 2 session schedule; `schedule_reference`.
- **Series and URL context:** intended national series [2]; season=2026, series_id=2, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:03.250577+00:00` → `2026-10-21T10:21:03.259175+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Schedules, calendars, next race (Phases 1/2).
- **Fixture:** [session_schedule.json](../../tests/fixtures/nascar/session_schedule.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## trucks-schedule

- **Full URL:** `https://cf.nascar.com/cacher/2026/3/schedule-feed.json`
- **Purpose/category:** Truck session schedule; `schedule_reference`.
- **Series and URL context:** intended national series [3]; season=2026, series_id=3, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:04.259370+00:00` → `2026-10-21T10:21:04.268335+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Schedules, calendars, next race (Phases 1/2).
- **Fixture:** [session_schedule.json](../../tests/fixtures/nascar/session_schedule.json) — handmade synthetic only. Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## cup-races

- **Full URL:** `https://cf.nascar.com/cacher/2026/1/race_list_basic.json`
- **Purpose/category:** Cup basic season race list; `schedule_reference`.
- **Series and URL context:** intended national series [1]; season=2026, series_id=1, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:05.268814+00:00` → `2026-10-21T10:21:05.276839+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** cached season/reference path; content age unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## weekend

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json`
- **Purpose/category:** Historical race weekend sessions/results; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:06.276982+00:00` → `2026-10-21T10:21:06.284852+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## lap-times

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/lap-times.json`
- **Purpose/category:** Historical lap timing; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:07.285159+00:00` → `2026-10-21T10:21:07.293400+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## lap-notes

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json`
- **Purpose/category:** Historical lap notes; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:08.293524+00:00` → `2026-10-21T10:21:08.301782+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## loop-stats

- **Full URL:** `https://cf.nascar.com/loopstats/prod/2024/1/5392.json`
- **Purpose/category:** Historical loop statistics; `historical`.
- **Series and URL context:** intended national series [1, 2, 3]; season=2024, series_id=unknown, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:09.302081+00:00` → `2026-10-21T10:21:09.309940+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## lap-averages

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json`
- **Purpose/category:** Historical lap averages; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:10.310062+00:00` → `2026-10-21T10:21:10.317823+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## archived-pits

- **Full URL:** `https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json`
- **Purpose/category:** Archived race pit activity; `historical`.
- **Series and URL context:** intended national series [1]; season=2026, series_id=1, race_id=5626, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:11.318162+00:00` → `2026-10-21T10:21:11.326363+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## archived-stages

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json`
- **Purpose/category:** Archived race stage points; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:12.326492+00:00` → `2026-10-21T10:21:12.334753+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## video-metadata

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/snappytv.json`
- **Purpose/category:** Video metadata only; no media requests; `historical`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:13.335056+00:00` → `2026-10-21T10:21:13.342992+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** race-specific historical path. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## legacy-live

- **Full URL:** `https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json`
- **Purpose/category:** Legacy race-specific live context; `legacy`.
- **Series and URL context:** intended national series [1]; season=unknown, series_id=1, race_id=5170, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:14.343123+00:00` → `2026-10-21T10:21:14.350697+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** legacy race-specific path; current-session coverage unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## legacy-points

- **Full URL:** `https://cf.nascar.com/live/feeds/series_1/5170/live_points.json`
- **Purpose/category:** Legacy race-specific points; `legacy`.
- **Series and URL context:** intended national series [1]; season=unknown, series_id=1, race_id=5170, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:15.351105+00:00` → `2026-10-21T10:21:15.359163+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** legacy race-specific path; current-session coverage unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## legacy-pits

- **Full URL:** `https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json`
- **Purpose/category:** Legacy race-specific pit activity; `legacy`.
- **Series and URL context:** intended national series [1]; season=unknown, series_id=1, race_id=5170, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:16.359305+00:00` → `2026-10-21T10:21:16.370552+00:00`; 11 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** legacy race-specific path; current-session coverage unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Future Phase 3B/4 only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## legacy-practice-averages

- **Full URL:** `https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json`
- **Purpose/category:** Legacy series 2 practice lap averages; `legacy`.
- **Series and URL context:** intended national series [2]; season=2019, series_id=2, race_id=4817, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:17.370830+00:00` → `2026-10-21T10:21:17.379659+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** legacy race-specific path; current-session coverage unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `working`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## driver-recap

- **Full URL:** `https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json`
- **Purpose/category:** Driver recap (non-core, previously error/login); `excluded`.
- **Series and URL context:** intended national series [1]; season=2024, series_id=1, race_id=5392, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:18.379800+00:00` → `2026-10-21T10:21:18.389070+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** excluded; behavior unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `error_login`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## drive-cup

- **Full URL:** `https://cf.nascar.com/drive/1/configs-ng.json`
- **Purpose/category:** Drive configuration (excluded; no token or playback investigation); `excluded`.
- **Series and URL context:** intended national series [1]; season=unknown, series_id=1, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:19.389376+00:00` → `2026-10-21T10:21:19.398807+00:00`; 9 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** excluded; behavior unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `error_login`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## drive-series2

- **Full URL:** `https://cf.nascar.com/drive/2/configs-ng.json`
- **Purpose/category:** Drive configuration (excluded; no token or playback investigation); `excluded`.
- **Series and URL context:** intended national series [2]; season=unknown, series_id=2, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:20.398941+00:00` → `2026-10-21T10:21:20.406934+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** excluded; behavior unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `error_login`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.

## drive-trucks

- **Full URL:** `https://cf.nascar.com/drive/3/configs-ng.json`
- **Purpose/category:** Drive configuration (excluded; no token or playback investigation); `excluded`.
- **Series and URL context:** intended national series [3]; season=unknown, series_id=3, race_id=unknown, run_id=unknown. All response identifiers unobserved.
- **Current accessibility:** `proxy_connect_denied`; proxy CONNECT status 403; origin HTTP status **not available**. No response content type or body.
- **Attempt:** `2026-10-21T10:21:21.407059+00:00` → `2026-10-21T10:21:21.415018+00:00`; 8 ms. Anonymous HTTPS GET, no cookies/credentials, TLS verification retained, no redirect/retry.
- **Behavior intent:** excluded; behavior unverified. Actual live/historical/cache/static behavior **unverified**.
- **Related endpoints:** [live_feed](#live-feed), [season_races](#season-races).
- **Integration dependencies:** Reference only; no production consumer.
- **Fixture:** none (no invented real sample). Real capture: **none**.
- **Limitations/validation:** owner report `error_login`; no current origin/schema/session observation. Experimental parser support, where present, is community-supported and synthetically tested; data permissions and allowed cadence remain unresolved.


## Phase 4A historical implementation

The seven explicit historical endpoint patterns, supported field models, distinct
availability/provenance states and request/retention limits are documented in
[the historical contract](../HISTORY.md). Production implements weekend-feed,
lap-times, lap-notes, loopstats/prod, lap-averages, archived live-pit-data and
archived live-stage-points through an independent on-demand provider. These are
observed examples, not verified coverage across years/series/races. There are zero
historical startup or ordinary scheduled detail requests. No alternate/legacy,
SnappyTV, recap or Drive historical request is added. No NASCAR network call was
performed in Phase 4A; original probe and imported snapshot evidence is unchanged.
See [Phase 4A validation](../PHASE4A_VALIDATION.md) for actual checks and unresolved gates.
