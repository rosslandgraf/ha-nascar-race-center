# Owner update and authorized real-source acceptance

Candidate pair: **integration 0.1.2 / card 0.5.3**, Home Assistant Core 2026.10.2.
This procedure is for the owner's existing HA OS installation; it has not been
executed there. No public repository or HACS setup is required. PR #15 is already
merged; this is a separate review candidate. Use its reviewed commit, not a moving
branch or a published release (none is created).

## Update the installed pair without replacing the entry

1. While still in Demonstration, record the current integration/card versions,
   selected series, NASCAR entry ID, favorites, event preferences and conservative
   polling options. Copy the dashboard/card configuration and its resource URL.
   Record an ordinary household baseline: representative existing integrations,
   services and automations, without changing them. Keep enabled automations and
   their behavior under owner control during the source test.
2. Create/download a normal full HA backup and confirm its supported restore
   route. Separately save `/config/custom_components/nascar_race_center/`, the
   currently installed versioned JS, and the resource configuration. Do not edit
   `.storage`. If integration 0.1.0 / card 0.5.1 is still installed, this update
   includes PR #15's snapshot fixes. If 0.1.1 / 0.5.2 is installed, those remain.
3. From the reviewed PR checkout verify `sha256sum -c
   docs/CF_READINESS_ARTIFACTS.sha256` at repository root. Every integration file
   and the one committed JS are listed. `manifest.json` must say **0.1.2**. Download
   through the owner's existing authenticated GitHub access; do not publish or
   change visibility. A source checkout/archive is sufficient; building on HA OS
   is unnecessary.
4. With the supported file editor/transfer method, replace only the complete
   integration directory with `custom_components/nascar_race_center/` at
   `/config/custom_components/nascar_race_center/`. Avoid nesting it twice or
   mixing Python files from versions. Do not copy tests, work, demo fixtures,
   node_modules, cloud activation scripts or repository-local HA files.
5. Copy exactly `frontend/dist/nascar-race-center-card-0.5.3.js` to
   `/config/www/nascar-race-center/nascar-race-center-card-0.5.3.js`. Keep the old
   JS alongside it for rollback. Restart **Home Assistant Core** normally to load
   the new Python. Entry reload alone does not load changed Python files. Check
   the existing entry loads in Demonstration and its registry/entity IDs persist.
   Do not delete/recreate the entry or dashboard.
6. Edit the existing module resource in **Settings → Dashboards → Resources**
   (Advanced Mode may be needed) to
   `/local/nascar-race-center/nascar-race-center-card-0.5.3.js`, type **JavaScript
   Module**. For YAML resources update that same existing URL with `type: module`.
   Do not add a duplicate card module. Keep all existing card options/entry IDs.
7. Close/reopen dashboard tabs or hard reload the document; the custom element is
   registered once per document. Reload/reset the companion frontend cache only
   through its normal settings if needed. Verify the downloaded filename and
   artifact hash in browser tools where available; the card footer must say
   **0.5.3**. Backend first, card second is the supported order.
8. Verify Demonstration, History/Analytics selection switching/pagination, calm
   unavailable pits/stages/points and multiple-card/reconnect behavior. The normal
   Demo has no active race and does not fabricate real timing. Verify the recorded
   household baseline again. Stop and roll back if startup or existing household
   behavior regresses.

No config migration or entity-ID change is required. Backend API v1 remains
compatible with the older card, but the supported readiness pair includes 0.5.3's
new source-state labels. Removing series or favorite IDs can remove those
entities as usual; preserve selections during the upgrade.

## Permission and before-session checks

CF remains experimental. Before selecting it, privately confirm permission for
normal automated access to the documented `https://cf.nascar.com` paths, endpoint
classes, cadence and any evidence retention. Confirm the HA network permits that
host normally. Public accessibility or a checkbox is not that permission. Stop
on denied access; do not supply credentials/cookies, disable TLS, change proxy
routes or use the different Swagger host.

