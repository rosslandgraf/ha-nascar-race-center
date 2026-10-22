# Phase 6A — beta acceptance and observation record

Use a private copy of this checklist for the owner run. **PASS** means the stated
procedure actually passed; **FAIL** needs evidence and a recovery decision;
**NOT TESTED** means no claim. Add date/time/timezone, tester, device/software
versions, relevant screenshot/log excerpt and issue reference. Automated results
below describe the prepared Linux development environment, not the owner's HA OS.
No physical-device row is pre-approved by CI.

## Run identity and safety gates

| Record | Value for the owner to complete |
| --- | --- |
| Date/time/timezone, tester, explicit installation approval | NOT TESTED |
| HP EliteDesk 705 G4 Mini / actual RAM, storage/free space | NOT TESTED |
| Core / Frontend / Supervisor / OS / installation type | NOT TESTED |
| Browser/app / OS / viewport and actual card width / theme | NOT TESTED |
| HA language, number format, time format, timezone | NOT TESTED |
| Runtime source | `ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972` (Phase 5C) |
| Integration / card / API | 0.1.0 / 0.5.1 / v1 |
| Copied file hashes / resource URL / saved entry ID | NOT TESTED; compare installation guide and artifact manifest |
| Backup success / contents / off-device size+hash / retrievable key | NOT TESTED |
| Backup restore rehearsal / independent file recovery route | NOT TESTED; distinguish the two |
| Existing household service and automation control inventory | NOT TESTED |

- [ ] Compatibility, backup/key/recovery route and restart window reviewed with
  the owner; any untested restoration is explicitly recorded.
- [ ] Existing dashboards/resources/config files saved privately; path conflicts
  resolved before copying; no household integration or automation replaced.
- [ ] Demonstration selected, CF authorization unchecked, racing events disabled.
- [ ] Stop immediately on a household regression; use [rollback](PHASE6A_ROLLBACK.md).

## Automated acceptance already executed in development

See [validation](PHASE6A_VALIDATION.md) for commands, exact versions, measurements
and CI evidence. These rows are not owner-hardware results.

| Check | Result | Evidence scope |
| --- | --- | --- |
| Real config flow → unmodified demo setup, all series and series 2 alone | PASS | Two `test_beta_smoke.py` cases; no provider fixture replacement |
| Actual HA calendars, favorites options, stable registry IDs across options/reload | PASS | Same smoke journeys plus existing lifecycle/calendar/favorites tests |
| Administrator bootstrap, schedule, live subscription, history continuation, analytics | PASS | Authenticated actual HA WebSocket fixture/server; offline fictional history |
| Non-admin denial, socket disconnect, stale token rejection and resource cleanup | PASS | Smoke journeys plus existing scope/expiry/revocation/cancellation tests |
| Entry removal preserves an unrelated helper and event-driven automation | PASS | Native HA automation runs after removal; no household hardware exercised |
| No external HTTP in demo journey | PASS | Request guard rejects every non-loopback aiohttp request before I/O |
| Small Recorder writes, bounded snapshots and zero history continuation GETs | PASS | Existing actual-HA Recorder and synthetic large-stream checks rerun |
| Five-view rendering, responsive/focus/keyboard/theme/zoom/reconnect behavior | PASS; 162 browser scenarios | Playwright mock-HA browser harness; distinct from native HA frontend/device acceptance |
| Full HA process restart, owner backup restoration, actual household reliability | NOT TESTED | Requires owner environment and approval |

## What production Demonstration mode can show

The real demo constructs fictional examples in Python; it does not load browser
fixtures or contact NASCAR. Use the same configured series throughout each
selection. It generates two weekends per year/series: February 15 and November 15
at 19:00 UTC, with practice two days before, qualifying one day before and a
three-hour fictional race session. These durations are fictional demo facts,
not inferred real-race durations. The upcoming display depends on today's date
and retained seasons; an empty next activity late in a season is valid.

