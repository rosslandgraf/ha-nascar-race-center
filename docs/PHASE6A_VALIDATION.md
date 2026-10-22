# Phase 6A — beta readiness validation

October 22, 2026 (America/New_York). Branch `phase6a-beta-readiness`, starting from
latest merged `main`, Phase 5C / PR #13 squash
**`ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972`**. The signed commit and runtime
file identities were verified. This phase changes documentation and acceptance
tests only; it does not change production Python, frontend source/bundle, API
permissions, provider policy or persisted formats.

**Finding:** no code/packaging blocker was identified for an owner-approved,
manual **Demonstration-only** installation on the tested Core baseline. This is
readiness to attempt a controlled beta, not owner acceptance. Owner Core/OS
compatibility, backup/recovery verification, maintenance-window approval and
household checks are required installation gates. They remain **NOT TESTED**.
Administrator-only dashboard access and deliberately empty demo live data are
intentional constraints. No owner's HA OS, HP hardware, UniFi configuration,
physical browser/app, backup or assistive reader was accessed or changed.

## Deliverables and review scope

- [Installation](PHASE6A_INSTALLATION.md): beginner sequence, compatibility,
  full backup verification, pinned files/hashes, conflict checks, manual resource,
  separate dashboard, demo entry/favorites and expected offline behavior.
- [Beta checklist](PHASE6A_BETA_CHECKLIST.md): automated evidence separated from
  exact future owner/device procedures; CPU, memory, Recorder, startup, browser,
  lifecycle, accessibility, household control and two-hour observations.
- [Rollback/update](PHASE6A_ROLLBACK.md): separate card and integration recovery,
  complete version replacement, caching, identity and migration limits, removal
  and explicit approval before full-system restoration.
- [Runtime SHA-256 manifest](PHASE6A_ARTIFACTS.sha256): **48** production files
  from the pinned candidate, including translations and the built module.
- `tests/test_beta_smoke.py`: two real Home Assistant fixture-server journeys,
  using production demo providers and native authenticated WebSocket operations.
  The existing CI pytest step discovers them; no new CI/live-network job is needed.

Read before choosing scope: AGENTS, full project brief, roadmap, architecture,
README, frontend/API v1 documents and all Phase 5 validation reports. The API
library/catalog/field evidence and fixture provenance preserve synthetic versus
observed distinctions; this phase makes **zero NASCAR requests**. Endpoint
evidence and data-use assumptions are unchanged. MIT applies to code only.

## Compatibility and installation inspection

| Area | Inspected result and practical consequence |
| --- | --- |
| Manifest | Domain `nascar_race_center`, version `0.1.0`, `config_flow: true`, `single_config_entry: true`, service integration; no pip `requirements` or declared integration dependencies |
| Runtime baseline | Python 3.14 required by `pyproject.toml` and modern syntax; tested 3.14.8 / Core 2026.10.2 / HA frontend 20260930.4; `hacs.json` minimum 2026.10.2; no earlier/newer Core or HA OS/Supervisor compatibility claim |
| Flow/options | Unique installation key is the domain; config flow VERSION 1/default minor 1, no custom migration; options reload the same entry; CF requires Boolean explicit authorization |
| Entity identity | Registry-scoped entry ID + series/metric or NASCAR driver ID/metric; no driver-name/car-number keys. Same entry preserves IDs through reload/options/compatible file update. Delete/re-add does not preserve entry identity |
| Demo isolation | Separate in-memory schedule/reference/scoring/history providers; no CF client construction on the demo branch, live returns None; history constructs small fictional values, never bundled test fixtures |
| Dashboard v1 | Registered during setup via HA's supported extension; eight native commands, active administrator required on admission and delivery; loaded entry/selected series checked; read-only options/favorites |
| Card | Independently versioned 0.5.1, API v1, local self-contained Lit module. No external fonts/assets/imports/provider transport or hidden preview dependency; no private HA frontend imports |
| Manual installation | Python folder under `/config/custom_components/nascar_race_center/`, JS under `/config/www/nascar-race-center/`, module URL `/local/nascar-race-center/nascar-race-center-card-0.5.1.js`; no automatic copy, resource registration or HACS card installation |
| Lifecycle | HA forwards/unloads sensor/binary_sensor/calendar platforms, owns coordinator shutdown and shared aiohttp session. Entry callbacks drain history/analytics/dashboard work. Removal clears only entry-owned event/polling stores. Restart retains saved config/registry; ephemeral snapshots cannot resume |
| Browser target | ES2022, custom elements/Shadow DOM/container CSS; Phase 5C minimum feature targets Chrome/Edge 111+, Firefox 113+, Safari 16.4+ are targets, not an executed historical-version matrix |

