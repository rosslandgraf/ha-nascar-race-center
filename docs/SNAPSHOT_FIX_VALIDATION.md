# Snapshot exploration and empty-state beta fix

This focused fix starts from merged main `fe23d92852120903694e0a87f600e82c2816c841`
(PR #14 / Phase 6A). The owner reports successful physical installation of
integration **0.1.0** and card **0.5.1** on Home Assistant OS / Core 2026.10.2 in
Demonstration mode, followed by the defects described here. That report establishes
installation, not completion of the remaining physical acceptance checklist.
The candidate pair is integration **0.1.1** and card **0.5.2**, dashboard API v1.
No release is published and no owner installation is changed by this work.

## Causes and decisions

Every new History/Analytics request without a token allocated a full slot for
300 seconds, including empty or small selections. There was no release command.
The card also refused a third local selection outright. Clearing local pages
could not free the backend. Ordinary exploration therefore exhausted two slots
almost immediately even though no one needed those old snapshots.

The smallest change adds an idempotent `release_snapshot` command and explicit
client ownership of tokens. Each card retains at most two recent selections,
reuses exact retained selections/pages without a request, and releases a displaced
selection before replacement. When both History and Analytics are retained, a
new selection replaces an older selection of the same kind first. Navigation
keeps selections and their pagination. A returned-to cached page does not rebuild
or refresh its snapshot. A released selection must be submitted afresh.

If capacity is held by multiple cards, the card makes one paced retry after
requesting cleanup of one hidden, idle selection on the **same connection and
entry**. Each cooperating card performs its own release; tokens and pages remain
private to their clients. A visible selection in another card is protected.
There is no server LRU that guesses whether a snapshot is in use. Another tab's
connection, another entry, or another user cannot be reclaimed this way. If all
slots are actively needed, the capacity notice remains an honest resource limit.

Invalidation/restart waits for pending page work, releases late first-page tokens,
and ignores obsolete responses. Client disposal cancels queued reads while paced
cleanup can finish after card removal. Native socket disconnect, entry unload,
reload, shutdown and the original TTL remain backend cleanup backstops. An
explicit release immediately prevents new reads but retains its accounted slot
and immutable index until existing page workers drain. A retry cannot steal that
reservation. Cleanup failures during an interrupted or rate-limited connection
fall back to disconnect/expiry; there is no retry loop or socket closure shortcut.

Live bootstrap uses a structured null race/run identity without a session; detail
pages previously returned a null identity. The frontend compared undefined fields
with null and reported `snapshot_changed`. Detail pages now use the same structured
empty identity, and PageView also accepts the earlier null identity for an expected
empty context. A real race/run/series change, or disappearance of a known context,
still rejects mixed observations. The card requests detail only with a fresh
matching race and renders no-session/unavailable observations calmly. Successful
empty pages remain normal data; expiry/source-change/capacity notices offer recovery
without a red failure panel. Authentication, connection, invalid-selection and
unexpected API failures still use error panels.

## Resource and security budgets

All backend limits remain unchanged: **4 global / 2 per user** reserved snapshots
across entries (including builds and draining readers), **24 MiB / 100,000 rows**
per snapshot, **96 MiB** total reserved index budget, **256 KiB** response envelopes,
**200 rows** per page, **300 seconds** fixed TTL. This is index accounting, not a
process RSS cap; bounded source caches, source models, computation, HA transport
and decoded responses have their existing additional budgets.

Dashboard work remains 2 requests per user / 8 per entry, with 30 admitted commands
per user/entry per 10 seconds, including release commands. The card's shared 370 ms
pacing applies to cleanup and replacement too. Subscriptions, HTTP cache/floor,
response sizes, polling intervals, provider, and analytics driver/lap/window limits
are unchanged. Frontend retention remains 8 pages / 1,600 rows per selection and
two selections per card; the navigation back stack is capped at 64 offsets.

Release requires the usual administrator, loaded-entry and admission checks.
Ownership checks require the exact runtime owner, authenticated user and original
WebSocket connection. Unknown, expired, retired, modified and foreign tokens all
receive the same empty success response, exposing no token-existence oracle.
Release neither retrieves records nor accepts another selection's identity.
Token retrieval still checks command, race, ordered datasets and all analytics
options. No state attributes, Recorder schema, entities, configuration/storage
formats, event publication, household services or automation behavior change.

## Executed validation

Tests use handmade structural fixtures or the unchanged offline Demonstration
provider; no NASCAR endpoints are contacted. The prepared runtime is Python
3.14.8 / Home Assistant 2026.10.2, Ruff 0.17.1, mypy 2.4.0, Node 24.19.0,
TypeScript 5.9.3 and Playwright 1.56.1.

| Check | Executed result |
| --- | --- |
| All Python tests | **1,018 passed**, 58.41 seconds (1,009 existing + 9 new) |
| Focused existing dashboard/pagination/beta journeys | **80 passed**, 13.46 seconds |
| New authenticated release/no-session regressions | **9 passed**, 1.14 seconds |
| Ruff lint and formatting | PASS |
| Strict mypy | PASS, 44 production source files |
| Official Hassfest | PASS, 1 integration / 0 invalid, Core tag 2026.10.2 source `8d7fd8b68677c2585be36ec86043308f403875b8` |
| Independent actual-HA REST/state/service smoke | **1 passed**, 0.25 seconds |
| Prepared HA configuration validation | PASS, exit 0 |
| Frontend ESLint / Prettier / TypeScript | PASS |
| All frontend unit/component tests | **78 passed**, 4 files, 16.31 seconds |
| Production build and transfer/license/import/fixture budgets | PASS; 180,000 raw / 50,000 gzip ceilings unchanged |
| Three-engine browser scenarios | **171 passed**, 6.0 minutes; **57 per engine**, no failed scenarios/retries in the final full run |
| Lockfile install / committed bundle reproduction / SHA-256 verification | PASS |
| HACS | Private-repository skip and existing brands exception retained; no full HACS approval |

The new backend journey opens 20 distinct small selections alternating History
and Analytics, releases each abandoned token, preserves a separate active token,
pages that original token afterward, and verifies disconnect cleanup. Its
simulated admission clock advances 0.4 seconds per command (about 16 seconds total),
never five minutes. This respects the real unchanged sliding window rather than
turning it off. Other cases use a real HA authenticated socket to reject cross-user,
cross-connection, cross-entry and revoked-admin release, check idempotence, and
hold a blocked page serializer through retirement until its reservation drains.
Pits/stages/points use the unmodified demo's real no-session response. Existing
pagination/large-stream tests still cover expiry, source changes, byte/row limits,
cache eviction, cancellation, stop, reload and restart invalidation.

All 162 pre-existing browser scenarios remain, with the old capacity-rejection
scenario updated to require replacement and the expiry scenario updated to expect
a calm status panel. Nine additional engine/scenario combinations exercise the
new journeys. Existing widths 320–1920, narrow containers, accessibility, focus,
source states, zoom, idle, reconnect, performance and production bundle assertions
still pass. Generated captures/measurements remain in ignored development work;
Phase 5C historical artifacts are not overwritten by this fix.

Frontend regressions cover late-token release after disposal, cancellation before
sending a queued selection, repeated restart clicks during cleanup, cached-page
reuse, null and structured empty identities, and independent series/race/run/
disappearance source-change rejection. Browser tests add 20 dataset selections,
repeated History/Analytics navigation, cached resubmission, two cards with a full
retained budget, visible-peer protection, removal cleanup and zero no-session
pits/stages/points requests. They use a bounded synthetic two-slot preview adapter;
backend behavior is separately exercised with actual HA fixture sockets.

The existing two offline beta smoke journeys install/configure via real HA flows,
verify calendar/registry identities, reload/remove the entry and run an unrelated
native household event automation afterward. They passed in the full suite with
all non-loopback HTTP guarded. The independent fixture smoke and configuration
check also passed. These confirm regression protection in the development HA test
environment, **not** the owner's installed household or a full HA OS hardware boot.

Initial sandboxed HA socket/multiprocessing checks could not initialize and were
stopped; supported network-enabled execution completed them. Browser engines and
missing shared libraries were downloaded to ignored `work/`, with WebKit's local
runtime libraries populated as in Phase 6A. Firefox's own sandbox cannot initialize
inside the nested command sandbox; the final browser run uses supported outer
execution without disabling Firefox sandbox features. No network/TLS policy was
bypassed and no NASCAR destination was contacted.

## Remaining limits

A third simultaneously active selection per user, or a fifth globally, still
receives a capacity notice. Hidden selections on another connection/entry cannot
be reclaimed by a peer card. Close the unused card/tab or allow its fixed TTL to
expire. Fixed expiry, backend source request floors, rate windows and missing demo
history/laps remain visible; exploration does not fabricate records or bypass them.
Interrupted cleanup has disconnect/TTL backstops. Snapshot tokens never resume
across a socket reconnect, entry reload or process restart.

The physical upgrade, real household baseline, hardware/mobile/native companion
acceptance and long soak remain owner checks. Prior owner-reported installation
success is acknowledged without claiming those new physical checks ran. CF source
rights, schema/freshness and allowed cadence gates remain unresolved; no CF request,
provider/polling change, owner access, release publication, merge or Phase 6B work
occurred. See the [exact update/rollback guide](SNAPSHOT_FIX_UPGRADE.md).

## Artifact identity

[Complete integration/card SHA-256 manifest](SNAPSHOT_FIX_ARTIFACTS.sha256), verified
locally with `sha256sum -c`. The integration manifest version is 0.1.1; every
integration file is covered. The card is rebuilt under its new 0.5.2 filename.

| Artifact | SHA-256 |
| --- | --- |
| `frontend/dist/nascar-race-center-card-0.5.2.js` (154,351 raw / 38,649 gzip bytes) | `f124cc6585433fc26d2f5eedfab06d1aecb3bc880822708f109dc39f50d01f0b` |
| `docs/SNAPSHOT_FIX_ARTIFACTS.sha256` | `86284f9c4678e69058e0a0d02fc73ffbeff6b4ea3d42b06774aacf20d3efcb1c` |

The historical Phase 6A manifest still pins 0.1.0 / 0.5.1; it is not rewritten to
claim the earlier release contained these fixes. Verify it on the pinned PR #14
checkout when recovering the old Python set. Runtime packaging/licenses remain
separate for the integration and card. No deploy/release automation is invoked.