| View/feature | Exact offline exercise and expected result | Owner result |
| --- | --- | --- |
| Setup and series | Follow installation; verify only selected series are navigable, one integration entry and one calendar per selected series | NOT TESTED |
| Race Center | Choose each series; see demo source, future schedule/countdown when one exists, fictional track and selected favorites; no invented leader/lap/flag | NOT TESTED |
| Live Timing | Open the view and return to Race Center; **no active session**, no fabricated driver rows or live totals; one live subscription while a live view is visible | NOT TESTED |
| Race Weekend | Open season weekends and practice/qualifying/race sessions; compare known UTC times to HA-local display and calendars | NOT TESTED |
| Favorites | Configure 99001/99002, save, reload; verify fictional reference names and retained 99002 identity; live metrics unavailable without observations | NOT TESTED |
| History | Select a retained demo race or explicit season/series/race; choose weekend and laps, then Load race records; one fictional result for driver 99002/car 00/position 1/laps 5, no lap-by-lap observations | NOT TESTED |
| Analytics | For that same key, select driver 99002, laps 1–10, window 5; submit; reported result summaries may show, lap metrics/charts remain empty/unavailable; no synthetic pace curve | NOT TESTED |
| Other history datasets | Select notes/loop/averages/pits/stages explicitly; empty collections remain empty, no claim of real published results or coverage | NOT TESTED |
| Diagnostics | Download from the integration entry; review demo provider, selected series, reference/favorite counts and no live session; inspect whole HA wrapper privately | NOT TESTED |
| Session/availability states | Production demo meaningfully checks no-active-session, missing metrics and empty history. Fresh racing, stale/denied source, pits/stages/points and race/run transitions require the clearly synthetic development harness or a separately authorized source test | NOT TESTED |
| Racing events | Defaults remain disabled; no NASCAR event causes household actions. Synthetic replay/storage tests cover baseline suppression, not live semantic/device acceptance | NOT TESTED |

Never replace the production demo with rich preview fixtures to make empty
sections look complete. `frontend/demo` tests 100-driver timing, pit/stage/points,
null charts and populated historical pagination with **fictional** data only.
Production demo's weekend history is short enough that a normal 200-row page may
have no Next button. Large paging/expiry/capacity states use the controlled harness
or documented authenticated development API tests, not real NASCAR collection.

## Physical browser, device and accessibility matrix

For each row perform the common sequence: open the separate beta dashboard as an
administrator; use all five views, change series, configure favorites through HA,
save/reopen the card editor, reload the frontend, and check source/empty states.
Record browser/app version, orientation, actual card width and failures. Do not
mark a physical row PASS from Playwright's desktop engine or touch emulation.

| Target | Additional exact actions and acceptance | Result |
| --- | --- | --- |
| Desktop Chromium/Chrome/Edge | Run common sequence; Tab/Shift-Tab through visible controls, activate Enter/Space, check visible focus and no document overflow | NOT TESTED |
| Desktop Firefox | Repeat common sequence; inspect native select labels, focus and card sizing independently | NOT TESTED |
| macOS Safari or desktop WebKit where available | Record whether actual Safari or development WebKit; verify long Analytics selection labels fit; do not equate Linux WebKit with Safari device validation | NOT TESTED |
| iPhone Safari | Portrait and landscape; tap all navigation, selectors and native menus; scroll intentional inner regions; no page-wide sideways overflow | NOT TESTED |
| HA iOS companion app | Repeat on same iPhone; background/foreground app, reopen dashboard and reconnect; no stale selection shown as current | NOT TESTED |
| Android Chrome/browser if available | Repeat touch/rotation/narrow controls; record unavailable device as NOT TESTED | NOT TESTED |
| HA Android companion app if available | Repeat background/resume, card editing and connection recovery | NOT TESTED |
| Narrow mobile/embedded card | Test actual available widths around 320–430 CSS px and a 320 px embedded card; five buttons/selects/labels fit, inner table/chart scroll stays inside card | NOT TESTED |
| Tablet/wall dashboard | Portrait/landscape at available 768–1024 and 1280–1920 widths; two cards, Compact density, 2-hour observation; record actual container width | NOT TESTED |
| Light/dark/custom theme | Toggle supported themes; labels/focus/status remain readable and missing data stays explicit; enable reduced motion | NOT TESTED |
| Keyboard with populated synthetic tower | On separate development harness: sort; driver arrows/Home/End; Enter detail, Escape/Close return focus; context change never shows old driver/run | NOT TESTED |
| VoiceOver | With a tester: navigate headings, five destinations, selections, status/empty announcements; on synthetic charts/timing check sort announcements, observations/table and detail focus return; note repetitive/missing labels | NOT TESTED |
| TalkBack | Repeat swipe reading order and double-tap activation on Android; check unavailable values are spoken meaningfully | NOT TESTED |
| Browser zoom / OS text | Use browser's own 200% zoom, then OS text enlargement; repeat navigation/selectors in both orientations; record settings and clipping, distinct from CSS zoom CI | NOT TESTED |
| Locale/timezone | First record household HA settings. Prefer a separate dev HA for timezone changes; only with approval temporarily change HA to America/New_York then UTC, language/12–24h/decimal preferences, compare the same explicit-offset demo sessions, and restore saved settings | NOT TESTED |

