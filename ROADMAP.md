# Phased implementation roadmap

The complete [brief](NASCAR_Race_Center_Codex_Brief.md) defines the target product. Phases 1 through 5C are reviewed and merged into `main`, including PR #13 (`ec35f25`) and the observed API reference package. Phase 6A starts from that merge and preserves its 1,007-test Python baseline, adding two acceptance journeys. Each phase has an acceptance gate; planned later work is not a feature list of the current implementation.

The post-installation beta correction was merged in PR #15, separately from Phase 6B:
[snapshot/empty-state validation](docs/SNAPSHOT_FIX_VALIDATION.md) and
[0.1.0 / 0.5.1 update/rollback](docs/SNAPSHOT_FIX_UPGRADE.md). The
0.1.1 / 0.5.2 pair fixes confirmed owner-reported usability defects without
changing provider, polling, household configuration or the release gates.

The subsequent [CF-readiness candidate](docs/CF_READINESS_VALIDATION.md) starts
from merged PR #15 (`68e917e`), improves all-series/session source assessment and
conservative non-race polling, and prepares an [owner-operated authorized test](docs/CF_OWNER_ACCEPTANCE.md).
It does not complete source permission/live acceptance gates or begin Phase 6B.

The next focused [bundled packaging candidate](docs/HACS_DISTRIBUTION.md) starts
from merged PR #16 (`7ca9d4d`). Integration 0.2.0 includes card 0.6.0 in one HACS
Integration download, with stable resource setup and an [owner migration guide](docs/HACS_MIGRATION.md).
It prepares public distribution without publishing it or completing Phase 6B.

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

**Status:** reviewed and squash-merged in PR #3. See
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

## Phase 3B — Live pits, stages and reported championship points

**Status:** reviewed and squash-merged in PR #5; evidence-limited features retain their validation gates. See
[validation](docs/PHASE3B_VALIDATION.md) and [field/association blockers](docs/PHASE3B_EVIDENCE.md).

**Delivered:** embedded NASCAR-ID pit observations and current stage; normalized
standalone pit activity, stage results/points, championship positions and reported
race/championship scores; source provenance and strict race/run/namespace/time
validation; independently failing shared optional feeds; compact race/favorite
sensors; offline demo and stable configuration/IDs; synthetic and real-HA coverage.

**Evidence boundary:** global pits lack race/driver identity; stages report another
race and lack series/source time; points report zero IDs. Those datasets remain
unavailable for live association and are not automatically requested. Capability
is `unsupported_association`; parsers/models and future integration interfaces
remain available. No fabricated totals, scoring formulas, completed-stage/stop
counts, pit time units, rank movement or official finality.
Live permission/cadence and active-session acceptance remain open. Readiness for
code review does not mean those data gates are satisfied.

## Phase 3C — Racing events, notifications and automations

**Status:** reviewed and squash-merged in PR #6. See the
[validation checks](docs/PHASE3C_VALIDATION.md); live-session gates remain open.

**Delivered:** opt-in typed event engine over existing normalized live/schedule
models; silent setup/restart/reconnect/switch baselines; bounded durable
high-water marks and event IDs saved before publication; fresh-evidence gates;
upcoming reminders, verified start, flags, lead/favorite top-N and embedded pit
observations; one observed checkered completion per session; translated options;
notification and optional scene-restoring lighting blueprints; synthetic replay
and actual Home Assistant lifecycle/storage/automation tests.

**Limits:** no official results, retirements, stage finishes or championship
movement events; no new endpoints or faster polling. Active-session semantics and
physical-device testing remain unverified. Event publication never directly
notifies users or controls devices. History acquisition remains Phase 4.
See [event behavior and blueprint setup](docs/EVENTS.md).

## Phase 3D-A — NASCAR CF provider compatibility

**Status:** reviewed and squash-merged in PR #7; offline validation passed. Live acceptance gates remain open.
See [corrections/evidence/checks](docs/PHASE3DA_VALIDATION.md) and the future
[authorized HA OS validation procedure](docs/CF_LIVE_VALIDATION.md).

**Scope:** compare production parsers to observed structures; preserve unknown
codes and numeric team values without assigning meanings; reject contradictory
schedule enrichment; distinguish transport, JSON, parsing and usable HA data;
add synthetic structural and real HA regressions. Preserve polling, demo,
Phase 1–3C behavior and unresolved permission/live-session gates.

