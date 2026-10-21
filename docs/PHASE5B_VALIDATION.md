# Phase 5B validation

October 21, 2026 (America/New_York). Branch `phase5b-premium-dashboard`, based
on latest merged main / Phase 5A PR #11 squash
`fb8d8d0b4939ff1104acd35e67e35d8e683a426b`. Phase 5A is reviewed and merged.
This PR supplies only Phase 5B; no backend contract change was needed.

## Delivered behavior

The actual `nascar-race-center-card` custom Lovelace element has five connected
views, an in-UI editor/entry picker, stable sortable timing rows and favorites,
requested driver/scoring detail pages, retained schedules, manual historical
keys/datasets and backend analytics charts/summary comparisons. Authenticated
HA requests/subscriptions consume API v1; no separate socket/token manager exists.
The local versioned module builds independently from the Python integration; bundled MIT/BSD license notices accompany the standalone JS artifact.
[Installation, architecture, browser targets and detailed limits](FRONTEND.md)
provide a reproducible review path.

The production bundle contains Lit and original interface graphics, with no
runtime imports, remote fonts, provider URLs or preview fixtures. Tests distinguish
all data as fictional. The installed offline provider deliberately has no live
field/lap observations; the card displays its explicit empty states. The richer
browser preview is a separate test adapter over real serializer exports and
is never an integration fallback or production-bundle data source.

## Executed local checks

Prepared Python 3.14.8 / HA 2026.10.2 toolchain reused. Node 24.19.0, npm 11.9.0,
Lit 3.3.1, TypeScript 5.9.3, Playwright 1.56.1. All provider traffic in automated
checks is mocked. **Zero real NASCAR requests** were performed.

| Check | Executed result |
| --- | --- |
| Full existing Python suite before additions | **1,006 passed**, 55.88 s |
| Final full Python suite including frontend contract export/check | **1,007 passed**, 54.84 s |
| Ruff check / format | Passed; latest check covered 144 Python files |
| mypy integration | Passed; 44 source files |
| Official Hassfest, HA 2026.10.2 source | Passed; 1 integration, 0 invalid |
| Independent prepared actual-HA REST/state/service runtime test | **1 passed** |
| Prepared `hass --script check_config` | Passed, exit 0 |
| Frontend ESLint / Prettier | Passed |
| Frontend strict TypeScript | Passed |
| Vitest frontend unit/component tests | **54 passed**, 3 files |
| Playwright actual-card browser scenarios | **19 passed** |
| Axe WCAG 2 A/AA and applicable 2.1 AA checks | Zero reported violations in tested overview/timing/weekend/history/analytics and light-theme states |
| Versioned bundle build / size / no external imports or test-data checks | Passed |
| Production bundle actual browser render | Passed; 100 keyed timing rows, local-only preview requests |
| Committed bundle reproducibility | Passed locally after clean lockfile install, SHA-256 comparison and clean build-diff; also passed hosted CI |
| Git whitespace check | Passed |
| HACS integration validation | Existing private-repository skip and temporary brands exception retained; not full HACS approval |

Hassfest used official source `8d7fd8b68677c2585be36ec86043308f403875b8`
(HA tag 2026.10.2) in ignored `work/home-assistant-core`. Actual installed frontend
20260930.4 and its matching custom-card/entry-discovery source were inspected.
Executed hosted workflow results for the final implementation are recorded below.

## Automated coverage and actual API grounding

`tests/test_frontend_contract.py` creates an actual loaded demo entry and
administrator HA WebSocket client, exports bootstrap/live/schedule/driver/scoring/
history responses through production serializers, and uses actual Phase 4B
analytics over fictional normalized observations. Its schema check guards the
committed browser inputs against v1 drift. Regeneration is explicit via
`NRC_EXPORT_FRONTEND=1 pytest -q tests/test_frontend_contract.py`. Existing Python
WebSocket/pagination tests continue to exercise native authentication, all eight
commands, 50,028-history/79,324-analytics-row streams, zero continuation GETs,
snapshot slots, expiry, revocation, cancellation and Recorder boundaries.