No undocumented runtime package install was found. HA-supplied helpers, storage,
Recorder and shared transport are native dependencies; Node/npm/TypeScript,
pytest and Playwright are development tools, not owner HA OS requirements.
The first `www` directory and imported Python require a normal Core restart.

## Security, diagnostics, storage and request review

`diagnostics.py` explicitly selects normalized provider/health/count/timestamp
fields; it does not dump `entry.data`, `entry.options`, raw feeds, request/response
headers, tokens or HA origin URLs. CF transport/parser diagnostic outcomes are
bounded (24 each), fixed-path/status classifications. Existing secret-canary and
CF diagnostics tests remain in the passing suite. The **HA diagnostics wrapper**
can contain system/config metadata outside this function; owners must review the
whole downloaded document and sanitized log excerpts privately before sharing.
No global privacy guarantee is inferred from the integration allowlist.

HTTP uses HA's shared session, 15-second timeout, no redirects and 2 MiB body cap;
parser errors and expected provider failures use fixed safe reasons rather than
raw bodies or arbitrary upstream exception messages. Dashboard serializers
explicitly allowlist finite JSON projections; expected invalid selection/runtime
errors use fixed messages. Event ledger failures log fixed reasons and disable
events without disabling schedules. Unexpected HA/framework tracebacks and global
debug logging are not a safe diagnostic export format; this phase adds no logger
or exception-handling change.

Inbound WebSocket frames retain HA/aiohttp's **4 MiB default** maximum (inspected
installed source); the integration does not impose a new smaller frame transport
limit. Its schemas reject extra fields, overlong entry IDs, invalid integer/ID
bounds, oversized/duplicate lists and invalid page/query combinations before
provider work. The **256 KiB** budget is the outbound integration envelope, not
the inbound frame limit. Page limits 1–200; admission 30 commands/user/entry per
10 seconds, two user requests and eight entry requests including drain;
subscriptions four per connection/64 per entry.

History/analytics tokens bind user, originating socket, exact selection, command
and runtime entry. Authorization is rechecked, including revocation; tokens do
not grant access independently. Indexed snapshots have four global/two per-user
slots, 24 MiB/100,000 rows each, fixed 300-second lifetime; reservations persist
until canceled workers drain. Expiry/disconnect/unload/reload/shutdown cleanup,
cross-user/socket/entry rejection, oversized later rows and capacity admission
are exercised by existing actual-HA tests. Maximum 96 MiB is **additional index
storage**, excluding source models, HTTP decoding, HA queues/pages and other HA
memory. History/analytics are on demand, never startup/idle downloads.

Persistence consists of small private HA Store event deduplication and CF polling
reservations; demo events disabled cause no event-ledger work. No raw history or
dashboard snapshot goes to disk/Recorder. Dashboard reads/subscriptions add no
entity attributes. Existing event baseline suppression, persistence-before-publish,
backoff/cache/Retry-After and CF conservative authorization boundaries are unchanged.
No API permission expansion, live request or data-rights determination occurred.

## Executed development checks

Prepared Debian 13 x86_64 toolchain reused: Python **3.14.8**, Core **2026.10.2**,
frontend **20260930.4**, pytest **9.0.3**, pytest-homeassistant-custom-component
**0.13.373**, Ruff **0.17.1**, mypy **2.4.0**. Frontend: Node **24.19.0**, npm
**11.9.0**, Lit **3.3.1**, TypeScript **5.9.3**, Playwright **1.56.1**.