## Phase 3D-B — Adaptive near-real-time polling

**Status:** reviewed and squash-merged in PR #8. See
[polling and permission policy](docs/POLLING.md) and
[actual validation/budgets](docs/PHASE3DB_VALIDATION.md).

**Delivered:** provider-gated 10-second race/practice/qualifying capability;
30–60-second approach discovery, five-minute session gaps, hourly idle/overnight
and six-hour off-season targets; source-clock/failure backoff; shared request
slots, server caching/304/Retry-After safeguards; compact persisted CF restart
reservations; translated options and bounded diagnostics. Existing sensors,
event meanings, entity IDs and configuration version remain compatible.

**Permission boundary:** CF defaults and legacy discovery budgets remain guarded
at 300 seconds or slower. Adaptive options and data-use acknowledgements cannot
enable fast CF access. The offline demo remains empty unless a test explicitly
supplies synthetic activity. Measured synthetic performance establishes capability,
not authorized NASCAR cadence or real-world latency. No new NASCAR probes,
standalone scoring requests, history or dashboard work.

## Phase 4A — Historical data foundation

**Status:** reviewed and squash-merged in PR #9, `907e5bba46d5017836a074197e68fd26a3093b69`. See the [internal contract](docs/HISTORY.md) and [actual validation](docs/PHASE4A_VALIDATION.md).

**Delivered:** typed immutable, evidence-limited weekend/results/sessions, laps/flags,
object-keyed notes, loop metrics, lap averages and archived pit/stage data; independent
on-demand provider/broker; full season/series/race keys and separate run namespaces;
strict validation, partial availability, compact provenance, bounded isolated memory,
conditional HTTP/backoff, deduplication and entry-owned cancellation/cleanup.
Zero historical startup or scheduled detail requests; offline fictional demo remains.

**Gates:** single observed examples do not establish cross-season/series coverage.
No publication/finality, timing units, pit-driver join or undocumented sentinel
meaning is invented. Data-use, authorized current-source and live acceptance gates
remain open. No NASCAR requests, persistent raw archive, dashboard or analytics.

## Phase 4B — Historical analytics and comparisons

**Status:** reviewed and squash-merged in PR #10, `926e6693be9250de5a2716d7d799fba901385a11`.
See the [internal API/formulas](docs/ANALYTICS.md) and
[actual validation](docs/PHASE4B_VALIDATION.md).

**Delivered:** immutable recorded-lap/time/position series, coverage/gaps, exact
mean/median/extrema, population consistency, contiguous rolling windows, explicit
all-available/common-valid-lap comparison bases, pairwise numerical differences,
reported result/stage/loop/average/session rows and independent provenance/failure
states. `entry.runtime_data.analytics` reuses HistoryService on demand and bounds
executor work, concurrent requests and output. No startup/periodic history work,
extra Recorder rows, frontend or authenticated transport is introduced.

**Gates:** source units, conditions, sentinel meanings, official classification,
cross-context historical coverage and NASCAR data-use remain unverified. No tire
strategy, pit-driver join, rating formula, invented score or championship standings.
Phases 5A–5C are merged. Phase 6A beta procedures are prepared for review below; Phase 6B and public release remain deferred.

## Phase 5A — Authenticated dashboard data interface

**Status:** reviewed and squash-merged in PR #11 (`fb8d8d0b4939ff1104acd35e67e35d8e683a426b`). See the
[dashboard API v1](docs/DASHBOARD_API.md), its documented TypeScript model
projections and [executed validation](docs/PHASE5A_VALIDATION.md).

**Delivered:** native authenticated administrator-only HA WebSocket commands for
cached bootstrap, retained schedule navigation, live projections/subscriptions,
paged embedded/scoring details and on-demand history/analytics. Entry/user/client
resource limits, source freshness notifications, coalescing/deduplication,
snapshot-checked continuation, finite explicit serializers and lifecycle cleanup
preserve existing upstream, events, entity IDs and Recorder boundaries.

**Remaining:** real NASCAR latency/source/data-use gates, broader permission
policy if separately authorized, and the visual frontend. Phase 5B below implements the separate frontend against API v1. Phase 5C owns additional polish and device/accessibility reviews. No deployment or release is authorized.

