# Phase 6A — controlled Home Assistant OS beta installation

This is an owner-operated **Demonstration-only** beta on the HP EliteDesk 705 G4
Mini. It is not a release or permission to install. Review the PR and obtain the
owner's explicit installation/restart approval before following the HA steps.
No access to that machine is assumed. Leave its Ethernet and UniFi Dream Machine
configuration alone. Existing household services take priority.

Use this guide with the [acceptance checklist](PHASE6A_BETA_CHECKLIST.md),
[rollback guide](PHASE6A_ROLLBACK.md) and [validation record](PHASE6A_VALIDATION.md).
Record PASS, FAIL or NOT TESTED with evidence; a blank checkbox is not a pass.

## 1. Check compatibility and establish a recovery route — required

1. Sign in to Home Assistant as an administrator. Open **Settings → System →
   Repairs → ⋮ → System information** (or **Settings → About**, where offered).
   Record Core, Frontend, Supervisor and Operating System versions, installation
   type, free disk space, timezone and the browser/app version in the checklist.
   Do not paste internal URLs or the complete system-information report publicly.
2. The tested baseline is **Core 2026.10.2**, Python **3.14.8**, HA frontend
   **20260930.4**. `hacs.json` declares Core 2026.10.2 as the minimum. Earlier
   Core versions are unsupported; newer versions need their own check. HA OS
   supplies Python: do **not** install Python, pip, Node or npm on HA OS. Do not
   upgrade a working household HA installation merely to run this beta; if it
   differs, stop for a compatibility decision using a separate development HA.
3. Choose a maintenance window when a short HA restart will not interrupt an
   important automation. List representative existing lights/sensors/automations
   and their present state. Record existing dashboards, integrations and resource
   URLs using screenshots or private exports. Preserve any existing NASCAR files
   and options as described in the rollback guide. Do not edit household YAML.
4. Confirm an already working, owner-approved way to manage `/config` files even
   if Core cannot start, such as an existing Samba share or supported editor/app
   independent of the Core frontend. Confirm the owner can reach the HA OS
   console/recovery interface. A dashboard-only file editor is not a complete
   recovery route. If no suitable file-transfer/recovery method exists, stop and
   arrange one separately; enabling SSH or installing an app is not a required
   automatic step of this beta.

## 2. Make and verify a full backup — required before changing anything

1. Open **Settings → System → Backups**. Choose **Backup now** / the manual backup
   action. Select the full system: Home Assistant configuration/database and all
   installed apps/add-ons; include media/share folders where the UI offers them.
   Record exactly what is included and excluded. Name it, for example,
   `Before NASCAR Phase6A YYYY-MM-DD`. Wait until it completes without errors.
   Do not proceed while another backup, update or database migration is running.
2. Open its details: check success, timestamp, contents and plausible size. A
   filename or a scheduled-backup setting alone is insufficient. Download a copy
   to another computer/storage location; verify the download completes and the
   size agrees with the backup details. Record a SHA-256 of the downloaded file
   privately so later corruption can be detected. Keep it outside the HA disk.
3. Save the backup emergency kit/encryption key/password through HA's supported
   backup controls in a separate secure place; verify the owner can retrieve it.
   Never commit or send the key, backup, `.storage`, database or access tokens.
4. Record verification separately: **creation PASS**, **off-device copy PASS**,
   **key retrievable PASS**, **restore rehearsal PASS or NOT TESTED**. Successful
   download/checksum does not prove restoration. A restore rehearsal needs a
   separate authorized isolated HA target; never rehearse by restoring over the
   household instance. If no recovery route or usable backup/key is confirmed,
   stop. If restoration is untested, record that limitation for the owner's
   installation decision. Keep the previous known-good backup too.

## 3. Obtain the exact reviewed candidate — required, on a separate computer

The runtime candidate is merged Phase 5C / PR #13, commit
**`ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972`**. Phase 6A adds tests and procedures;
it does not change these production files. Do not download a moving branch or
build a new module on the HA machine.

