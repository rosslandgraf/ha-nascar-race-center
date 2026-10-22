# Phase 5C validation

October 21, 2026 (America/New_York). Development branch
`phase5c-dashboard-polish`, based on latest merged main / Phase 5B PR #12 squash
`177f81cab64edd6a01b35ecb3ec363e1c01504fa`. Card **0.5.1** consumes the unchanged
authenticated dashboard **API v1**. Python behavior and shared API declarations
are unchanged. No NASCAR requests, production HA access, deployment, publication,
merge, visibility change or Phase 6 work are included.

## Delivered refinements and before/after behavior

| Area | Phase 5B | Phase 5C |
| --- | --- | --- |
| Navigation/layout | Horizontally scrolling phone navigation; one panel density | Five visible wrapping phone destinations; per-card comfortable/compact density; clearer selected underline and headings |
| Overview | Large decorative hero; sparse wide field context | Quieter charcoal hero, consistent panels, compact progress, shaped/text flags and five-driver wide overview strip |
| Mobile timing | Duplicate favorite column; gap easily offscreen | Essential identity/context/gap columns; optional extra measurements; pinned position/car/driver; stable column widths and scrolling headers |
| Timing controls | Sort semantics and driver opening | 44 px driver/sort controls, Arrow Up/Down/Home/End, announced sorts, correct Enter/Escape/Close focus return and context-change recovery |
| Chart exploration | Native SVG titles plus table | Selectable driver legends, hover/tap cursor, native observation selector, previous/next and announced exact values; nulls remain inspectable |
| Sparse/missing observations | Nulls break paths | Same disconnected paths; centered single observations; all-null series retain an accessible table without a fabricated plot |
| Historical records | Generic nested fields | Reported finishing order, record-type filtering, lap/flag/pit/stage/loop/average summaries and scoring metric tables; complete wrapper/namespace fallback |
| Snapshot navigation | Previous/next and tab retention | Paging before long records/charts, cached-page chooser, retained History/Analytics selections and explicit loaded record ranges |
| Formatting/performance | New Intl formatter for each cell | Bounded 32-entry locale/precision formatter cache; HA number preferences also reach results, metric cards and nested records |
| Browser verification | 19 Chromium scenarios | 53 scenarios configured for Chromium, Firefox and WebKit; local/hosted execution distinguished below |

The new tests found and fixed two concrete defects: driver-open custom events
previously lost the originating button, preventing focus return; long metric
options could overflow inside a narrow card despite no page-wide overflow.
The tests now check both viewport and card scroll widths. Column sorting copies
observations; position change remains relative to starting position, never a pass.
Driver details remain tied to series/race/timing-run generations.

Snapshot reuse creates no command or new snapshot. Expired selections remain
labeled cached observations, with explicit offset-zero restart. Capacity UX
explains the two-per-user/four-global server budget. Local clearing never claims
to release a slot; API v1 has no release command. No history prefetch/retry loop,
new live subscription, provider endpoint, polling cadence or racing formula is
introduced. Missing units, finality and source coverage remain unverified.

## Executed checks

Prepared Python 3.14.8, HA 2026.10.2, installed frontend 20260930.4, Node 24.19.0,
Lit 3.3.1, TypeScript 5.9.3 and Playwright 1.56.1. All test racing observations
are fictional synthetic contracts. The real offline provider remains deliberately
empty for unsupported live/lap observations.

| Check | Result |
| --- | --- |
| Full Python suite | **1,007 passed**, 67.81 s |
| Ruff check / format | Passed; 144 files formatted |
| mypy integration | Passed; 44 source files |
| Official Hassfest | Passed; 1 integration, 0 invalid; HA tag 2026.10.2 source `8d7fd8b68677c2585be36ec86043308f403875b8` |
| Prepared actual HA REST/state/service runtime test | **1 passed**, 0.18 s |
| Prepared HA configuration check | Passed, exit 0 |
| Frontend ESLint / Prettier / strict TypeScript | Passed |
| Frontend unit/component suite | **68 passed**, including all 54 Phase 5B tests |
| Chromium browser suite | **53 passed**, 1.7 minutes |
| Firefox / WebKit local execution | Unavailable: browser download domains denied with HTTP 403 `Domain forbidden` |
| Production build / transfer budget / fixture exclusion | Passed; exact measurements below |
| Clean-lockfile bundle reproducibility | Passed; identical SHA-256 after offline lockfile reinstall/rebuild |
| Git whitespace / backend-contract diff | Passed; no backend/API declaration changes |
| Hosted GitHub Actions | Exact results/links recorded below |
| HACS | Existing private-repository skip and brands exception retained; not full approval |