## Phase 5B — Functional premium Lovelace dashboard

**Status:** reviewed and merged in PR #12 (`177f81c`) from merged Phase 5A. See [frontend installation/architecture](docs/FRONTEND.md) and [actual validation/screenshots](docs/PHASE5B_VALIDATION.md).

**Delivered:** independently built/versioned local Lit card, picker/editor and explicit entry selection; five connected views; full sortable live field and favorites; requested detail disclosure; retained race weekends/manual historical keys; progressive history and backend analytics with bounded gap-preserving SVG charts; administrator/error/freshness/demo states; responsive phone/tablet/desktop/wall layouts, keyboard controls and reduced motion.

**Boundaries:** one selected-series subscription; authenticated HA transport only; exact immutable snapshot offsets, two retained selections and eight cached pages/view; no NASCAR polling, backend contract change, new entities/Recorder rows, controlled assets, production installation or resource registration. Frontend CI/lockfile/versioned bundle are separate from existing integration/HACS packaging.

**Remaining:** physical-device/assistive-reader acceptance, broader localization and rare-record presentation. NASCAR rights, active-source units/semantics, public HACS packaging and release gates remain open. Phase 5C is merged below; Phase 6A prepares the controlled offline beta.

## Phase 5C — Dashboard refinement and expanded verification

**Status:** reviewed and merged in PR #13 (`ec35f25`) from Phase 5B. See
[Phase 5C validation](docs/PHASE5C_VALIDATION.md) for executed checks, screenshots,
measurements and explicit limitations. Deployment and release remain unperformed.

**Delivered:** card-local comfortable/compact density; responsive five-view
navigation; pinned, accessible timing identity/columns; keyboard driver movement
and focus recovery; interactive SVG observation inspection including missing data;
visible loaded-page coverage and cached navigation; retained History/Analytics
selection reuse; specialized historical summaries preserving namespace/provenance;
English source labels and expanded number/date preference coverage. Card 0.5.1
remains a separately versioned reproducible local module over API v1.

**Acceptance limits:** browser rendering and mocked lifecycle checks do not close
physical-device/HA OS/companion WebView or VoiceOver/TalkBack acceptance. Those
remain exact manual [Phase 6A checklist](docs/PHASE6A_BETA_CHECKLIST.md) items,
alongside translations, source rights/semantics/cadence and separate HACS distribution gates.

## Phase 5 — Premium Dashboard and dedicated data interface

**Depends on:** stable integration models/data-view interface, independent frontend packaging plan, and authorized assets.

**Work:** a dedicated authenticated Home Assistant data interface for larger live/history views, plus overview/upcoming weekend, series selector, favorites, sortable leaderboard, flags/stages/pits, standings, history and analytics; accessible controls, keyboard support, tablet/mobile layouts, reduced motion, loading/empty/denied/offline/stale states. Use neutral or user-supplied assets. Document resource registration and version compatibility.

**Acceptance:** browser/accessibility tests and screenshots at phone, desktop and wall-tablet sizes; large data views avoid state-attribute inflation; card distribution and integration distribution validated independently. No media proxying, restricted logos, photos or video included.

## Phase 6A — Controlled offline beta readiness

**Status:** prepared for independent review from merged Phase 5C. See the
[installation guide](docs/PHASE6A_INSTALLATION.md),
[checkable acceptance matrix](docs/PHASE6A_BETA_CHECKLIST.md),
[update/rollback procedure](docs/PHASE6A_ROLLBACK.md) and
[executed validation](docs/PHASE6A_VALIDATION.md).

**Delivered:** compatibility/security/lifecycle review; pinned runtime artifact
hashes; full-backup verification and independent recovery prerequisites;
conflict-safe manual integration/resource installation and separate dashboard;
accurate production-demo expectations; observational household/CPU/memory/Recorder/
browser baselines; explicit NOT TESTED physical/device/accessibility acceptance;
two actual-HA authenticated demo install/options/reload/removal smoke journeys.
Production behavior, API permissions, source authorization and card 0.5.1 are unchanged.

**Gates:** owner installation/restart approval, actual HA OS compatibility,
backup/recovery verification and all unperformed owner/device checks remain open.
Readiness to attempt an offline beta does not require or establish CF/data/public
release permission. No owner installation, deployment, UniFi change, merge,
release, visibility change or HACS publication is included. Phase 6B is not begun.

