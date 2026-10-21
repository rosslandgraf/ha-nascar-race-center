# Frontend: NASCAR Race Center card 0.5.0

Phase 5B supplies a working custom Lovelace card, consuming the merged Phase 5A
[dashboard API v1](DASHBOARD_API.md). The separately identified
[`frontend/`](../frontend/) package owns its lockfile, source, tests and versioned
local ES module. Python integration packaging, cadence, entities, Recorder,
automation and authentication behavior are unchanged.

## Manual development installation

The user performs these steps on a development HA installation. Nothing in the
repository installs files on HA OS or changes dashboards/resources automatically.

1. From a checkout containing Phase 5A and 5B, use Node 24 and `cd frontend &&
   npm ci && npm run build`. The committed bundle may also be used directly.
2. Manually create `<HA config>/www/nascar-race-center/` and copy
   `frontend/dist/nascar-race-center-card-0.5.0.js` into that directory. On HA OS,
   `<HA config>` is ordinarily `/config`; use the installation's supported file
   editor or file transfer method. Do not copy `node_modules`, `demo` or tests.
3. With an administrator account, open **Settings → Dashboards → Resources**
   (enable Advanced Mode in the profile if necessary). Add a **JavaScript Module**
   resource with URL:
   `/local/nascar-race-center/nascar-race-center-card-0.5.0.js`.
   YAML-managed resource users add that same URL with `type: module` to their
   existing resource list. Do not add the resource twice.
4. Reload the browser, edit a dashboard and choose **NASCAR Race Center** from the
   custom-card picker. Use its editor to select the loaded integration entry,
   initial monitored series, initial view and optional title. Save the card.
5. As a manual alternative, use the configuration below. Copy the exact
   `entry_id` from the editor's authenticated entry selector/manual-ID field;
   do not infer it from entity names. The empty default card opens an entry
   chooser. Use the editor to persist an entry selection in Lovelace.

```yaml
type: custom:nascar-race-center-card
entry_id: YOUR_LOADED_INTEGRATION_ENTRY_ID
series_id: 1
section: Race Center
title: NASCAR Race Center
```

`entry_id` selects a loaded NASCAR integration entry. Every API command requires
it. `series_id` is optional (1/2/3); the first monitored series is the default,
and an unmonitored configured series falls back to the first monitored series.
`section` is one of Race Center, Live Timing, Race Weekend, History, Analytics.
Favorites remain read-only and are configured through integration options.

HA API v1 deliberately requires an active **administrator**, even if the user
can view sensor entities. The card explains denied/missing/unloaded-entry and
version errors. It never obtains tokens or opens its own socket.

A wide/Sections dashboard is recommended: the card advertises full columns,
auto rows and a conservative minimum size through `getGridOptions`; masonry
receives `getCardSize() = 10`. The editor, `setConfig`, `hass` lifecycle,
`getStubConfig`, default config and custom-card picker registration are included.

## Views and evidence boundaries

- **Race Center:** selected series, current fresh session and matching cached race
  metadata, next known event/session, reliable countdown, leader, lap/stage
  observations, favorites and source health/content timestamp. Current metadata
  is looked up by race ID; an upcoming race's track is never substituted for an
  unmatched live race. Explicit-offset future instants alone support countdowns.
- **Live Timing:** full normalized field (up to 100 drivers), stable keyed sortable
  rows, favorites, car strings, starts, derived position change, raw gap/times/
  speeds, completed laps, running status and pit-observation count. Open a driver
  for requested pit stops or laps-led intervals; associated pits/stages/points
  use their own supported detail command. Scoring remains provisional.
- **Race Weekend:** retained race/session catalog, localized confirmed instants,
  unknown-time labels, enrichment/source failures and available cached track
  metadata. Continuation pages retain parent race IDs, including pages beginning
  inside a preceding event's session collection. Select a race to fill History.
- **History:** explicit series/season/race key and dataset controls, retained race
  suggestions and manual keys, reported results table and per-page expandable
  metadata/session/stage/lap/note/pit/loop/average observations. An explicit valid
  key does not certify historical endpoint coverage. Missing results stay unknown.