1. While signed into an account allowed to read this repository, open the
   [pinned commit](https://github.com/rosslandgraf/ha-nascar-race-center/tree/ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972),
   then download the [pinned ZIP](https://github.com/rosslandgraf/ha-nascar-race-center/archive/ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972.zip). Confirm the displayed commit, extract locally,
   and retain the original archive. A private-repository download needs your
   normal GitHub login; it does not require giving HA GitHub credentials.
   Alternatively use `git clone` on your computer and
   `git checkout --detach ec35f257ccaa37c6a4d15a26d2fd4ea6e0257972`;
   `git rev-parse HEAD` must match exactly.
2. Use only `custom_components/nascar_race_center/` and the already built
   `frontend/dist/nascar-race-center-card-0.5.1.js`. Never copy the whole repository,
   tests, fixtures, demo preview, `work`, `.git`, `node_modules` or Python caches
   into HA. No requirements download is needed: manifest `requirements` is empty;
   Lit and its license notices are bundled in the JavaScript.
3. Verify the JavaScript SHA-256 before copying and after transfer/download from
   HA. Expected file size **149,263 bytes**, SHA-256:

   ```text
   dd23b8e40704f7d5b0766d5d8ac12816c08e19832e241e8d75616fd2591dae2c
   ```

   On Windows PowerShell run `Get-FileHash .\nascar-race-center-card-0.5.1.js
   -Algorithm SHA256` on one line. On macOS use
   `shasum -a 256 nascar-race-center-card-0.5.1.js`; on Linux use
   `sha256sum nascar-race-center-card-0.5.1.js`. Match every character (hex case is
   immaterial). The full [runtime file manifest](PHASE6A_ARTIFACTS.sha256) also
   identifies the Python files. On a computer with `sha256sum`, run
   `sha256sum -c /path/to/PHASE6A_ARTIFACTS.sha256` from the extracted repository
   root. Every listed file must pass. These hashes identify the reviewed files;
   obtain the manifest through the reviewed Phase 6A PR.

## 4. Copy the integration and restart safely — required

1. Using the existing approved file-transfer method, inspect
   `/config/custom_components/nascar_race_center/` and
   `/config/www/nascar-race-center/` **before** copying. If either exists, stop
   and save its complete contents off-device, record its origin/version/hash and
   follow the update procedure. Do not merge old/new Python files or silently
   overwrite an unknown JavaScript file. Check the resource list for duplicates.
2. Create the missing parent directories without replacing existing directories.
   Copy the **contents** of the candidate integration folder into exactly:

   ```text
   /config/custom_components/nascar_race_center/manifest.json
   /config/custom_components/nascar_race_center/__init__.py
   /config/custom_components/nascar_race_center/config_flow.py
   /config/custom_components/nascar_race_center/translations/en.json
   ...all other files from that integration folder
   ```

   There must not be an extra nested `nascar_race_center` or repository directory.
   Keep every other directory under `custom_components` intact. Compare the file
   list and hashes with the downloaded candidate; transfer tools must preserve
   bytes. Use the manifest to verify the transferred files on a computer if HA
   has no checksum command.
3. Copy the module to exactly:
   `/config/www/nascar-race-center/nascar-race-center-card-0.5.1.js`.
   Preserve any previous version under its old filename. Files in `www` are
   served through `/local/`; put no backup, credential or private configuration
   there. No frontend resource is registered automatically.
4. Run the UI's **Check configuration** action if available under Developer Tools
   (enable Advanced Mode in your profile if needed). Resolve existing errors
   before restarting; a successful check alone does not prove custom integration
   startup. Use **Settings → System → Restart Home Assistant** (in the power/⋮
   menu on some versions), then choose the normal Core restart. Avoid hard power
   loss and avoid restarting/rebooting network equipment.
5. Wait for HA to reconnect. Check **Settings → System → Logs** and Repairs for
   new errors, then verify the recorded household services. A normal warning
   about an unreviewed custom integration may appear; repeated setup errors,
   safe mode, unavailable household services or growing errors are a FAIL. Stop
   and use rollback before proceeding.

## 5. Configure Demonstration mode — required

1. Open **Settings → Devices & services → Add integration**, search for
   **NASCAR Race Center**, and open it. If absent, confirm folder nesting and
   the completed restart. Do not add YAML or install dependencies to fix it.
2. Leave **Data source: Demonstration** selected. Do not choose NASCAR CF or
   acknowledge data-use authorization. Keep conservative defaults and racing
   events disabled; create no notification/lighting blueprint automation.
   Select the national series to test (1, 2, 3). For the simplest run choose all
   three; one entry manages them. Finish the flow only once.
3. Open its **Configure** options to add fictional favorites, for example
   **Demo Alex Driver (99001)** and **Demo Jordan Driver (99002)**. Save; a brief
   config-entry reload is expected. Verify series calendars and metadata entities.
   Demo live-position/timing/scoring entities can be unavailable: that is expected,
   not an instruction to enable CF. Disabled-by-default metrics can remain disabled.
4. Use the entry's ⋮ **Download diagnostics** action. Review the integration
   section for provider `demo`, selected series, successful schedules/references,
   favorite count and no live timing. HA's downloaded diagnostics wrapper may
   also contain HA/system metadata; review the entire download before sharing.
   Store evidence privately. Do not upload whole logs or enable global debug logging.

## 6. Register the module and create a separate dashboard — required for card beta

1. Open **Settings → Dashboards → ⋮ → Resources** with Advanced Mode enabled.
   Add one resource with type **JavaScript Module** and exact URL:
   `/local/nascar-race-center/nascar-race-center-card-0.5.1.js`.
   Do not add multiple versions of the same custom element. For an existing
   YAML-managed resource list, the owner must review a single equivalent
   `url`/`type: module` addition and check configuration; do not replace the list
   or switch dashboard storage modes.
2. Reload the browser. If this is HA's first `www` directory, the earlier restart
   enables local serving. Open the `/local/` resource using your current HA origin;
   verify HTTP 200/JavaScript rather than a login/error HTML page. Download it and
   compare the hash from step 3. A missing custom element usually means a wrong
   path, wrong resource type, stale cache or failed module load.
3. In **Settings → Dashboards**, choose **Add dashboard → New dashboard from
   scratch**, title **NASCAR Race Center Beta**, and a unique URL path such as
   `nascar-beta`. Leave existing dashboards/default selection unchanged. Use an
   administrator-only dashboard visibility option where available; visibility is
   a convenience, while the API independently enforces administrator access.
4. Open only this new dashboard, choose **Edit dashboard → Add card**, then
   **NASCAR Race Center**. In its custom-card editor select the loaded NASCAR
   integration entry, selected series and initial view **Race Center**. Save.
   Do not infer `entry_id` from an entity name or fabricate an ID. A manual
   alternative is documented in [FRONTEND.md](FRONTEND.md). A wide Sections view
   is useful but optional; a narrow card must still be usable.
5. Exercise **Race Center, Live Timing, Race Weekend, History, Analytics** using
   the exact demo expectations in the checklist. Favorites are changed in the
   integration options, not in the card. Always keep fictional labels visible.
6. Open the new dashboard from a desktop browser and your phone browser as an
   administrator. Record the actual browser/app versions and results. Phone,
   companion app, screen reader and owner-hardware checks remain **NOT TESTED**
   until the owner performs them. A normal non-administrator account must see an
   access error for the card, while unrelated household dashboards keep working.

## Optional follow-up, only after the basic checks pass

Add a second card to the beta dashboard, try Compact density, light/dark themes,
tablet layouts, browser zoom and the two-hour observation procedure. Avoid
enabling racing events on a live household automation: production demo cannot
exercise live transitions. Controlled rich replay belongs in a separate test
harness, clearly synthetic. Neither live CF acceptance nor Phase 6B is authorized
by successful offline installation. Stop on a new household regression; use the
separate dashboard/integration rollback paths before considering full restoration.