## Phase 6 — Beta and release readiness

**Depends on:** reviewed prior phases; public distribution/data permissions must be resolved before the public release portion. Phase 6A offline preparation is scoped separately above.

**Work:** supported HA/Python matrix; upgrade/migration/uninstall checks; replay/end-to-end tests; diagnostics/redaction audit; translation coverage; polling/cache/storage budgets; authorized branding submission; external beta; release notes; security reporting; integration/card release automation and HACS documentation.

**Acceptance:** no HACS exceptions, passing Hassfest/HACS and full CI, documented live observations and compatibility limits, confirmed terms/permissions and asset rights, beta sign-off, explicit owner approval before public release or production installation. CI must not auto-publish merely because tests pass.

## Release blockers carried between phases

| Gate | Current state | Resolution required |
| --- | --- | --- |
| Data rights and polling limits | Unresolved | Owner review and documented permission where required |
| Anonymous endpoint and active-session access | Supplied single-snapshot observations; this environment blocked | Authorized current-session observation with identity/time provenance |
| Live race/session behavior | Unverified | Authorized active-session observation and replay fixtures |
| Historical source coverage and analytics | Phase 4A merged; Phase 4B merged numerical analytics, cross-context coverage unverified | Authorized per-context source/units/conditions evidence; retain formula/sample/provenance limits |
| Dashboard/card packaging | Single Integration bundle candidate, 0.2.0 / 0.6.0 | Public distribution approval and physical migration acceptance |
| Full HACS validation | Action rejects private repositories | Validate after an explicitly approved public-distribution decision; do not change visibility merely to pass CI |
| HACS brands requirement | Original local NRC icon; exception removed | Full official validator on approved public repository; owner asset approval |
| Production/release approval | Not granted | Explicit owner authorization after review |


## Persistent final-objective completion checklist

Update this checklist in every phase. Checked items describe implemented code;
source/live/data-use and release gates above still apply.

- [x] Foundation, offline demonstration, stable IDs and independent coordinators (Phase 1, merged).
- [x] Multi-series race/session schedules and native calendars (Phase 2, merged; timestamp/status limits documented).
- [x] Favorite-driver selection, metadata and live timing (Phases 2/3A, merged).
- [x] Live NASCAR timing, normalized leaderboard and provisional session progress (Phase 3A, merged).
- [x] Embedded pits/current stage and evidence-gated pit/stage/points models/sensors (Phase 3B, merged).
- [ ] Validate standalone live pit/stage/points association, completed stops/stages and official results against reliable evidence.
- [x] Opt-in reliable racing events and notification/lighting blueprint implementation (Phase 3C, merged).
- [x] CF provider compatibility and pipeline diagnostics (Phase 3D-A, merged).
- [ ] Authorized HA OS end-to-end CF acceptance (live source and permission gates remain open).
- [x] Adaptive polling capability and synthetic request/Recorder budgets (Phase 3D-B, merged PR #8).
- [ ] Independently verify permitted CF cadence and real active-session latency before faster CF activation.
- [ ] Validate active-session event semantics and physical-device automation behavior.
- [x] On-demand historical results/laps/notes/loop/average/pit/stage foundation with bounded memory and provenance (Phase 4A, merged PR #9).
- [x] Defensible derived analytics/comparisons and bounded internal consumer API (Phase 4B, merged PR #10).
- [ ] Historical cross-context coverage, source units/conditions and semantic acceptance.
- [x] Authenticated dedicated dashboard transport v1 (Phase 5A, reviewed and merged).
- [x] Functional premium dashboard and separate frontend package (Phase 5B, merged).
- [x] Responsive/interaction polish and expanded automated verification (Phase 5C, merged PR #13).
- [x] Controlled offline beta installation, backup, rollback and automated acceptance preparation (Phase 6A, for review).
- [ ] Physical devices, assistive-reader acceptance and remaining Phase 6A matrix (see Phase 6A checklist).
- [ ] Owner HA OS beta installation/acceptance and household reliability sign-off (Phase 6A manual tests NOT TESTED).
- [ ] Remaining Beta & Release Readiness: beta feedback, translations and release workflows (later separately authorized Phase 6 work).
- [ ] Public HACS distribution: bundled candidate prepared; official public validation, asset/privacy review and explicit publication authorization remain open.