## Lifecycle, access and multi-card acceptance

| Procedure | Expected result | Result |
| --- | --- | --- |
| Add two cards on beta dashboard; choose different series and views; switch rapidly | Independent selections, no previous-series data/focus leaks; each live card has one subscription; leaving live views disposes it | NOT TESTED |
| Use an existing normal non-admin account; open card without granting admin just for testing | Administrator-required error; normal household dashboards/entities still work according to their existing permissions | NOT TESTED |
| On only the test phone/laptop, briefly disable its Wi-Fi/network or use browser offline mode, then restore | HA reconnects; card reboots from bootstrap; old connection-bound snapshot cannot continue, no rapid retry loop | NOT TESTED |
| Reload integration through its ⋮ Reload action, with beta card open | Brief entry-unavailable/reconnect state; after loaded, use offered reconnect/reload; entities keep identity and only replacement runtime subscribes | NOT TESTED |
| Owner-approved normal Core restart | Household services return, saved entry/options/favorites/entity IDs and resource/card settings persist; fresh snapshots required | NOT TESTED |
| Remove one card, then the other, save, reload dashboard; re-add via editor | No orphaned live subscriptions for removed cards; correct loaded entry selectable; no integration or unrelated card removed | NOT TESTED |
| Controlled history paging on separate development HA/harness | Navigate every page using exact next offset; Back/reuse selection has no new source retrieval; loaded-range labels stay honest | NOT TESTED |
| Snapshot expiration in controlled development session | Start short history selection, wait over five minutes, request continuation; explicit expired/invalid selection, Restart from offset zero, no false resume | NOT TESTED |
| Snapshot capacity/scoping in controlled development tests | Two selections per user/four globally, other socket/user cannot replay token; no automatic capacity retry or new API privileges | NOT TESTED |
| Remove/restore integration in approved window using rollback guide | Other services survive; deleting/re-adding has new entry identity; verified backup restore needed for exact old registry restoration | NOT TESTED |

Network interruption means the **client connection**, not unplugging HA's Ethernet
or modifying UniFi. Do not export tokens/cookies or full Network frame logs.
The developer pytest cases are the repeatable authenticated API procedure for
large snapshots, expiry and scoping; no secret-bearing console script is required
on the owner's instance.

## Performance and reliability observation procedure

All owner measurements below are **NOT TESTED**. Record raw observations and
comparable workloads; there is no invented HP CPU/RAM/latency acceptance threshold.
Use the same sampling interval and duration before/after. Stop for sustained new
resource pressure, increasing errors, unavailable household entities, missed
scheduled household actions or unusable interaction; investigate against baseline
before calling it a NASCAR regression. Do not provoke safety-critical automations.

1. **Before installation:** with normal household activity, sample for ten
   minutes at one-minute intervals. Use existing HA OS/System hardware/Core
   resource diagnostics or already installed monitoring; record which tool and
   whether CPU is host-wide or Core-only, its units/normalization, memory units,
   disk free, and HA uptime. No new monitoring integration is mandatory. If a
   metric is unavailable, record NOT TESTED instead of changing production config.
2. Record the Recorder database backend (SQLite/external), its current size and
   routine purge/repack/backup activity using an existing read-only file/stat or
   database monitoring method. For SQLite consider WAL too; never open/edit a
   running database with an unsafe tool or copy only its main file as a backup.
   Do not change Recorder filters, retention or schema for this beta.