Local Chromium is **154.0.8037.57** on Linux. The Playwright default projects run
Chromium, Firefox and WebKit; `NRC_BROWSERS=chromium` explicitly selects the local
available subset. CI installs all three engines and uploads engine-specific
artifacts. Configuration alone is not a claim that an engine passed.

## Coverage and screenshots

The 53 browser scenarios retain every Phase 5B assertion and add touch column
controls, pinned identity, focus return, orientation changes, chart keyboard/
hover/touch inspection, missing observations, loaded-page and selection reuse,
capacity exhaustion, rapid series/run changes, reconnect, independent cards,
100-driver updates, cleanup, 15 minutes of virtual idle, editor discovery,
light/forced colors, reduced motion, text enlargement and 200% CSS zoom/reflow.

Viewport matrix: **320, 375, 390, 430, 480, 768, 834, 1024, 1280, 1440, 1920 px**.
Each timing/weekend/overview scenario checks actual card boundaries, then constrains
an overview to a **320 px** card in the same viewport. Analytics independently
checks 320/375/390/480/834 px containers and long summary metric options. Phone
landscape is **844 × 390**. Full-width wall capture removes the preview's normal
1500 px cap, exercising a **1864 px card** inside a 1920 px viewport. Other preview
cards use the screenshot viewport minus page padding, capped at 1500 px; they are
not mislabeled as viewport-wide cards.

Actual browser-rendered card screenshots, with visible fictional demonstration
labels and original UI graphics:

| View/state | Viewport | Chromium evidence |
| --- | --- | --- |
| Small phone Race Center | 320 × 900 | [Overview](screenshots/phase5c/chromium/phone-overview.png) |
| Small phone timing | 320 × 900 | [Timing](screenshots/phase5c/chromium/phone-timing.png) |
| Phone landscape timing | 844 × 390 | [Landscape](screenshots/phase5c/chromium/phone-landscape.png) |
| Tablet Race Center | 768 × 1024 | [Tablet overview](screenshots/phase5c/chromium/tablet-overview.png) |
| Tablet Race Weekend | 834 × 1112 | [Weekend](screenshots/phase5c/chromium/tablet-weekend.png) |
| Desktop timing, compact | 1440 × 1100 | [Timing](screenshots/phase5c/chromium/desktop-timing.png) |
| Desktop analytics | 1440 × 1100 | [Analytics](screenshots/phase5c/chromium/desktop-analytics.png) |
| Full-width wall Race Center, compact | 1920 × 1200 | [Wall](screenshots/phase5c/chromium/wall-overview.png) |
| Light theme timing | 640 × 900 | [Light](screenshots/phase5c/chromium/light-theme.png) |
| Loading | 1280 × 720 | [Loading](screenshots/phase5c/chromium/loading.png) |
| Stale | 390 × 900 | [Stale](screenshots/phase5c/chromium/stale.png) |
| No active session | 390 × 900 | [No session](screenshots/phase5c/chromium/no_active_session.png) |
| Unavailable source | 390 × 900 | [Unreported](screenshots/phase5c/chromium/not_reported.png) |
| Offline | 390 × 900 | [Offline](screenshots/phase5c/chromium/offline.png) |

Compared against committed [Phase 5B screenshots](PHASE5B_VALIDATION.md): small
phones now expose all navigation destinations and prioritize useful gap/context
information over a duplicate favorite column; primary timing identity stays
visible during measurement scrolling. Wide overview favorites no longer stretch
to a neighbor's height, the hero is more compact, and the reported front-five
strip adds glanceable field context. Charts now expose exact/missing values
without requiring hover or opening a table. The 5B scenario captures remain in
ignored `work/phase5b-regression/`; baseline committed screenshots are preserved.

## Accessibility findings and limits

