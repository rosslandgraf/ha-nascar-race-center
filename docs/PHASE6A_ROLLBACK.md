# Phase 6A — safe update, removal and recovery

These procedures are for the owner after explicit approval for the relevant
installation, restart or restoration. They do not run automatically. Use a
maintenance window and preserve the household setup. Start with the backup and
recovery-route checks in [installation](PHASE6A_INSTALLATION.md).

## Save a recoverable baseline before every update

Create a fresh full backup; verify completion, contents, off-device copy and
encryption key. Record restore-rehearsal status separately, even if NOT TESTED.
Keep the previous known-good backup. Save off-device copies of the entire current
integration directory, versioned JavaScript files, existing resource URL/type,
the beta dashboard's card configuration, selected series/favorites/event options,
and a private entity/device identity inventory. Record source commits and hashes.
Do not put archives in `/config/www`, download `.storage` into Git or hand-edit
HA registries. A backup filename alone is not evidence of recovery.

Identity inventory: in the integration's entity list, record entity ID and unique
ID where the UI provides it (entity settings/info); use a private supported
registry export if needed. Also record the exact card editor `entry_id`. The
implementation uses **entry ID + series ID + metric**, and **entry ID + NASCAR
driver ID + metric**; the integration domain scopes the registry. Driver name/car
number is never identity. Existing entry/options/restart upgrades preserve these
IDs. Removing and recreating an entry generates a new entry ID and is **not** an
identity-preserving rollback. Renaming entity IDs manually also changes the
inventory. Retain the entry when recovering files.

## Upgrade to a newer reviewed version

1. Obtain explicit approval for the particular reviewed commit. Read its
   compatibility/migration notes; verify Python files and the built card hashes.
   Do not use a moving branch. Do not upgrade Core or HACS as an incidental step.
2. Confirm backup/recovery baseline above and record representative household
   services. Leave the integration in Demonstration mode with racing events off.
3. Stage the complete new Python directory away from `custom_components` and
   outside `www`. At the approved maintenance window, replace only
   `/config/custom_components/nascar_race_center/` as a complete set using the
   existing approved file-transfer method. Preserve its previous complete set
   off-device. Do not copy over a running directory gradually, leave removed
   modules from older versions, or leave a renamed duplicate integration under
   `custom_components`. Do not delete or recreate the config entry.
4. Copy the new built module into `/config/www/nascar-race-center/` under its
   **new versioned filename**, leaving the old module available for recovery.
   Verify its post-transfer hash. Core needs a normal restart for Python changes;
   a config-entry reload does not reliably reload Python modules.
5. After the restart check Logs, Repairs, household services and the same NASCAR
   entry/entities. Only then update the **existing single resource** to the new
   `/local/nascar-race-center/<new-versioned-filename>.js` URL. Do not load two
   versions: custom element registration persists for the current document.
6. Fully reload every open browser/app frontend. A changed filename avoids
   ordinary stale-cache reuse. Hard reload on desktop; close/reopen the companion
   frontend or use its frontend-cache reset control if needed, without deleting
   app account/settings. Verify the downloaded resource bytes/hash and network
   response; do not append random query strings to conceal a mismatched file.
7. Compare entity unique IDs/entity IDs, series/favorites and card entry ID with
   the inventory. Check there are no duplicate entities/resources/subscriptions,
   and repeat the beta smoke/household checks. Record results before retiring
   old files/backups. A restarted browser does not prove an HA restart passed.

Current config flow is **VERSION 1**, default minor version 1, with no custom
config-entry migration; the integration manifest is **0.1.0**, independent of card
**0.5.1**. This Phase 6A does not alter persisted formats. Do not infer a safe
downgrade from an unchanged manifest version: future releases must document
migrations and rollback. If a future version migrates configuration/storage,
restore a verified compatible backup or follow its explicit migration guidance;
copying old code over newer storage is insufficient.

## Roll back the dashboard/card alone

Use this path for a failed custom card when HA and the integration still work.