- **Analytics:** explicit 1–8 NASCAR IDs, inclusive lap range, optional supported
  5/10/15/20/25/30-lap windows and comparison basis. Charts show backend lap-time,
  position, consecutive-delta or rolling-window observations. Metric cards use
  backend values, classification, method, unit and reason directly. Pairwise
  comparisons, fastest/mean/median metrics, stage/race/session performance and
  loop/average fields have interactive summary-comparison bars and a bounded record explorer. Only identical metric/method/unit/source-group bases are compared; conflicting or candidate-sentinel values stay unavailable in charts.

Timing and speed units remain unverified; the UI never appends seconds or mph
without a contract basis. Source status codes and flags retain unknown meanings.
A checkered observation is not an official final classification. Archived
reported date labels remain labels, not certified instants. No unsupported tire,
sector, strategy, rating, finality or championship conclusions are generated.
Dataset evidence retains identity validation, coverage, delivery and retry hints.

## Transport, pagination and lifecycle

`api.ts` is the single typed client for all eight commands. It uses `hass.callWS`
and `hass.connection.subscribeMessage`, includes entry/API version on every
request, handles HA result/event envelopes and errors, validates scope, page
boundaries and versions, and imports leaf declarations from
`docs/DASHBOARD_API_MODELS.d.ts`. Additional TypeScript interfaces describe the
actual v1 envelopes/record unions; they are not a new backend contract.
Identifiers remain strings in responses. Requests convert IDs only when their
integer bounds and JavaScript safe-integer representation hold. A live driver ID
above `Number.MAX_SAFE_INTEGER` is displayed but its detail request is refused
explicitly rather than rounded; history/analytics IDs are already bounded lower
by API v1.

One live subscription serves the selected series while Race Center/Live Timing
is visible. Switching between these two views reuses it; leaving them releases
it and clears current timing. Returning waits for a new snapshot. Series/config/
connection changes invalidate generations and discard late callbacks/results.
Revisions are local to one subscription. Unsubscribe acknowledgements are
serialized so rapid switching/removal cannot leave a late subscription behind.
Ready/disconnected listeners recover from bootstrap; disconnect invalidates
connection-bound snapshots. Terminal entry-unavailable events show an actionable
reconnect state. The card clears pacing/countdown timers, listeners and local
views on removal. HA owns cancellation/cleanup of sent WebSocket work: the
frontend cannot cancel an individual `callWS` request and discards a late result.

Each page requests at most 200 rows and trusts the server's explicit next offset,
including byte-budget-shortened pages. `PageView` retains at most eight pages
(1,600 records); source-order assembly sorts page offsets and never merges
changed snapshots. Previous pages use cached state or replay the same immutable
token/offset if evicted. Only the current history page (200 rows) is rendered;
charts/accessibility tables use at most the retained 1,600 rows, with visible
loaded-page scope. Null values and missing lap numbers break lines. The browser
never reconstructs absent observations or interpolates chart gaps.

At most two history/analytics selections are retained per card. Submitting the
same exact selection reuses it; rendering and tab switching create no snapshots.
A different third selection explains capacity and asks the user to reuse/wait.
The actual **two-per-user/four-global** server budget applies across all cards,
users/entries and browser tabs; local state cannot override it. Snapshots expire
five minutes after server construction; the card also bounds local continuation
age and handles earlier server invalidation. Expired cached historical records
remain explicitly labeled; restart starts from offset zero without the old token.
There is no release endpoint: forgetting local state cannot release a server
slot; closing the shared HA socket solely for this purpose would disrupt HA and
is not performed. Capacity errors, fixed expiry and request-floor/backoff outcomes
have explicit retry/restart actions with no automatic retry loop.

Requests are serialized and paced at least 370 ms apart per connection/entry,
shared by independent card clients (under 30 commands/10 seconds). Other tabs
and HA clients still share the server's authoritative limits. No render operation
requests data. Schedule pages are cached on demand; a current live race can
trigger one cached, filtered schedule read for matching metadata. Historical
retrieval/analytics occur only on explicit submission and pagination. Live details
occur only on explicit opening. No NASCAR refresh/poll, new endpoint, entity or
Recorder row is introduced. Existing backend services retain their request,
coalescing, cache, cancellation, upstream authorization and cadence ownership.