Use the current official weekend schedule to choose a **known practice,
qualifying or race session**, independently of track or series. Talladega Friday
October 23 is an opportunity only if the official schedule and permission support
it; no date, series or track is built into this implementation. Test each of Cup
(1), O'Reilly (2) and Craftsman Trucks (3), and each session type separately as
opportunities occur. Do not infer all nine from one successful race.

Make the one initial CF switch while official live information confirms the
intended session is under way. Starting between sessions can leave hourly or
six-hour discovery, especially with unknown schedule timestamps.

In **Settings → Devices & services → NASCAR Race Center → Configure**, edit the
**existing entry**, choose NASCAR CF, affirm authorization only if confirmed, and
keep all selected series and conservative polling settings. Review favorites:
fictional Demo IDs (990xx) are not real NASCAR driver IDs. Choose legitimate
NASCAR IDs reported by the approved source; names/car numbers are not identity.
Keep event/blueprint preferences unchanged unless the owner intentionally changes
them; no new household automation is necessary for this test. Source changes
reload the entry and baseline the existing event engine.

This is the only provider switch needed for the test. Setup attempts the existing
season schedule, per-series optional session schedules, driver/track references
and one global live feed. Historical requests occur only when explicitly opened.
Standalone pits/stages/points must not be requested: their associations remain
unsupported. Permission scope must cover the selected operations. For an initial
live-only acceptance, avoid opening new historical selections.

