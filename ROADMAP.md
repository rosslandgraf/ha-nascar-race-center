# Phased implementation roadmap

The complete [brief](NASCAR_Race_Center_Codex_Brief.md) defines the target product. Phases 1 and 2 were reviewed and squash-merged into `main`, with 243 passing tests at the Phase 2 baseline. Phase 3A starts from `fb88120` on its own feature branch. Each phase has an acceptance gate; planned later work is not a feature list of the current implementation.

## Phase 1 — Foundation and feasibility

**Status:** reviewed and merged. Its entities, settings, IDs and regression protections remain supported.

**Deliverables:** repository development instructions, architecture, endpoint/evidence matrix, permissions note, contributing guide, UI configuration/options, selected-series foundation, typed models, async provider transport, offline demonstration, experimental CF adapter, separate schedule/live coordinators, basic next-race/schedule/status/flag/lap entities, diagnostics, mocked tests, and CI.

**Engineering decisions:** one entry; demo by default; no NASCAR login; explicit authorization before CF requests; source parsing isolated from HA entities; immutable models; stable series IDs; lightweight attributes; independent live/schedule failures; no automation events emitted from unvalidated session transitions.

**Acceptance:** actual Home Assistant fixtures exercise setup, options and unload; provider tests use handmade structural responses with recorded provenance; meaningful tests cover unknown/no-race data, selected-series routing, rescheduling/time boundaries, malformed schemas, cache and error handling. Ruff, mypy and pytest run locally; Hassfest/HACS status is reported with any exceptions. Restored runtime is checked without re-onboarding. Open a PR, do not merge or deploy.

**Unresolved feasibility gates:** anonymous direct CF access from a normal client, real live-session schema/freshness, permission and permitted polling cadence. A passing mocked suite proves implementation behavior, not these gates. See the validation report accompanying the PR for actual results.

## Phase 2 — Complete schedules and favorite drivers

**Status:** reviewed and merged, with structural mocks and community-supported adapter contracts. See [VALIDATION.md](docs/VALIDATION.md) for executed checks. Current anonymous CF response shapes and source semantics are not independently verified.

**Delivered:** immutable race/session models; full retained season schedules across all three series; optional practice/qualifying/race enrichment; per-series native calendars with date-range weekend entries and explicit unknown-duration notices; rescheduling and season rollover; typed driver/track references; multiple favorites keyed by NASCAR driver ID; searchable UI selectors and metadata entities; isolated slow reference updates; backward-compatible entry defaults and Phase 1 identifiers.

**Acceptance:** fixtures cover all three series, ambiguous/missing times, DST, year boundary, postponed sessions, overlapping weekends and driver/car changes. Calendar times and entity availability are exercised through HA. Driver IDs survive display-name and car-number changes. Failures of reference feeds do not disable core schedules.

**Evidence limits:** no source timezone is inferred from naive timestamps, including fields named `start_time_utc`. CF cancellation/postponement status fields and authoritative session IDs are not supported by current community evidence. Normalized status handling is available for providers that can identify it; current CF adapters apply published schedule revisions without claiming explicit cancellation detection. Internal session IDs survive time/order changes but may change when the source renames a session. General driver directories do not establish an active roster, and media URLs are not manufacturer metadata. Phase 2 itself delivered no live favorite-driver positions or timing; Phase 3A adds those below. Event automations, production installation and release remain deferred.

## Phase 3A — Live race timing and leaderboards

**Status:** implemented on its own review branch. See
[Phase 3A validation](docs/PHASE3A_VALIDATION.md) for actual checks and evidence
limits. Direct active-session validation and documented provider polling/data-use
permission remain open gates; synthetic development does not close them.

**Delivered:** typed normalized reported field with ordered traversal and driver-ID
lookup; driver identities, positions, starting-position change, last/best laps,
reported gap and speed fields, laps completed and laps-led intervals; run context,
leader, reported current/total/remaining laps, flags and evidence-limited progress;
compact favorite metrics on stable Phase 2 driver devices; per-series routing of
one global source; diagnostic field counts and scoring-failure isolation.

**Reliability:** the existing shared live coordinator/transport and minimum
polling bounds remain. No new CF endpoint or per-driver/series polling loop.
Stale/failed fields cannot supply current scoring. Unknown source time or flag
cannot establish active/completed progress. Favorite position alone is enabled
by default. Full fields stay in bounded runtime memory. Actual Recorder checks
measure unchanged samples and a changed favorite, alongside actual HA lifecycle
and synthetic transition/error/cache tests.

**Limits:** community structural contracts only; timestamp, status, gap and
laps-led aggregation semantics remain evidence gates. Completion means a fresh
checkered observation, not final official classification. Only status 1 maps
to running. The in-memory normalized leaderboard has no custom dashboard/API.
No pits, stages, points, automation events, historical storage, public release
or production deployment is included.

## Remaining Phase 3 assignments — not started

Pit-stop tracking, stage scoring, championship points and automation events
remain for later assignments (3B/3C). Their implementation requires per-endpoint
evidence and appropriately sourced structural/replay fixtures. Later event work
must implement opt-in delivery, persistent deduplication, initial-baseline
suppression and restart/replay protection before exposing any events or
notification/light blueprints. The Phase 3A `LiveView`/reported run identity
boundary is available for reuse; it contains no hidden event ledger or inferred
pit/stage/points behavior.

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
| Full HACS validation | Action rejects private repositories | Validate after an explicitly approved public-distribution decision; do not change visibility merely to pass CI |
| HACS brands requirement | Deferred | Authorized neutral branding submission; remove CI exception |
| Production/release approval | Not granted | Explicit owner authorization after review |