3. After demo setup, repeat the ten-minute samples with no NASCAR card open,
   then one Race Center card, then two cards. Note favorites/enabled metrics and
   all competing work. Record available NASCAR and household entity counts and
   error deltas. Empty live timing is expected; schedules/calendars must work.
4. **Startup/reload:** time from approved restart/reload action to entry loaded,
   schedule/calendar availability and household recovery; record log timestamps
   and full wall-clock duration separately. Repeat a reload only if needed to
   investigate variability. Synthetic setup seconds exclude OS boot and are not
   an owner-hardware baseline.
5. **Frontend:** use browser DevTools Network/Performance on the beta dashboard.
   Separately measure cold resource transfer (cache disabled once), warm reload,
   card content ready and input responsiveness; save browser/cache/card width.
   Confirm the exact module request/hash. No NASCAR-origin request is expected.
   No production demo timing rows exist: record timing-row rendering NOT TESTED
   on the owner machine, and cite the synthetic 100-driver CI harness separately.
6. **WebSocket:** in browser DevTools, inspect only the test card commands on the
   shared `/api/websocket` connection. One `subscribe_live` per visible live card;
   Race Center ↔ Live Timing reuse it; other views/removal unsubscribe. HA sends
   unrelated commands too; count NASCAR-prefixed frames only. Do not publish
   auth frames, cookies or full captures. Closing one card must not disconnect HA.
7. **History/memory:** submit only a few intentional demo requests. No history
   acquisition on startup/idle; continuation has no new source fetch. Snapshot
   budget is 24 MiB/100,000 rows per slot, four globally, two per user, fixed 300 s;
   96 MiB is indexed storage **in addition** to HA/service/page memory. It is not
   a total RSS budget or proof of a plateau. Do not stress-maximize household HA.
8. **Two-hour soak:** leave the beta dashboard in its chosen layout, sample
   resources/errors/entity availability at start, 15, 30, 60 and 120 minutes.
   Record browser/app backgrounding, ordinary household actions and any memory
   trend; compare database size over equal pre/post windows (ideally 24 hours to
   observe routine recorder/purge effects). Avoid concurrent upgrades/backups
   during a short comparison. Optional longer/overnight soak needs owner consent.
9. Recheck representative household services and one safe existing automation
   before/after restart, reload, card removal and integration removal. For event
   behavior keep NASCAR events off, verify no spontaneous actions; live event
   transition/scene restoration testing stays a separate authorized test.

| Measurement (tool, scope, units, workload required) | Before | Demo/no card | One card | Two cards/soak | Result |
| --- | --- | --- | --- | --- | --- |
| CPU samples / min–median–max / competing activity | — | — | — | — | NOT TESTED |
| Core + browser memory / trend, host free memory | — | — | — | — | NOT TESTED |
| Recorder/database + WAL size / equal-window growth | — | — | — | — | NOT TESTED |
| NASCAR schedule/reference and household availability | — | — | — | — | NOT TESTED |
| Core startup / entry reload / household recovery seconds | — | — | — | — | NOT TESTED |
| Cold/warm module + card-content ready time | — | — | — | — | NOT TESTED |
| Timing-row render (synthetic environment if used) | — | — | — | — | NOT TESTED |
| NASCAR subscriptions / historical commands / errors | — | — | — | — | NOT TESTED |
| Backup restoration / removal/restoration outcomes | — | — | — | — | NOT TESTED |

## Decision and next gate

- [ ] Owner installation approval recorded (currently NOT TESTED).
- [ ] Required demo and household checks completed; failures resolved or beta
  rolled back; unavailable physical targets remain listed as NOT TESTED.
- [ ] Backup restoration risk and owner observations reviewed before any next
  installation decision. Beta sign-off: **NOT TESTED**; owner/date: **unrecorded**.
- [ ] Separate permission required for CF/live source testing, source units,
  finality, permitted cadence, data rights, HACS integration/card distribution,
  branding and any public release. No Phase 6B, merge or release follows
  automatically from this checklist.