## Components, build and compatibility

| Module | Responsibility |
| --- | --- |
| `src/card.ts` | Lovelace lifecycle, selection/navigation, five view compositions |
| `src/editor.ts` | Supported configuration editor and authenticated entry discovery |
| `src/api.ts` | Eight commands, envelope/selection checks, request pacing and errors |
| `src/types.ts` | Typed v1 envelope/record unions; shared leaf-model imports |
| `src/state.ts` | Immutable selection pages, token offsets, retention and generations |
| `src/format.ts` | Explicit-offset dates/countdowns, HA locale/time-zone/number-format support, stable sorting |
| `src/components/leaderboard.ts` | Stable keyed timing rows, sorting, favorite/driver disclosure |
| `src/components/chart.ts` | Bounded SVG charts, gaps, data-table equivalent |
| `src/components/metric-chart.ts` | Interactive backend summary/race/stage/loop/average metric comparisons |
| `src/components/records.ts` | Result tables, metric definitions and evidence/record disclosure |
| `src/styles.ts` | Theme-aware surfaces, typography, focus, container breakpoints, reduced motion |

Node 24 + lockfile provides `npm ci`; `npm run lint`, `npm run typecheck`,
`npm test`, `npm run build`, `npm run check:bundle`, `npm run test:browser` are
reproducible commands. In the restricted prepared cloud environment use `npm ci --cache ../work/npm-cache` to keep the cache in the workspace. CI checks committed-bundle reproducibility and uploads
actual-card screenshots/measurements. Test adapter/fixtures live only in
`frontend/demo`; a Python HA contract test exports/rechecks synthetic projections.

Compatibility: card 0.5.0 ↔ dashboard API v1 from merged PR #11 (`fb8d8d0`).
Inspected installed HA **2026.10.2** / frontend **20260930.4**, including
[custom-card interfaces](https://github.com/home-assistant/frontend/blob/20260930.4/src/panels/lovelace/types.ts)
and [entry discovery](https://github.com/home-assistant/frontend/blob/20260930.4/src/data/config_entries.ts).
No private HA frontend imports or external helper dependency are used.

Target current evergreen browsers with custom elements, Shadow DOM, ES2022,
Resize/container CSS and `color-mix` (Chrome/Edge 111+, Firefox 113+, Safari 16.4+;
actual validation uses installed Chromium, not a claim of tested coverage for
every target). No legacy browser polyfill/download is supplied.

## Accessibility, responsive behavior and distribution

The card inherits HA foreground, secondary text, accent, surface, radius and
shadow properties. Color mixing keeps status/movement text readable on light
and dark surfaces. Flag/status text accompanies color; graphics are original CSS
shapes. Native buttons/selects/forms, visible focus, labeled scroll regions,
sortable-header `aria-sort`, keyboard driver opening/Escape/close focus return,
status/alert regions and chart data tables support keyboard and assistive use.
Reduced-motion disables animations/transitions. Container queries respond to the
actual card width; phones prioritize position/car/driver/start/status and expose
measurements by horizontal scrolling or driver disclosure. See validation for
375/430/834/1440/1920 px screenshots and automated axe findings.

This is manual development distribution, **not** a HACS dashboard-plugin release.
The repository's existing `hacs.json` still describes the Python integration.
`frontend/package.json`, versioned `dist` and documentation make the card build
independently identifiable. A future separately reviewed plugin packaging/release
workflow must establish appropriate HACS dashboard assets/metadata/repository
rules. No second repository, public release, resource auto-registration or
visibility change is made here. MIT remains code-only; no NASCAR logos, photos,
sponsor graphics, video, remote fonts or controlled media are included.

Phase 5C follow-ups: physical-device/HA companion WebView and assistive-reader
reviews; additional browsers/theme combinations; touch column preferences and
wall-display density; richer record-specific presentation for rare datasets;
chart cursor/zoom and page-coverage navigation; localization beyond English.
These are polish/coverage tasks, not claims of completed Phase 5C work.