Zero axe violations were reported in the tested states. Automated axe WCAG 2 A/AA and applicable 2.1 AA scans cover overview, timing,
weekend, history, analytics, source states and light surfaces. Scans are automated evidence only. Keyboard regressions cover driver movement, disclosure focus,
context changes, chart selection, sorting semantics and focus visibility. Flag
shapes accompany text; missing values remain explicit. Plot and table scroll
regions have labels and keyboard focus. New controls use approximately 44 px
minimum targets. High-contrast/forced-color selection borders and reduced-motion
rules are exercised.

**No VoiceOver, TalkBack, physical phone/tablet/wall display, HA OS dashboard or
companion WebView was available or tested.** The runtime test exercises actual
HA fixtures, authentication/REST/state/services; the browser harness mocks the HA
frontend transport over real serializer fixtures. It is not an onboarded physical
HA frontend acceptance session. CSS zoom 200% and equivalent narrow reflow are
automated proxies; browser chrome zoom and OS text scaling remain manual checks.
The inline details region is deliberately nonmodal, with no modal focus trap.
Automated axe results do not establish manual WCAG compliance or screen-reader
usability. English source labels are centralized for new controls; complete
translation catalogs are not implemented.

## Bundle, performance and cleanup

The versioned module is `frontend/dist/nascar-race-center-card-0.5.1.js`; no runtime
imports, NASCAR URLs, preview adapters, fixture observations or remote fonts are
bundled. Lit and license notices remain included. The Phase 5B baseline was
**129,262 raw / 33,286 gzip bytes**; budget remains **180,000 / 50,000 bytes**.
Final exact sizes and SHA-256 are recorded below. Growth covers interaction,
responsive styles, record presentation and accessibility without a chart library.

[Production stress measurements](screenshots/phase5c/chromium/performance.json)
measure **100 changed updates of 100 keyed drivers with two independent cards**,
including real changed measurement cells. They record mean/max elapsed update
time, available Chromium heap usage, row count, idle commands and removed
subscriptions/listeners. The Phase 5B-style single-card 20-update scenario also
runs. Its repeated same row-array workload is lighter than the changed-cell,
two-card stress case, so their timings are not directly interchangeable.
A bounded cache reuses Intl number formatters instead of constructing one per
cell. All locale/number preference regressions still pass.

History DOM remains one current page of at most 200 rows; charts retain at most
eight pages/1600 records. The source subscription count remains one per visible
live card, with no extra NASCAR requests. Fifteen minutes of virtual idle adds
no commands or snapshots. Cleanup assertions remove all mock live subscriptions
and ready/disconnected listeners. Heap measurements are observations, not proof
of a long-duration memory plateau or a physical-device frame-rate guarantee.

