# Phased implementation roadmap

The complete [brief](NASCAR_Race_Center_Codex_Brief.md) defines the target product. Each phase is a focused pull request with its own acceptance gate. Phase 2 and later begin only after Phase 1 review. This roadmap includes planned work and must not be read as a feature list of the current implementation.

## Phase 1 — Foundation and feasibility

**Deliverables:** repository development instructions, architecture, endpoint/evidence matrix, permissions note, contributing guide, UI configuration/options, selected-series foundation, typed models, async provider transport, offline demonstration, experimental CF adapter, separate schedule/live coordinators, basic next-race/schedule/status/flag/lap entities, diagnostics, mocked tests, and CI.

**Engineering decisions:** one entry; demo by default; no NASCAR login; explicit authorization before CF requests; source parsing isolated from HA entities; immutable models; stable series IDs; lightweight attributes; independent live/schedule failures; no automation events emitted from unvalidated session transitions.

**Acceptance:** actual Home Assistant fixtures exercise setup, options and unload; provider tests use handmade structural responses with recorded provenance; meaningful tests cover unknown/no-race data, selected-series routing, rescheduling/time boundaries, malformed schemas, cache and error handling. Ruff, mypy and pytest run locally; Hassfest/HACS status is reported with any exceptions. Restored runtime is checked without re-onboarding. Open a PR, do not merge or deploy.

**Unresolved feasibility gates:** anonymous direct CF access from a normal client, real live-session schema/freshness, permission and permitted polling cadence. A passing mocked suite proves implementation behavior, not these gates. See the validation report accompanying the PR for actual results.

## Phase 2 — Complete schedules and favorite drivers

**Depends on:** Phase 1 review and evidence for additional schedule/reference shapes.

**Work:** normalize race/weekend/session IDs; practice, qualifying and race times; track/location metadata; full schedules and calendars; postponements and next-season rollover; driver reference cache; per-series favorite-driver selection; optional entity groups and unit/time preferences. Extend translation coverage and preserve existing IDs.

**Acceptance:** fixtures cover all three series, ambiguous/missing times, DST, year boundary, postponed sessions, overlapping weekends and driver/car changes. Calendar times and entity availability are exercised through HA. Driver IDs survive display-name and car-number changes. Failures of reference feeds do not disable core schedules.

## Phase 3 — Live Race Center and automation events

**Depends on:** validated active-session feeds and documented allowed polling behavior.

**Work:** live standings, driver movement/gaps/speeds/last and best laps; race/session detection; current/remaining laps; flags/cautions; pit activity; stage results; reported championship points/deltas; favorite-driver timing/status; data-source capability indicators. Treat concurrent live sessions as experimental until directly observed.

**Automation work:** opt-in session/flag/lead/top-N/pit/retirement/stage/race/result/points events; stable event IDs; debounce; persistent deduplication ledger; initial-baseline suppression; restart/replay recovery. Add notification and optional scene-restoring light blueprints independent of vendor integrations.

**Acceptance:** replay scenarios prove exactly-once user-visible transitions across repeated polls/restarts/replays and no false event from first data. Feed omissions, clock changes, stale CDN snapshots and series switches are explicit. Optional pit/stage/points failure leaves schedule/flag essentials usable. Recorder write volume is measured.

## Phase 4 — History and analytical views

**Depends on:** validated historical schemas and data-use review for storage/retention.

**Work:** on-demand past results, laps, lap notes, lap averages, loop statistics, archived stage/pit data; season/series/race/driver navigation; bounded caches and retention; source provenance and availability. Add position progression, long-run pace and strategy comparisons only when fields support defensible formulas. Exclude failed driver-recap endpoints unless evidence changes.

**Acceptance:** fixture-based numerical checks document formulas and sample limits. Unknown and unpublished results differ from network failure. Cross-season/race IDs never collide. No startup bulk history download or accidental unbounded storage.

## Phase 5 — Optional dashboard and Lovelace cards

**Depends on:** stable integration models/data-view interface, independent frontend packaging plan, and authorized assets.

**Work:** overview/upcoming weekend, series selector, favorites, sortable leaderboard, flags/stages/pits, standings, history and analytics; accessible controls, keyboard support, tablet/mobile layouts, reduced motion, loading/empty/denied/offline/stale states. Use neutral or user-supplied assets. Document resource registration and version compatibility.

**Acceptance:** browser/accessibility tests and screenshots at phone, desktop and wall-tablet sizes; large data views avoid state-attribute inflation; card distribution and integration distribution validated independently. No media proxying, restricted logos, photos or video included.

## Phase 6 — Beta and release readiness

**Depends on:** reviewed prior phases and resolved public distribution/data permissions.

**Work:** supported HA/Python matrix; upgrade/migration/uninstall checks; replay/end-to-end tests; diagnostics/redaction audit; translation coverage; polling/cache/storage budgets; authorized branding submission; external beta; release notes; security reporting; integration/card release automation and HACS documentation.

**Acceptance:** no HACS exceptions, passing Hassfest/HACS and full CI, documented live observations and compatibility limits, confirmed terms/permissions and asset rights, beta sign-off, explicit owner approval before public release or production installation. CI must not auto-publish merely because tests pass.

## Release blockers carried between phases

| Gate | Current state | Resolution required |
| --- | --- | --- |
| Data rights and polling limits | Unresolved | Owner review and documented permission where required |
| Anonymous direct endpoint access | Owner browser reports only | Controlled unauthenticated probe with evidence |
| Live race/session behavior | Unverified | Authorized active-session observation and replay fixtures |
| Historical schemas and derived analytics | Planned | Per-endpoint source evidence and numerical tests |
| Dashboard/card packaging | Planned | Separate frontend artifact and compatibility validation |
| HACS brands requirement | Deferred | Authorized neutral branding submission; remove CI exception |
| Production/release approval | Not granted | Explicit owner authorization after review |