The 54 frontend tests cover configuration/picker/editor/sizing, entry selection,
required envelopes/entry/version, HA result/event wrappers, IDs/car strings,
null/partial fields, safe errors, selected-series/freshness gates, favorites,
live updates, subscription disposal and delayed acknowledgement, race/session
changes, rapid switching and late callbacks, stable sorting, reconnect/bootstrap,
independent cards sharing one HA connection, disconnect cleanup, pagination/
source order/token/offset reuse, eight-page eviction/replay, changed/expired
snapshots, pacing/cancelled timers, date/number/DST formatting, null chart gaps,
position/delta/windows, backend summary bases, and conflict/sentinel exclusions. Final review added direct regressions preventing cross-race/run detail publication and substituted historical race keys.

Browser scenarios exercise the implemented card (source and committed production
bundle), meaningful navigation, historical selection, analytics queries and
continuations, median comparison, chart data-table/position controls, keyboard
focus/Enter/Escape driver disclosure, reduced-motion computed styles, denied and
stale/offline/unknown/no-session states, mobile analytics, light theme contrast,
tab reuse with no new snapshot, and expired-snapshot restart at offset zero.
The browser adapter is local/mock HA; actual authenticated HA WebSocket behavior
is exercised in the Python checks. A fully onboarded physical HA OS UI/companion
WebView installation was not performed or implied.

## Screenshots and responsive/accessibility findings

Every screenshot below is the actual Lit card, with fictional data and a visible
simulation label. No generated design mockups or controlled racing assets.

| View | Browser viewport | Actual screenshot |
| --- | --- | --- |
| Desktop overview | 1440 × 1100 | [Race Center](screenshots/phase5b/desktop-overview.png) |
| Desktop timing | 1440 × 1100 | [Live Timing](screenshots/phase5b/desktop-timing.png) |
| Small phone overview | 375 × 1100 | [Mobile Race Center](screenshots/phase5b/mobile-overview.png) |
| Large phone timing | 430 × 1000 | [Mobile timing tower](screenshots/phase5b/mobile-timing.png) |
| Tablet weekend | 834 × 1100 | [Race Weekend](screenshots/phase5b/tablet-weekend.png) |
| Wall dashboard | 1920 × 1200 | [Wall overview](screenshots/phase5b/wall-overview.png) |
| Historical results | 1440 × 1050 | [History](screenshots/phase5b/desktop-history.png) |
| Historical analytics | 1440 × 1150 | [Analytics and comparison](screenshots/phase5b/desktop-analytics.png) |

No page-wide horizontal overflow at the five requested representative widths.
The mobile tower preserves readable rows, prioritizes key fields and scrolls
measurements inside a labeled/focusable region; it does not shrink all columns.
Forms wrap at 375 px, including lap and window controls. Desktop/wall views
retain information hierarchy and spacing. Source/flag labels accompany colors.
Native keyboard controls, focus return, table sorting semantics, status/alert
regions and chart-equivalent tables are present. Reduced-motion disables
transitions/animations. HA color properties work with both tested dark and
light surfaces; automated axe scans reported no violations. Manual screen-reader,
additional-browser, physical-device and custom-theme coverage remains Phase 5C
review work, not an automated compliance claim.

## Performance and resource findings

See [machine-readable production measurements](screenshots/phase5b/measurements.json).
The synthetic Chromium measurement mounts the production module, then renders
20 pushed updates of **100 drivers**, awaiting both parent and keyed timing tower.
It includes no NASCAR latency. The first data-ready time includes the deliberate
370 ms client pacing interval and local test harness.