## Reproduce

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
# Prepared local engine:
NRC_BROWSERS=chromium npm run test:browser
# Full matrix on a host permitting Playwright downloads:
npx playwright install --with-deps chromium firefox webkit
CHROMIUM_PATH=bundled npm run test:browser
```

## Physical-device and Phase 6A acceptance checklist

Use an explicitly authorized development installation with the existing offline
provider or synthetic fixture harness. These steps were not performed on the
owner's HA system. Record device, OS, browser/app, HA/frontend/card versions,
locale/theme, actual card width, result and screenshot/reader notes for each row.

- [ ] Install the versioned module manually using [frontend instructions](FRONTEND.md); verify picker, editor entry selection, initial view/series and save/reload. Run in a narrow masonry card and full-width HA Sections layout; add two independent cards.
- [ ] On iPhone Safari and the iOS companion app at 320–430 CSS px, exercise every destination, series selector, column disclosure, horizontal timing scroll, driver tap/Close and rotation. Confirm no page scrolling sideways or clipped names/controls.
- [ ] Repeat on Android Chrome and the Android companion app at 360–480 CSS px; check touch scrolling and native selection menus, including missing car numbers and very long names.
- [ ] On iPad Safari and an Android tablet, check portrait/landscape at 768/834/1024 px and a 320 px embedded card. Confirm weekend session times, favorites, timing rows and analytics controls fit their actual containers.
- [ ] On an authorized wall-display browser at 1280/1440/1920 px, choose Compact, confirm flags/lap/leader/favorites/front-five are glanceable, then inspect a 100-driver tower. Leave open at least two hours, recording memory, CPU, responsiveness and absence of extra provider calls before/after.
- [ ] With VoiceOver, navigate headings/landmarks, selected navigation, sort controls, driver actions and chart inspector/table. Verify sort/value/status announcements are understandable, not repetitive, and Escape/Close return focus to the correct driver.
- [ ] Repeat with TalkBack, including swipe order, double-tap activation and reading explicit unavailable/missing observations. Record any duplicate labels or unreachable controls.
- [ ] With a physical keyboard, test Tab/Shift-Tab, visible focus, driver arrows/Home/End, Enter/Escape, chart selectors/buttons and loaded-page/selection navigation. Confirm context changes recover focus and never show a previous run's details.
- [ ] Use browser chrome zoom at 200%, OS text enlargement and long localized labels in light/dark and custom high-contrast themes. Check focus outlines, flag text, row numbers, summary labels and both orientations. Enable reduced motion.
- [ ] Choose HA locales with decimal-comma, comma-decimal and space-comma numbers; switch 12/24-hour clocks and timezone around DST. Confirm only explicit-offset instants are localized and historical source date labels remain unchanged.
- [ ] Load History and Analytics for a valid explicit key, page forward/back and reuse retained selections. Wait beyond five minutes, attempt continuation and restart; exhaust two per-user/four-global slots using authorized test clients and confirm no automatic retry or false release claim.
- [ ] Interrupt and restore the development HA connection; rapidly change monitored series and timing runs; remove/re-add both cards. Confirm subscriptions/listeners/timers clean up, old details disappear and cached snapshots are not reused across connections.

Phase 6 readiness remains open for these physical/assistive-reader checks,
translations, HA OS/companion integration acceptance, cross-context source units/
identity/finality/coverage, NASCAR data-use and polling permission, public asset
review, HACS brands/private-repository constraints and separate integration/card
release packaging. No gate is closed by synthetic screenshots or passing CI.

## Final local measurements

- Bundle: **148,577 bytes raw / 37,292 bytes gzip**, including license notices.
  Growth over 5B is 19,315 raw / 4,006 gzip bytes (about 14.9% / 12.0%), below
  the unchanged transfer budgets. Clean lockfile reinstall/build reproduced
  SHA-256 `0493f49939734ca1b77e8d36d168c2b2b0f8b24139f0a32b838f50fe7600d9f1`.
- The [single-card Phase 5B-style scenario](screenshots/phase5c/chromium/single-card-performance.json)
  averaged **0.915 ms**, maximum **11.2 ms** for 20 pushed 100-driver updates;
  the committed 5B measurement averaged 1.825 ms / maximum 27.9 ms. First render
  was 12.2 ms and data-ready 811.7 ms including deliberate command pacing.
- The stricter two-card / 100 changed updates measured **2.103 ms mean / 4.9 ms
  maximum**, with **100 stable keyed rows**, **2 subscriptions**, **0 idle
  commands**, and **0 subscriptions/listeners remaining after removal**.
  Chromium reported 6,797,542 used JS heap bytes at the observation point.
  Before the formatter cache the same local stress scenario averaged about
  28 ms; these observations vary with scheduling/GC and are not device guarantees.
- Final local frontend: **68 unit/component tests and 53 Chromium browser
  scenarios passed**. Automated scans reported **zero violations** in the
  exercised dark/light/view/state combinations. Full backend: **1,007 passed**.

## Hosted review checks

The original PR-creation browser limitations are superseded by the WebKit
correction and local matrix evidence below. Final-head hosted workflow results
are linked from [PR #13](https://github.com/rosslandgraf/ha-nascar-race-center/pull/13/checks).
No physical-device acceptance is claimed.

## WebKit overflow correction — October 22, 2026

This follow-up continues PR #13 on `phase5c-dashboard-polish` from committed
head `00ee3a3`; it supersedes the earlier local browser-download limitation.
WebKit **26.0**, Playwright build **2215**, downloaded successfully from
`cdn.playwright.dev` and launched/rendered locally on Debian 13. The host lacks
root/sudo access, so missing Debian runtime libraries were downloaded and
extracted under ignored `work/` and copied into the browser's local `sys/lib`
directories. The local launch used `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`
because Playwright checks the system `ldconfig` cache for GLES, which does not
list workspace libraries. The actual GLES library loaded and WebKit rendered;
no browser assertions or repository configuration were bypassed. WebKit and
Chromium first ran with the execution sandbox's network grant for local
browser/server sockets. The initial combined run completed Chromium
54/54, then stalled at Firefox startup because the nested command sandbox
blocked `/proc/self/uid_map` writes (`EROFS`). A standalone Firefox launch
succeeded outside that nested sandbox without disabling Firefox sandbox
features. The complete matrix was then run outside the nested command sandbox;
no test/configuration changes were made for that launch issue.

### Reproduction and computed-style diagnosis

The unmodified targeted test passed with this host's default OpenAI Sans font.
Selecting **DejaVu Sans**, the wider Linux font, reproduced the hosted failure
exactly before the CSS change: at a **320 px viewport**, preview padding leaves
a **304 px card**, whose `ha-card.scrollWidth` was **320 px**. The added font
variant failed the existing card-width assertion before the fix.

[Computed-style measurements](PHASE5C_WEBKIT_OVERFLOW.json) record the native
`white-space: pre` baseline and corrected layout. Both the Known retained race
and Metric and measurement basis selects already had **236 px border boxes**,
`width: 236px`, `min-width: 0px`, `max-width: 100%`, and parent grid tracks of
**236 px**. Nevertheless, the labels had scroll widths of **285 / 287 px**.
WebKit's native nonwrapping selected text contributed overflow outside the
correctly constrained select/grid boxes. Wider glyphs made this reach the card
boundary; further grid/fieldset minimum-width changes did not address it.

The shared select rule now sets **`white-space: normal`**, allowing the native
selected text to wrap within the existing control. Both labels then have
**236 px client/scroll widths**; the card's inner scroll width is **302 px**
inside its **304 px border box**. The selected text visibly wraps:
[before](screenshots/phase5c/webkit-select-before.png) and [after](screenshots/phase5c/webkit-select-after.png). Native appearance,
complete option labels, keyboard selection, focus styles, and intentional
chart/table scrolling remain.
Direct experiments with `text-overflow: ellipsis`, `overflow: hidden`, and
`white-space: nowrap` did not fix the parent-label overflow. No extra clipping,
relaxed width allowance, test retry, timeout increase, or skipped test was added.

The regression retains every original viewport/card/select assertion and adds
a DejaVu Sans variant plus direct scroll-width checks on both labels at all five
existing analytics widths. The targeted WebKit regression ran first and passed
**2/2** after the fix. The full matrix now contains **54 scenarios per engine**.

### Follow-up validation

Frontend ESLint/Prettier, strict TypeScript, **68 unit/component tests**, build,
and bundle-budget/fixture-exclusion/license checks passed. The rebuilt 0.5.1
module is **149,263 bytes raw / 37,506 bytes gzip**, SHA-256
`dd23b8e40704f7d5b0766d5d8ac12816c08e19832e241e8d75616fd2591dae2c`.
These measurements supersede the earlier pre-correction bundle measurements.
Fresh Python validation also passed: Ruff lint/format, mypy (44 source files),
and **1,007 tests in 79.22 s**. The Python suite ran outside the nested command
sandbox so the HA fixtures could create local sockets.

The complete local matrix passed **162/162 scenarios in 4.8 minutes** after
that targeted regression, with no retries or failures:

| Engine (Playwright 1.56.1 bundled builds) | Complete suite |
| --- | --- |
| Chromium 141.0.7390.37 / build 1194 | **54 passed** |
| Firefox 142.0.1 / build 1495 | **54 passed** |
| WebKit 26.0 / build 2215 | **54 passed** |

All original 53 scenarios per engine remain; the additional font variant brings
each engine to 54. Automated accessibility checks are included in these suites.
Generated full-matrix captures/logs are retained under ignored `work/`; the two
focused native-select screenshots and computed-style evidence are committed.

Final-head hosted workflow results are linked from
[PR #13's checks](https://github.com/rosslandgraf/ha-nascar-race-center/pull/13/checks).
The existing HACS private-repository skip and brands exception remain. This
correction makes no backend/API, endpoint, source-data, polling, licensing or
packaging change; all existing data-use assumptions and physical-device/manual
acceptance limits above remain open. No merge, deployment or Phase 6 work.
