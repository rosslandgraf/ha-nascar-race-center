# Existing installation → one managed integration

Candidate **integration 0.2.1 / card 0.6.1**, Core 2026.10.2. This is an owner
procedure, not an installation already performed. The repository is currently
private: **HACS adoption is blocked until an approved public distribution exists**.
No token, custom repository setting or private-repository workaround closes that
gate. Current manual installations continue working while approvals are pending.

For an existing bundled 0.2.0 installation, follow the current
[0.2.1 upgrade and rollback guide](REAL_CF_UPGRADE.md). Its resource URL stays
unchanged. The one-time resource edit below is for an older `/local/` install.

## Before changing files

1. Record the current versions, NASCAR config-entry ID, selected three series,
   favorites/provider, event/polling preferences and representative entity IDs.
   Save the existing NASCAR dashboard/card configuration and resource list. Check
   a few unrelated household integrations/automations as a baseline.
2. Take/download a full HA backup and confirm its supported restore route. Save
   the entire existing `/config/custom_components/nascar_race_center/`, existing
   versioned JS and its resource URL. Preserve old `/config/www/` files for rollback.
   Do not delete the integration entry, dashboard or edit `.storage`.
3. Confirm which public distribution repository and exact reviewed release the
   owner approved. Check the release notes, integration/card compatibility and
   `SHA256SUMS`. Match the domain **nascar_race_center**. Use just one repository
   to manage it; do not install a second dashboard/plugin repository for this card.
   HACS is a separate prerequisite on HA OS 2026.10.2; follow its official setup
   if it is not already installed. This PR installs neither HACS nor the package.

## Adopt through HACS after approval

4. In HACS, use **Custom repositories**, enter the approved public repository,
   choose **Integration**, and add it. Choose/download the approved release.
   GitHub authorization does not make a private development repository supported.
   HACS stores the runtime under `/config/custom_components/nascar_race_center/`.
5. HACS may recognize existing files/domain metadata, but that does not prove the
   manual installation is the reviewed release or tracked correctly. Explicitly
   download/re-download the chosen release and verify the HACS repository's
   installed version/update status. Read overwrite prompts: only this integration
   directory should be replaced. Do not use HA's **Delete integration** to migrate.
   HACS does not move the previous `/local/` JS or edit its resource registration.
6. Restart **Home Assistant Core**. HACS downloading files and config-entry reload
   do not replace Python modules already loaded in memory. Finish this restart
   before opening fresh dashboards; code served during a pending file update may
   be unavailable until restart. Check the same config entry loads, with provider,
   series, preferences and entity IDs preserved. Do not switch providers to adopt
   packaging; CF permission and polling behavior are unchanged.
7. In **Settings → Dashboards → Resources** (Advanced Mode if needed), edit the
   existing NASCAR module resource from `/local/nascar-race-center/...js` to
   **`/nascar_race_center/card.js`**, type **JavaScript Module**. Edit it once;
   do not append another NASCAR module. If YAML manages resources, replace only
   that NASCAR URL and preserve `type: module` and all other entries. If duplicate
   NASCAR resources already exist, remove only the known duplicates after backup.
   Keep every unrelated resource, dashboard, `entry_id` and card option.
   For YAML-managed resources, apply the URL edit with **Developer tools →
   Actions → `lovelace.reload_resources`** (available in YAML resource mode),
   or validate the configuration and restart Core after the edit. A browser
   refresh alone does not reload HA's YAML resource list. Apply this same step
   when restoring a saved YAML resource URL during rollback.
8. Fully reload/close and reopen dashboard documents on each browser/tablet or
   companion client. A registered custom element cannot be upgraded inside its
   existing document. Reset the companion frontend cache through its normal UI
   only if ordinary reload still shows the previous footer. Never import both
   the old manual module and the new loader into one document. Legacy 0.5.x files
   do not have the new guards and can still conflict if left registered together.
9. Verify the footer says **Card 0.6.1**, and diagnostics → `packaging` reports
   **integration 0.2.1**, card 0.6.1, `available` and the release's SHA-256. The
   loader request must be `/nascar_race_center/card.js`, `Cache-Control: no-store`;
   its module URL names the card version and full SHA-256 query. No copied JS in
   `/config/www/` is needed for this build. Existing old files may stay as backups;
   unregistered files do not execute.
10. Check existing cards, selected series, favorites, History/Analytics pagination,
    two clients and reconnect/reload, plus the household baseline. Normal Demo
    remains empty for live timing. No extra CF request or provider change is
    necessary to verify packaging. Record any hardware/companion/soak gaps.

Before public adoption is possible, an owner-approved manual preview can replace
only the complete integration directory from the reviewed checkout/archive, then
follow steps 6–10. Its compiled JS is already inside that directory. This still
requires one final manual file transfer; it does not establish private HACS support.
The private preview ZIP is an inspection/manual-install artifact, not a published
HACS release or special `zip_release` asset.

## Normal future update

Developer merges reviewed code → owner approves a specific publication → the
approved public repository gets a tested `v<integration version>` **release** →
HACS detects that version → owner installs through HACS → restart Core → reload
browser documents. Tags alone are not the release-based update channel. Each
release pins one compatible card version/hash. Even frontend-only changes must
advance the integration distribution version because HACS tracks the integration.
Do not overwrite/rebuild an existing release in place.

The stable resource URL stays the same. Its small generated loader is never
HTTP-cached; it imports the exact versioned/hashed module with normal static-file
caching. No automatic resource registration, dashboard rewrites, new polling,
background updater or arbitrary JavaScript download is introduced. Existing open
documents retain their old code until reloaded; this is not a hot-update system.

## Rollback

- In HACS, select/re-download the previous approved compatible release where
  available. Restore both its Python directory and bundled card together, restart
  Core, then reload browser documents. Within the bundled distribution line,
  `/nascar_race_center/card.js` stays unchanged and selects that release's module.
- To return to the last separate pair, use the saved full directory and saved
  `/local/...` resource/file. The merged PR #16 baseline is commit
  `7ca9d4d8d0ed837005adf366dcd5a5ecd9ae7a60`: integration 0.1.2 and
  `frontend/dist/nascar-race-center-card-0.5.3.js`. Verify its
  `docs/CF_READINESS_ARTIFACTS.sha256` on that checkout. Earlier 0.1.1/0.5.2 and
  0.1.0/0.5.1 pairs require their own saved or pinned files. Do not leave the new
  loader registered against Python versions that never served it.
- Preserve the entry and dashboard through rollback. Never clear persisted CF
  request guards to get an early request. Use the supported full-backup restore
  route if Core cannot start or the household baseline regresses.

## Uninstall or temporary disable

For temporary troubleshooting, disable the existing HA entry to stop its data
work; keep its settings for re-enable. Do not delete it to update or roll back.
For package removal, disable the entry, remove only the NASCAR resource, remove
this Integration package through HACS and restart Core. HACS removes its managed
component directory; it does not clean the old manual `/config/www/` backups or
all user dashboard references. Remove those only if intentionally abandoning them.

Permanent deletion of the config entry through HA is a separate owner choice and
removes its entities and compact integration-owned event/request ledgers as usual.
This is unnecessary for migration. Supported HA static routes have process
lifetime: disabling/removing the last entry can leave **code-only** routes until
restart; authenticated data commands reject unloaded entries, and removed files
return 404. No private route-unregistration hack or unrelated file cleanup is used.