1. Open an unrelated working HA dashboard, then edit only **NASCAR Race Center
   Beta**. Remove the affected card(s), or restore their saved card configuration.
   You can delete the dedicated beta dashboard from Settings → Dashboards only
   after confirming its title and unique path. Never delete the household
   Overview/default dashboard or replace the entire Lovelace configuration.
2. To return to the prior card, edit the one NASCAR JavaScript resource back to
   the saved old versioned URL and verify its file/hash. If no NASCAR cards remain
   anywhere, remove only that resource. Keep resources used by other custom cards.
3. Fully reload all frontends so the new/old custom-element document is fresh.
   Once no resources reference it, optionally remove only the failed new module.
   Leave unrelated `www` assets intact. Card/resource removal does not remove
   the Python integration, entities, polling or saved options.
4. Confirm household dashboards still load. Check two-card cleanup with browser
   Network WebSocket frames if available; do not close the shared HA socket as a
   snapshot-release shortcut. Native HA owns its other dashboard traffic.

## Roll back Python files while retaining the entry

If Core still starts, stop using the beta card and note the error privately.
Restore the **entire previous known-good** `nascar_race_center` directory and the
matching card resource/file using the saved copies and hashes. Restart Core
normally; a reload alone cannot undo imported Python. Keep the existing config
entry so registry identities/options remain. Verify Logs/Repairs, entity inventory,
calendars, source selection and household automations. If this was the first
installation and no prior working directory exists, use removal below.

If Core cannot start, use the prearranged HA OS file/recovery route to move only
`/config/custom_components/nascar_race_center/` out of `custom_components` into
private recovery storage, then restart Core using the supported console/UI. This
may leave the NASCAR entry unavailable while household HA recovers. If offered,
HA safe mode can help reach the frontend. Do not erase `.storage`, reinstall HA,
power-cycle repeatedly, change UniFi settings or alter unrelated components.
After Core recovers, either restore reviewed working files or remove the NASCAR
entry through the UI. Escalate to the backup route if recovery remains uncertain.

## Remove the integration only

1. First remove NASCAR cards/resources (above) or expect their entry-unavailable
   state. If you previously created any **NASCAR-specific** blueprint automations,
   disable/remove only those after recording their configuration. The default
   beta creates none. Do not disable household automations in bulk.
2. In **Settings → Devices & services**, locate NASCAR Race Center and delete
   **only its config entry**, using its ⋮ menu and checking the name. HA unloads
   its sensor/binary-sensor/calendar platforms and entry-owned work. The removal
   hook removes only its compact event ledger and live-polling reservation.
3. Verify the entry/entities are removed and household services still work.
   Recorder history may remain according to HA's normal retention policy;
   removal is not a promise of purging history. Do not delete the database or
   purge unrelated entities. Keep saved private evidence/backups.
4. Optionally remove only `/config/custom_components/nascar_race_center/` and
   restart Core. Keep every other integration directory intact. Removing files
   before removing the entry can make the UI cleanup harder.
5. Re-adding through Add integration creates a **new installation identity**.
   Review favorites and update the card entry selection and any NASCAR-only
   references. Do not promise old entity IDs or event deduplication will survive
   deletion. To recover the exact old registry/entry state, use a verified
   compatible backup; do not manually transplant `.storage` files.

## Full backup restoration — recovery of last resort

Obtain explicit owner approval for the specific backup and restore scope first:
restoring the full system can rewind **all** household configuration/database,
apps and automations since that backup. Record the expected loss and save the
current state if possible. Through the supported HA backup/OS recovery interface,
select the previously verified full backup, supply its saved key privately, check
its timestamp/components, and follow HA's restore flow. Never treat a checksum
as proof that restoration will succeed. Do not interrupt power during restore.

After HA finishes, verify Core/OS versions, login, integrations, household
dashboards/automations, database availability, restored file hashes and entity
inventory. Record restoration as PASS only after those checks actually finish.
If failed or unattempted, record FAIL/NOT TESTED and stop the beta. No restoration,
production restart, installation or network change was executed by this phase.
