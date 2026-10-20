# NASCAR Race Center - Codex Development Specification

Repository: https://github.com/rosslandgraf/ha-nascar-race-center
Status: Planning / private development
Intended target: Home Assistant OS, custom integration, HACS-compatible public release only after permission and license review.
Domain: `nascar_race_center`
Date of user browser testing: 2026-10-20

## Mission
Build a mature, maintainable, user-configurable Home Assistant custom integration and an optional premium, responsive race dashboard for NASCAR. Support the three major national series (series IDs 1, 2 and 3), race weekend schedules, live race/session monitoring, favorite drivers, historical analytics, race event automations, and future HACS distribution. Avoid NASCAR login requirements for ordinary users **only where anonymous access and permission have been established**. No account credentials or secrets go in code, commits, or CI logs.

## Status of API access
The project owner manually opened 28 NASCAR CF URLs in a browser on October 20, 2026: **24 returned working data** and **4 resulted in Error/Login**. This is owner-reported browser testing, not independent automated verification. This does not establish permission to poll/distribute the data, anonymous accessibility from all networks, schemas, or live-session freshness. The primary provider is `https://cf.nascar.com` and **NOT** the credential-protected `https://feed.nascar.com` Swagger site.

### Owner-reported working URLs (24)
**Live (5)**
- https://cf.nascar.com/live/feeds/live-feed.json
- https://cf.nascar.com/live/feeds/live-flag-data.json
- https://cf.nascar.com/live/feeds/live-pit-data.json
- https://cf.nascar.com/live/feeds/live-points.json
- https://cf.nascar.com/live/feeds/live-stage-points.json

**Schedules, reference data (7)**
- https://cf.nascar.com/cacher/2026/race_list_basic.json
- https://cf.nascar.com/cacher/drivers.json
- https://cf.nascar.com/cacher/tracks.json
- https://cf.nascar.com/cacher/2026/1/schedule-feed.json
- https://cf.nascar.com/cacher/2026/2/schedule-feed.json
- https://cf.nascar.com/cacher/2026/3/schedule-feed.json
- https://cf.nascar.com/cacher/2026/1/race_list_basic.json

**Historical/statistical (8)**
- https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json
- https://cf.nascar.com/cacher/2024/1/5392/lap-times.json
- https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json
- https://cf.nascar.com/loopstats/prod/2024/1/5392.json
- https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json
- https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json
- https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json
- https://cf.nascar.com/cacher/2024/1/5392/snappytv.json

**Legacy/race-specific patterns (4)**
- https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json
- https://cf.nascar.com/live/feeds/series_1/5170/live_points.json
- https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json
- https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json

### Owner-reported error/login URLs (4): non-core / excluded unless clarified
- https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json
- https://cf.nascar.com/drive/1/configs-ng.json
- https://cf.nascar.com/drive/2/configs-ng.json
- https://cf.nascar.com/drive/3/configs-ng.json

**Note:** Do not automatically scrape or proxy NASCAR Drive video or infer access tokens. Historical race-specific response success does not prove race-specific endpoints still serve current live sessions. SnappyTV metadata working does not establish playback rights.

### Reference material to review critically
- https://github.com/ooohfascinating/NascarApi/blob/main/NewEndpointsDiscovered.MD
- https://github.com/TannerYohe/nascar-api
- Current official Home Assistant developer documentation at https://developers.home-assistant.io/ (may redirect)
- Current HACS publishing documentation at https://www.hacs.dev/docs/publish/integration/

## Technical architecture and conventions
1. Home Assistant UI config flow plus options flow with translations and validation. No required YAML editing. Single integration instance should ideally monitor selected series and multiple drivers with configurable options.
2. Async Python using Home Assistant's shared aiohttp session helper, typed transport and domain models, and `DataUpdateCoordinator` for deduplicated polls. Split infrequently changing schedule/reference metadata from fast-changing live data and one-off historical fetches. Minimize upstream calls.
3. NASCAR provider adapter with endpoint catalog, normalized models, parsing/validation tolerant of additional or missing fields, season/year and series routing, and automatic mapping between race/weekend/session IDs. Do not invent JSON fields. Keep data provider swappable.
4. Respect caching headers where applicable and prudent defaults: very low frequency off-season, moderate near a scheduled session, more frequent only when active and within documented/permitted use limits. Backoff for 429/503, timeouts, retry jitter, cancellation, last-known-good state and staleness indicators. No aggressive undocumented polling.
5. No schema assumption without captured, sanitized fixtures. The fixtures must be appropriately sourced and not contain restricted redistributable assets. When the data-use license is unresolved, favor minimal structural/handmade fixtures.
6. Preserve stable unique IDs based on series, NASCAR driver ID and session/race ID rather than just car numbers or display names. Treat unavailable data as `unavailable`/unknown, not fabricated zero readings. Entity and device registries must be coherent.
7. Expose essential sensors and binary sensors, calendar entities for future race weekends/sessions where suitable, and events that can drive native Home Assistant automations. Prevent duplicate events after polls, restarts, clock changes and event replay. Only expose lightweight entity attributes; keep full leaderboards in a dedicated card/data view rather than huge attributes or hundreds of history writes.
8. Avoid cloud secrets, sensitive headers, account access, and internal/private endpoints. No requirement for users to sign into NASCAR unless formally authorized and explicitly opted into a supported authenticated mode.
9. Optional custom Lovelace card in a separately organized frontend package. Provide installation/resource registration guidance and compatibility checks. Carefully distinguish integration HACS distribution from frontend card packaging. Respect accessibility, tablet and mobile layouts, loading/error/empty states.
10. Implement tests and automation-first QA. Use GitHub Actions with lint/type checks, pytest, hassfest and HACS validation where appropriate for a custom integration. Never claim successful checks without actual execution and links/results.