| Executed check | Result |
| --- | --- |
| Unmodified merged Python baseline | **1,007 passed**, 60.67 s |
| New unmodified-demo smoke journeys | **2 passed**, 0.69 s |
| Final full Python suite | **1,009 passed**, 53.57 s |
| Ruff lint / format | PASS; 148 Python files formatted |
| Strict mypy | PASS; 44 production source files |
| Official Hassfest | PASS; **1 integration, 0 invalid**; official Core tag 2026.10.2, source `8d7fd8b68677c2585be36ec86043308f403875b8` |
| Prepared independent actual-HA REST/state/service smoke | **1 passed**, 0.25 s; not a NASCAR/HA OS test |
| Prepared HA configuration check | PASS; exit 0 |
| Frontend ESLint / Prettier / strict TypeScript | PASS |
| Frontend unit/component suite | **68 passed**, 4 files |
| Production build / bundle budgets / excluded fixtures/imports/license checks | PASS |
| Lockfile install and committed bundle reproduction | PASS; `npm ci`, build, clean dist diff and identical SHA-256 |
| Existing synthetic budgets + actual-HA pagination/Recorder checks | **32 passed**, 19.90 s; all CF HTTP intercepted with handmade fixtures |
| Three-engine Playwright suite | **162 passed**, 4.5 minutes; **54 per engine**, no failures/retries |
| HACS | Private-repository job skip / existing brands exception retained; no full HACS approval |
| Owner HA OS / hardware / backup restore / physical-device checks | **NOT TESTED** |

The new smoke cases create the config entry through the actual HA flow manager,
query native calendar events, exercise administrator bootstrap/schedule/live
subscription/history pagination/analytics, reject a normal user, close/reopen
the native socket and reject its old token, update favorites through options,
verify stable registry identity on reload, remove the entry and run an unrelated
native event-driven automation afterward. An aiohttp guard fails before any
non-loopback HTTP can leave; no provider is replaced with rich test data.
These are actual HA **fixture/server** tests, not a complete supervised OS boot
or an onboarded native frontend browser test. Process restart remains manual;
existing replay/storage tests cover persistence mechanisms separately.

## Measured performance — development and synthetic only

No CPU, RSS, Recorder disk-growth, OS startup or frontend timing on the HP
EliteDesk is known. The checklist defines comparable before/after observation
windows without invented percentage/ms acceptance targets.

| Measurement in prepared development environment | Observation |
| --- | --- |
| Demo flow submission/form/setup to settled fixtures, three series / one series | **0.065232 / 0.026429 s**, one focused sample each; excludes OS boot, normal HA startup and browser loading |
| 100-driver live payload / delivery over actual fixture WebSocket | **70,669 bytes**, five changed updates **0.10467–0.10628 s** including intentional 100 ms coalescing |
| 50,028-row intercepted-CF history, all seven datasets | First page **0.59350 s**; continuation mean/max **0.00304/0.00643 s**; indexed **10,906,062 bytes**, max response **36,254 bytes**, continuation GETs **0** |
| 79,324-row intercepted-CF analytics, all seven datasets | First page **1.31150 s**; continuation mean/max **0.00332/0.00775 s**; indexed **19,086,650 bytes**, max response **217,526 bytes**, continuation GETs **0** |
| Separate projection-only history index, 50,010 rows | Build **0.40459 s**, retained traced **9,948,669 bytes**, peak traced **10,394,344 bytes**, accounted **10,749,010 bytes** |
| Separate projection-only analytics index, 79,316 rows | Build **0.78159 s**, retained traced **17,776,739 bytes**, peak traced **18,493,217 bytes**, accounted **19,001,876 bytes** |
| Recorder | Existing actual in-memory Recorder test passed: dashboard token reads/live subscription add zero new rows; disk-growth/household retention NOT TESTED |

Synthetic intercepted-CF timings include real parsers/services but do not contact
NASCAR or measure its latency. Tracemalloc values exclude prebuilt source models
and process RSS. These one-run observations are not contractual device budgets.
Browser measurements are in [PHASE6A_MEASUREMENTS.json](PHASE6A_MEASUREMENTS.json),
alongside the backend observations. Two cards / 100 changed updates / 100 drivers:
Chromium **1.789 ms mean / 4.6 ms max**, Firefox **3.21 / 9 ms**, WebKit
**2.18 / 4 ms**. All three preserved 100 keyed rows, two subscriptions while
mounted, zero idle commands and zero remaining listeners/subscriptions after
removal. Chromium reported 10,000,000 JS heap bytes, a potentially coarse browser
observation, not RSS or a long-duration memory test. These are local rendering
measurements with mocked HA transport. The separate single-card measurements in
the JSON include deliberate command pacing and a lighter repeated-array workload.

