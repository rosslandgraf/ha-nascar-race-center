# Update 0.1.0 / 0.5.1 to 0.1.1 / 0.5.2, or roll back

This is a review candidate, not a published release. Install only the exact reviewed
PR commit you choose; record that SHA. Keep Demonstration mode and current polling,
series, favorites and event settings. These instructions do not authorize changes
to other integrations or the owner's installation by an agent.

1. Before a maintenance window, make a Home Assistant backup and confirm your
   existing recovery/file-transfer method works. Save private copies of the complete
   installed `/config/custom_components/nascar_race_center/` directory, the current
   0.5.1 module, the single NASCAR resource URL/type, card YAML/entry ID, entity IDs
   and representative household automation/service behavior. Keep backups outside
   `www` and outside `custom_components`; never commit `.storage` or credentials.
2. Obtain the reviewed commit's **complete** `custom_components/nascar_race_center/`
   directory and `frontend/dist/nascar-race-center-card-0.5.2.js`. On a checkout of
   that exact commit run `sha256sum -c docs/SNAPSHOT_FIX_ARTIFACTS.sha256` (or compare
   SHA-256 with PowerShell `Get-FileHash` / macOS `shasum -a 256`). The manifest must
   say **0.1.1**. The 0.5.2 module SHA-256 is
   `f124cc6585433fc26d2f5eedfab06d1aecb3bc880822708f109dc39f50d01f0b`.
   Do not use source TypeScript, a moving main, or a partial Python set.
3. Stage Python files privately away from the active integration. At the approved
   window replace only `/config/custom_components/nascar_race_center/` as a complete
   set, preserving its prior set off-device. Do not leave duplicate integration
   directories under `custom_components` or alter the existing config entry.
4. Copy the built card to
   `/config/www/nascar-race-center/nascar-race-center-card-0.5.2.js`, leaving 0.5.1
   available for rollback. Verify transferred hashes. Restart Home Assistant Core
   normally to load Python **0.1.1**; config-entry reload alone does not reload
   imported Python. Check Logs/Repairs, the same entry/entity IDs, calendars and
   representative existing household services/automations before proceeding.
5. Edit the **existing single** NASCAR JavaScript module resource from
   `/local/nascar-race-center/nascar-race-center-card-0.5.1.js` to
   `/local/nascar-race-center/nascar-race-center-card-0.5.2.js`, type **JavaScript
   module**. Do not add a second resource or change other resources. Fully reload
   every desktop browser and companion frontend; custom elements cannot be replaced
   in an already loaded document. Verify Network downloaded the 0.5.2 filename and
   matching bytes, and the card About/version reports 0.5.2. Use the companion's
   frontend-cache reset only if needed, preserving its account and settings.
6. In Demonstration mode, try 20 different small History/Analytics selections,
   switch tabs, revisit a retained page, and use two cards. Opening pits, stages and
   points without a race should show a normal empty notice and send no live-detail
   commands. Check a normal Core restart/reconnect and the same household baseline.
   Record actual physical results; automated fixture/browser results do not replace
   them. No provider change, NASCAR endpoint probe, or polling adjustment is needed.

Update Python first and card second. Card 0.5.2's release workflow requires the
0.1.1 backend; an older backend returns `unknown_command` for release and cannot
provide this cleanup guarantee. Card 0.5.1 can still read API v1 from 0.1.1 but retains
the old exploration restriction. Treat **0.1.1 / 0.5.2** as the supported fix pair.
There is no config-entry migration or storage format change in this fix.

To roll back, restore the **entire saved 0.1.0 Python directory**, retain the same
config entry, restart Core normally, change the single resource back to the saved
`/local/nascar-race-center/nascar-race-center-card-0.5.1.js`, and fully reload all
frontends. Verify its known SHA-256
`dd23b8e40704f7d5b0766d5d8ac12816c08e19832e241e8d75616fd2591dae2c`
and the saved Python hashes (the repository's original
[Phase 6A manifest](PHASE6A_ARTIFACTS.sha256) pins that pair at PR #14). The original
capacity/no-session defects return with that pair. Check the same IDs/options,
Logs/Repairs, calendars and household baseline. Do not remove/recreate the entry,
edit registries, purge Recorder or restore all household state as a routine file
rollback. If Core fails to start, use the established supported recovery route to
move only this integration out of `custom_components`, then restart; follow the
[existing rollback guide](PHASE6A_ROLLBACK.md) for recovery or separately approved
full-backup restoration. Remove the new card file only after no resource uses it.