## Feature requirements
### A. Onboarding and options
- Series multi-select: NASCAR Cup (1), second-tier national series (2), Craftsman Truck Series (3). Adapt public-facing naming by season rather than hardcode a historical sponsor name.
- Favorite driver multi-select; per-series selection, clear naming, and options for enabling additional sensors/events.
- User preference for units/time formatting, but source datetimes internally timezone-aware. Calendar times reflect race track or user's Home Assistant timezone as configured.
- Diagnostics showing last successful update, current provider status, rate-limit status, latest session IDs and parsed field availability. Redact secrets and avoid exposing tokens.

### B. Schedules and sessions
- Next race and countdown; full season schedule; practice, qualifying and race start times; track name/location; postponement/rescheduling; stage and lap counts where supplied.
- Date/time zones and daylight-saving-safe handling; fallbacks for missing schedule fields; automatic new-season rollover.
- Series-aware calendar support and weekend schedule cards.

### C. Live race center
- Active race/qualifying/practice detection and session context, race status, current lap, laps remaining, flag state with flag change timeline, cautions, stage status and official results when available.
- Live standings with positions, car number, driver, team/manufacturer where available, gaps, intervals, speeds, last/best laps, laps led, running/retired statuses, and start-position change. Do not assume all these fields exist in every session; show graceful omissions.
- Favorite driver sensor group: position, movement, last/best lap, pit count and status when available.
- Live pit and stage points, championship point deltas where truly reported.
- Support current series from feed metadata; multi-series concurrent live sessions experimental until active-race validation.

### D. History and analytical views
- Past races and results, lap-by-lap data, caution/lap notes, lap-average comparisons, loop statistics, stage points and archived pit data.
- Filter by series, season, event and driver; display only facts present in data, with proper data availability notices.
- Racing analytics such as long-run pace, position progression and tire strategy only when derivable from validated fields; clearly label derived statistics.
- Historical recap feed is not core because it failed testing.

### E. UX/dashboard
- Full dashboard with overview, upcoming race/weekend, series selector, favorite driver cards, sortable live leaderboard, flag history, stage progress, pit data, championship standings, race analytics and history. Mobile, desktop and wall-tablet friendly.
- Distinguish no active session, feed stale, offline, denied, and not yet published results.
- Do not distribute NASCAR-controlled logos, photos or video content without appropriate authorization. Use neutral placeholders or user-supplied assets where appropriate.

### F. Automations
- Events: race scheduled soon, session started, green/yellow/red/checkered flag change, lead change, selected driver enters/leaves top N, pit stop, retirement, stage finish, race finish (only once), posted results, significant points movement where available.
- Debounce and event IDs; do not falsely trigger events from initial baseline fetch or restarting Home Assistant.
- Example blueprints for notifications and optional smart-light flag effects, with scene restoration and user opt-in. Keep core feed code completely independent of specific Hue, Ring or other integrations.

## Delivery and project management
Plan in focused, reviewable pull requests. Every PR must contain a scope explanation, tests, CI status, local validation steps, screenshots where applicable, known issues, and data-use assumptions.

**PR 1 - Foundation & feasibility:** README, legal/permissions note, explicit endpoint compatibility matrix (owner-reported vs verified by CI or manual), ARCHITECTURE, ROADMAP, CONTRIBUTING, AGENTS.md, license decision deferred, skeleton custom integration, config/option flow, coordinator with mocked provider, basic next-race/schedule/race-status/flag sensors, unit tests and basic CI. Only implement capabilities backed by actual schema validation. No production deployment.
**PR 2 - Full schedule and driver entities:** multi-series, calendars, favorite-driver selection, stable IDs, fixtures and tests.
**PR 3 - Live Race Center:** current standings, session lifecycle, flags, pits, stages, points and robust events; test using replayable fixtures without pounding live endpoints.
**PR 4 - History & analytics:** historical races/laps/loop stats, navigation, caching and derived metrics.
**PR 5 - Dashboard:** optional interactive custom cards, accessibility, responsive layout, packaging and documentation.
**PR 6 - Release readiness:** integration quality, end-to-end/replay tests, diagnostics, translation coverage, release automation, supported matrix, external beta and HACS checks when permissions established.

## Acceptance gates
- No real NASCAR credentials required for public base configuration; verify anonymous endpoints without existing login/cookies on a normal client (owner has NASCAR credentials, so browser tests alone are insufficient).
- Confirm service terms and explicit permission if needed **before public release, broad distribution, automated collection on real accounts, logo/media redistribution, or aggressive polling**. Public accessibility alone does not establish rights.
- Distinguish smoke-tested endpoints from verified JSON schemas and live-race behavior. Failures of optional feeds never disable core schedule/flag features.
- No credentials in the repository or GitHub Actions logs. No direct deployment to the owner's production Home Assistant without explicit review.
- All data-driven automated claims backed by fixtures/tests; test handling for no race, rescheduled race, overlapping series, pit/feed missing, cache old, schema drift, 429, 403, 404, 503, malformed/empty JSON, restart/replay and season boundary.
- Stable entity IDs after upgrades, configurable options, clean uninstallation and reconfiguration, no excessive Recorder storage usage.

## First Codex task
Read the repository and this specification. Research official Home Assistant and HACS requirements, validate documented NASCAR CF field shapes only where access and usage are allowed, create the architecture and plan, then implement PR 1 with tests. Do not begin PR 2+ until PR 1 has been reviewed. Open a pull request; do not merge directly to main. Report exactly what was tested and what remains unverified.
