# Upgrade the bundled integration: 0.2.0 → 0.2.1

Candidate **integration 0.2.1 / card 0.6.1**, HA OS 2026.10.2. No owner installation
or NASCAR request is performed by this PR. The stable resource remains
**`/nascar_race_center/card.js`**. Keep the existing config entry, three series,
favorite IDs, provider, data-use acknowledgement, events and polling options.
No config-entry or persisted ledger format migration is required.

## Before installation

1. Save a full supported HA backup off-device and verify the recovery route.
   Save the complete installed `custom_components/nascar_race_center/` directory,
   current card/resource configuration, config-entry ID, favorite IDs, selected
   series and representative entity IDs. Record household automation/service
   behavior for comparison. Keep backups outside `www` and `custom_components`.
2. Review the exact PR commit/release and [artifact manifest](REAL_CF_ARTIFACTS.sha256).
   The integration manifest must say 0.2.1, `frontend/bundle.json` must pin 0.2.1 /0.6.1 and its
   exact card SHA-256. For a destination-rewritten export, its own `SHA256SUMS`
   is authoritative; rewriting documentation/issue URLs changes the manifest hash.
   The runtime directory already contains JS and licenses.
   Do not mix files from different version pairs or copy a second JS into `www`.

## Install the approved complete package

3. If an independently approved **public** distribution/release exists, explicitly
   choose/download/re-download that Integration version in HACS and verify its
   installed version. Download tracking is separate from the HA config entry.
   Use one repository for this domain. The private development repository remains
   unsupported by HACS; authentication does not remove that limitation.
4. Before such a release exists, a separately owner-approved manual preview can
   replace only the complete integration directory from this reviewed checkout
   or CI preview ZIP, using the existing recovery/file-transfer method. This is
   still one bundled directory and does not establish private HACS installation.
   Never leave an old/renamed duplicate integration beneath `custom_components`.
5. Restart **Home Assistant Core** normally. Entry reload alone cannot reload
   imported Python or select updated bundled bytes. Do not clear persisted CF
   request reservations/cooldowns to force an early request. A temporarily reserved
   request may delay the first observation safely after restart.
6. Keep the existing **single** module resource `/nascar_race_center/card.js`.
   Fully reload/close and reopen each browser/companion document after Core is up.
   Only use the companion's normal frontend-cache reset if ordinary reload still
   shows an old footer. No new resource or per-upgrade URL edit is required.
   An earlier `/local/...` installation first follows the one-time resource edit
   in [HACS migration](HACS_MIGRATION.md), including its supported YAML reload step.

## Owner acceptance after the update

7. Verify the same entry/entity IDs, provider, series/favorites and event/polling
   preferences. Check logs/repairs and the household baseline. Footer: **Card
   0.6.1**; diagnostics `packaging`: available, integration 0.2.1, card 0.6.1 and
   matching SHA-256. Keep the resource URL unchanged.
8. Recheck schedule counts and the new per-feed timestamp-reason counters. Valid
   named UTC starts should be aware UTC; ambiguous generic/local times and year-1
   ends remain unknown. Compare Talladega qualifying and Homestead practice with
   independently published local times. Check calendars in the actual HA timezone,
   next practice/qualifying/race, chronological weekends and retained history.
9. Verify reference `failed_feeds` no longer includes drivers for the reported
   mixed directory. Compare source/candidate/usable counts and bounded ambiguous-ID
   sample against the actual 915-row response. Inspect the four named cases from
   the evidence report. Previously selected/quarantined IDs must remain stored;
   missing metadata must not become another driver's name or a duplicate entity.
10. Record polling configured/target/effective intervals and constraint/next eligible
    request. Around known sessions, stale prior-race metadata may remain withheld
    while discovery uses the bounded window. A scheduled start is not proof of
    activity. CF requests still cannot occur below 300 seconds or the selected
    higher minimum; backoff, caching and server pauses can make them slower.
11. Owner-operated live acceptance should record all three series and practice,
    qualifying and race, including empty vehicles, cold/stale/retained source,
    run changes and source regression. Do not manufacture activity, increase
    cadence permission or bypass access restrictions to complete a checklist.
    A lap-averages 403 should leave valid peer datasets usable and appear in
    diagnostics/disclosure with HTTP status. Test pagination, two cards and reload.

## Rollback

Re-download the previous approved compatible HACS release where available, or
restore the saved **entire 0.2.0 directory**, restart Core, then reload all browser
documents. Keep `/nascar_race_center/card.js` and the existing config entry and
options. The PR #17 baseline is
`986e49fa458c827e306f37ef5b7d6524e58063e9` (integration 0.2.0 /card 0.6.0); verify
`docs/HACS_PACKAGING_ARTIFACTS.sha256` **on that checkout**, not against 0.2.1 files.
Its bundled card SHA-256 is
`24e89e3cddefdf66703679057e116cfb51bfa0c8c613b6ded9b3f7c4a73e2f94`.

The reported timestamp/directory/polling defects return with 0.2.0. Do not delete
or recreate the entry, hand-edit registries/`.storage`, purge Recorder, or clear
request ledgers. Return to the household baseline; use the supported full-backup
recovery route if Core cannot start. Rollback to a pre-bundled pair additionally
requires its saved `/local/...` resource/file as described in the HACS guide.

Public distribution, default-catalog HACS validation, physical-device migration,
companion behavior and household soak still require their documented approvals
and actual owner acceptance. No public release is produced automatically.