Download entry diagnostics from its menu after setup and after ordinary eligible
refreshes. Do not repeatedly reload, restart, clear storage/caches or force updates
to evade request reservations or cooldowns. Browsing cards/diagnostics reads
cached models and does not trigger live GETs. Consult `live.polling` for the actual
next interval: 300 seconds is a floor, not a guarantee of a five-minute refresh.
Known race windows can be 15 minutes, nearby idle one hour, otherwise six hours;
unknown-offset schedule times can leave six-hour discovery. Practice/qualifying
with supported on-track observations use the conservative minimum. Completed or
nonadvancing observations fall back to discovery; server/backoff can lengthen it.
See [the exact policy](CF_READINESS_VALIDATION.md#polling-and-resource-decisions).

## During an approved active session

At minimum collect one initial and one later ordinary eligible observation.
Store only approved minimal diagnostics privately, without raw feed bodies,
headers, tokens or HA storage. Use the official NASCAR published live results /
qualifying information in the owner's ordinary browser as an independent check;
that check is not performed by this PR or CI.

| Check | Expected / acceptance evidence |
| --- | --- |
| Provider | Top-level `provider=cf`; Demo banner absent. A card title alone does not establish the provider. |
| Attempt / HTTPS / JSON | `cf_pipeline.transport[path]`: `attempt_at`, `response_at`, `http_status`, `transport`, `json_status`, `delivery`, `successful_response_at`, `next_eligible_in_seconds`. `cache` means no new GET; `revalidated` is a 304 using prior content. No status/`connection_error` is transport failure, not origin denial. |
| Parse | `cf_pipeline.parsers` says `parsed`. HTTP 200 + JSON alone is insufficient. `invalid` is schema failure; no-session/empty normalized observations are separate. |
| Identity | `live.series_id`, `race_id`, `run_id`, `run_type_code` match the independently known session. Card shows selected series/type, race/timing-run, source timestamp. Other selected series say `not_reported` and have no timing rows. |
| Progress | Initially reported/activity-unconfirmed. Later source clock **and observations** advance with matching identity and supported activity; `observation_advancement=observations_changed`, `session_progress=active`. Timestamp-only is insufficient. Compare reported lap/driver changes, not download time. |
| Vehicles | `live.timing.reported_count`, `normalized_count`, `omitted_count`, `leaderboard_availability`, `timing_unavailable_reason`, per-series `usable_timing`. Compare several NASCAR IDs/names/car numbers, reported positions, laps, gaps, last/best timing/speeds where present, and selected favorites. Missing values stay unavailable; gaps/time/speed units retain source-evidence limits. |
| Practice / qualifying | Correct detected type; usable reported vehicles appear at zero global race laps. No race total/stage sentinel is displayed as race scoring. Compare qualifying information to the official published session, without calling a provisional feed order the final starting grid. |
| Scoring | Embedded pits only where provided for the matching driver/run. Standalone pits/stages/points remain unsupported/unavailable, calmly; no fabricated totals or unrelated race joins. |
| Timing budget | `live.polling` target/effective interval, constraint, network eligibility; no faster than the configured minimum or server limits. Several cards/favorites still share one global live loop. |
| Household | Existing unrelated integrations/automations still match the recorded baseline; no changed dashboard entry ID or entity identities from upgrade. |

If HTTP/network access fails, do not claim source-schema failure. On 429/503,
respect Retry-After and stop manual requests. On schema rejection, retain the
small redacted diagnostic outcome for review; do not patch defaults to make rows
appear. Offset-free schedule times legitimately leave calendar/next-race times
unknown even when race counts/names parse. Unknown flags/driver status and units
need separate evidence, not guesses.

## After the session, recovery and result record

Checkered with current source evidence says completed, not official finality.
Cold/retained content says latest recorded; fresh timestamp alone cannot keep
old timing active. Empty vehicles says no current session, with no red load error
or fabricated field. At more than 15 minutes of source age the existing local
expiry makes timing stale without an extra GET. Confirm previous History/Analytics
selections remain intact until their normal selection expiry, independently of
an empty live feed. Compare final results to NASCAR's published classification;
feed checkered alone does not certify them.

At the end of the approved window, use **Configure** on the same entry to return
to **Demonstration** (or disable the entry if desired). Verify clean reload,
Demo banner, stopped CF requests and unchanged entry/entity IDs. Review favorites
when changing data source; do not silently replace the owner's real choices with
fictional IDs. Native socket reconnect/entry reload disposes live subscriptions
and snapshots; resubmit expired historical selections normally. Do not repeat
reloads to get around CF's retained request slot or host cooldown.

Record: reviewed commit and both artifact versions/hashes; HA Core/OS/Supervisor
versions; permission scope/window; independent official event/session reference;
UTC sample times; selected series and actual reported series/race/run/type; safe
HTTP/JSON/parser outcomes; source and observation advancement; vehicle counts /
omissions; a few checked fields/favorites; calm empty/completed behavior;
request eligibility; disconnect/reload and household baseline results. Mark
untested series/session combinations explicitly. One HTTP success closes neither
active-session nor permission/cadence/redistribution gates.

## Rollback

1. Return to Demonstration through the same entry before removing this candidate,
   if the UI is healthy. Save its diagnostics privately and stop the test.
2. Restore the backed-up **whole** integration directory and restart Core. Restore
   the old JS/module URL from step 2, reload the browser document/companion cache,
   and verify the old versions and household baseline. Preserve the entry and
   dashboard; no new storage migration needs reversing.
3. For a code-only known PR #15 pair, checkout
   `68e917eab183a405a1f662ba49a71eb23dcc4fed`, verify
   `docs/SNAPSHOT_FIX_ARTIFACTS.sha256`, use its integration **0.1.1** directory and
   `frontend/dist/nascar-race-center-card-0.5.2.js`. Resource URL:
   `/local/nascar-race-center/nascar-race-center-card-0.5.2.js`. Verify hashes on
   that pinned checkout, not against the newer Python directory.
4. If the backed-up installed pair is still **0.1.0 / 0.5.1**, restore those exact
   saved files/resource, or use the prior pinned Phase 6A
   [rollback guide](PHASE6A_ROLLBACK.md). That older pair has the known snapshot
   usability defects; returning to it does not retain PR #15 fixes.
5. If Core cannot start or household behavior has changed, use the installation's
   supported backup restore route. Do not delete the NASCAR entry, hand-edit
   `.storage`, change unrelated integrations or clear persistent request guards.