The current module is **129,262 bytes raw / 33,286 bytes gzip**, including Lit;
the bundle budget is 180,000 raw / 50,000 gzip bytes. `check:bundle` reports exact
bytes and rejects remote module imports, provider URLs or preview-data leakage.
The final recorded initial render was 5.5 ms; 100-driver updates averaged 1.825 ms
with a maximum of 27.9 ms. Other local runs varied with browser scheduling. Exact values from the
final run remain in the JSON artifact; these are not device/service guarantees.

Rows are keyed by string NASCAR ID. Unrelated HA entity updates do not request a
render. History renders at most one 200-record page; chart/source assembly retains
at most eight pages/1,600 records per open view. Two active selections/card are retained
without tab-triggered recreation. Server two-per-user/four-global slots remain
authoritative across all cards/tabs. Page offsets follow byte-budget-shortened
responses; previous evicted pages replay the same token. Changed stateless pages
are discarded. Expired/invalid snapshots require explicit restart; no retry loop.
No 50,000-row browser DOM, chart interpolation or new backend computation exists.

Live navigation maintains one selected-series subscription and clears timing
when leaving the live views, avoiding redisplay of an unobserved stale field.
Per-connection/entry commands are serialized/paced; sent requests remain HA-owned
and late results are discarded after selection/disconnection. No live/bootstrap/
schedule command triggers NASCAR refresh. Explicit history/analytics use existing
backend authorization, coalescing, HTTP/cache/request-floor and calculation budgets.

## Reproduction

```sh
source /workspace/.cloud-setup/nascar-race-center/activate.sh
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
cd frontend
npm ci --cache ../work/npm-cache
npm run lint
npm run typecheck
npm test
npm run build
npm run check:bundle
npm run test:browser
```

Other machines can use normal `npm ci` and Playwright's bundled Chromium as
explained in the frontend README. CI additionally verifies that rebuilding
changes no tracked bundle bytes, runs official integration workflows and uploads
browser screenshots/measurements as a retained artifact.

## Limits and Phase 5C follow-ups

Administrator-only API access, unverified source scales/finality/flags/coverage,
CF/data-use permission and conservative provider cadence are preserved. Valid
manual keys do not establish endpoint coverage across seasons. A driver ID above
JavaScript's safe integer bound remains displayable but cannot be sent losslessly
to v1's integer-only live-detail command; the card explains that refusal.

The server has no explicit snapshot-release command. Third/new selections can
encounter occupied slots until fixed expiry, including from other browser tabs;
forgetting a local view cannot release those resources. The UI explains waiting,
reuse and restart. Chart/page coverage is explicitly limited to loaded pages;
advancing far enough evicts early pages and their chart samples. Replaying an
evicted page requires a still-valid token. This preserves resource limits without
downloading every lap/window or presenting mixed selections as one complete race.

Phase 5C tasks: physical phones/tablets/wall devices and companion WebViews,
additional engines and assistive-reader/manual accessibility reviews, touch
column preferences, wall-density options, chart cursor/zoom and coverage navigation,
more specialized rare-record presentations and broader localization. Phase 6,
release/public HACS distribution, brands and live source permission gates remain
separate. No merge, deployment, HA OS installation, release, visibility change,
new public repository or NASCAR network request occurred in this phase.

## Hosted checks

The final implementation commit `39e524c` passed all three hosted PR workflows:

- [Python tests, Ruff and mypy](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39691960830): **success**.
- [Frontend lint, types, 54 tests, reproducible bundle and 19 browser scenarios](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39691960824): **success**, with uploaded browser artifacts.
- [Official Hassfest](https://github.com/rosslandgraf/ha-nascar-race-center/actions/runs/39691960833): **success**; the HACS job is **skipped** because repository visibility remains private.

These links pin executed implementation validation. Subsequent documentation/
screenshot-only commits run the same workflows; the current head's status is
visible in [PR #12 checks](https://github.com/rosslandgraf/ha-nascar-race-center/pull/12/checks).
No implementation check is inferred from configuration alone.