Runtime bundle **149,263 raw / 37,506 gzip bytes**, unchanged below existing
180,000/50,000-byte budgets. SHA-256:
`dd23b8e40704f7d5b0766d5d8ac12816c08e19832e241e8d75616fd2591dae2c`.
No Python/frontend production bytes differ from the pinned Phase 5C candidate.

## Reproduce without owner access or NASCAR traffic

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
pytest -q -s tests/test_beta_smoke.py
pytest -q -s tests/test_dashboard_performance.py tests/test_dashboard_pagination.py tests/test_dashboard_recorder.py
PYTHONPATH=work/home-assistant-core python -m script.hassfest --integration-path custom_components/nascar_race_center
pytest -q -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config --config /workspace/.cloud-setup/nascar-race-center/hass-config
sha256sum -c docs/PHASE6A_ARTIFACTS.sha256
cd frontend
npm ci --cache ../work/npm-cache
npm run lint
npm run typecheck
npm test
npm run build
npm run check:bundle
git diff --exit-code -- dist/
PLAYWRIGHT_BROWSERS_PATH=../work/ms-playwright npx playwright install chromium firefox webkit
PLAYWRIGHT_BROWSERS_PATH=../work/ms-playwright CHROMIUM_PATH=bundled npm run test:browser -- --max-failures=1
```

Prepared activation/config paths are development-only. Use official Hassfest
source at the exact revision above, as in earlier validation. On a normal CI host
use Playwright `install --with-deps`; local missing libraries were downloaded from
the configured Debian repository and extracted under ignored `work/browser-libs`,
not installed into HA. The downloaded WebKit wrapper replaces LD_LIBRARY_PATH,
so those libraries were copied into its local `minibrowser-{gtk,wpe}/sys/lib`.
Playwright's system-ldconfig GLES detection does not see workspace libraries;
the local run uses `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` after library
inspection/actual rendering. Browser assertions/configuration are unchanged.
Firefox's own sandbox cannot initialize inside the nested command sandbox
(`/proc/self/uid_map` EROFS); browser runs use the supported outer execution mode,
without disabling Firefox sandbox features. HTTP proxy/TLS policy stays intact.

Initial Git/npm/browser networking needed the supported execution network grant;
GitHub connector reads independently confirmed main. No denied NASCAR destination
was retried or bypassed. Scratch data/logs/runtime state remain ignored in `work/`.
Do not commit the local HA config/logs/credentials or generated Phase 5C captures.

## Remaining gates

Required owner participation: approve installation/restarts, verify real versions,
backup/recovery, household baseline, manual file transfer/resource/dashboard,
desktop/mobile/native companion behavior, assistive readers, browser/OS zoom,
locales/timezones, two-card/soak performance, approved restart/reload/remove and
recovery. Every unperformed row remains NOT TESTED. Full backup restoration is
separately approved and potentially rewinds household changes.

Source rights, anonymous/active-session behavior, timing units, official finality,
standalone scoring association, historical coverage and permitted polling cadence
remain independently unresolved. CF polling is not enabled. Full translations,
HACS private-repository/brands exceptions and separate integration/card public
distribution remain open. No merge, release, visibility change, public HACS
listing, owner installation, network modification or Phase 6B was performed.

## Final browser and CI evidence

Local Playwright 1.56.1 bundled engines: Chromium **141.0.7390.37** (1194),
Firefox **142.0.1** (1495), WebKit **26.0** (2215). **162/162** complete scenarios
passed in **4.5 minutes**, preserving all existing assertions and the DejaVu Sans
WebKit regression. Exercised widths 320–1920 CSS px, narrow embedded cards,
light/dark/source states, keyboard/focus, axe scans, text enlargement, CSS zoom,
reconnect, selection/pagination/expiry/capacity, two-card updates and removal.
Automated axe checks reported zero violations in their exercised states; this
is not manual assistive-reader/WCAG or physical Safari/iOS/Android acceptance.

The focused PR's checks and completion description record hosted workflow URLs,
head SHA and conclusions separately from these local results. HACS remains
conditionally skipped for the private repository with its existing brands
exception; no visibility/branding exception was changed to claim approval.
