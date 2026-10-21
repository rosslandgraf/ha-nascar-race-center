# Observed NASCAR API reference assessment

Reviewed October 21, 2026. **No confirmed structural defect in this package
requires a Phase 3A code fix before an experimental development merge.** This
does not satisfy the roadmap's active-session acceptance or release gates.
Keep those gates open; do not describe this import as live validation.

## Scope, provenance and branch relationship

- Main reviewed: [`fb881201a31d7c320c263f4d83e4a09b2b789c11`](https://github.com/rosslandgraf/ha-nascar-race-center/tree/fb881201a31d7c320c263f4d83e4a09b2b789c11).
  The original checkout was clean on local branch `work`; its old remote-main
  tracking ref was refreshed before creating the documentation branch/worktree.
- The actual Phase 3A work is [PR #3](https://github.com/rosslandgraf/ha-nascar-race-center/pull/3),
  `phase-3a-live-timing`, **open and unmerged** at reviewed head
  [`9aa4e0f495c71d9f636114aaddfa9c248c86f9cf`](https://github.com/rosslandgraf/ha-nascar-race-center/tree/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf).
  It was the only open PR before this import. Its 50-file diff and current
  parsers/models/freshness projections were read using a detached worktree;
  its branch and PR were not edited. This assessment is pinned to those commits.
- This documentation branch starts directly from main, with no Phase 3A commits.
  The 78 archive files are preserved byte-for-byte under
  [nascar-api-reference](nascar-api-reference/START_HERE.md). Archive instructions,
  including its original development brief, are historical reference data;
  they do not authorize implementation, execution, networking or later phases.
- The package records **28 endpoint attempts: 24 populated JSON responses, one
  empty successful article envelope (25), and three HTTP 403 XML denials
  (26–28)**. These are supplied capture observations, not requests made in this
  review, and are separate from PR #3's earlier proxy-CONNECT failures. Neither
  result invalidates the other network/time-specific observation.
- [Structural samples](nascar-api-reference/README.md) contain redacted scalar
  placeholders and collapsed array shapes. They are not original NASCAR response
  fixtures, valid replay inputs, race facts or production fallback data. Source
  JSON response hashes in the [manifest](nascar-api-reference/Documentation/manifest.json)
  cannot be verified without the excluded private originals; distribution
  checksums verify only the supplied files, not authenticity or source truth.
  No ZIP, private raw captures, credentials, media or runtime fallback is imported.
- Repository phase definitions govern: main has a broad Phase 3;
  [PR #3's roadmap](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/ROADMAP.md#phase-3a--live-race-timing-and-leaderboards)
  defines 3A as timing/leaderboards, leaves pits/stages/points/events to later
  3B/3C assignments, and assigns history/analytics to **Phase 4**. The package's
  provisional mapping of history to 3C must not replace that roadmap.

## Findings and merge impact

Code links below are immutable; line numbers refer to the reviewed commits.
Evidence IDs refer to the package's endpoint IDs, not PR numbers. The
[field profiles](nascar-api-reference/Documentation/field_profiles.json),
[relationships](nascar-api-reference/Documentation/verified_relationships.json)
and [findings](nascar-api-reference/Documentation/findings.md) retain the relevant
paths, types and limited factual comparisons without reconstructing raw captures.

| Finding and evidence | Existing assumption and exact code reference | Affected scope / disposition |
| --- | --- | --- |
| **Live structure agrees.** 01/21 expose an object, `vehicles[]`, nested `driver.driver_id`, `running_position`, `starting_position`, lap times/speeds, `delta`, Boolean `is_on_track`, string `vehicle_number`, and `laps_led[]` intervals. 01 has 37 vehicles. | Main reads only context in [`models.py:323`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L323). 3A adds optional scoring in [`models.py:339`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/models.py#L339) and [`timing.py:121`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/timing.py#L121). Extra fields such as embedded pits/stage are ignored. | Main and 3A: structural support is corroborated, not requiredness, complete roster coverage or semantic correctness across sessions. No merge blocker. |
| **Driver namespace agrees.** 07 separates numeric `Nascar_Driver_ID` from string `Driver_ID` (observed example 4023 versus `"374500"`). All 37 live driver IDs join the NASCAR namespace. Historical `NASCARDriverID` and points `membership_id` have distinct spellings/roles. | Main/3A [`reference.py:129`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/reference.py#L129) uses `Nascar_Driver_ID`; 3A [`timing.py:132`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/timing.py#L132) uses nested `driver_id`. String car numbers remain display data. | Main and 3A agree. Future adapters must normalize documented namespaces explicitly; no name/car/secondary-ID join. No merge blocker. |
| **Global feeds conflict.** Relationship evidence records 01 race **5633**, 05 stages race **5168**, and 04 points `series_id/race_id/run_id` all **0**; legacy points 22 also have zero context. 02 flags and 03 pits lack explicit race context. | The actual provider calls only global 01 for live data: [`provider.py:84`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/provider.py#L84). 3A routes its reported series in [`coordinator.py:297`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/coordinator.py#L297) and replaces snapshots at [`coordinator.py:349`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/coordinator.py#L349); it does not join those other feeds. | Future 3B/3C: **block automatic joins** until series/race/run/provenance can be established. Zero is unknown context, never the active race. Not a 3A blocker; freshness cannot establish cross-feed identity. |
| **Session namespaces are not interchangeable.** 13 has weekend run IDs 5497/5498 and timing IDs 6/9; race timing ID and 19 stage run ID are 10. | 3A's [`models.py:96`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/models.py#L96) keys its reported live context by series/race/run; it does not equate weekend or historical IDs. Main schedule IDs derive from season/series/race/kind/name in [`models.py:121`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L121). | 3A is consistent with its single-feed boundary. Future 3B/3C and Phase 4 need explicit mappings; schedule IDs are internal, not provider timing IDs. Rename stability and missing run IDs remain unverified. |
| **Timestamp representation agrees for live; schedule usability remains limited.** 01 has `2026-10-21T04:04:25.0191231-07:00`; numeric `time_of_day` is not established as Unix time. 06/09–12 and embedded schedules have offset-free datetime strings, including `*_utc`. | Main [`models.py:108`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L108) / 3A [`models.py:124`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/models.py#L124) accepts explicit offsets and uses `fromisoformat`; numeric source clocks are not substituted. `_session` and race parsing use this same conservative helper. | Main and 3A: live format supported, with sub-microsecond precision truncated by Python. Captured schedule starts/ends remain unknown, so calendars/next-race selection can be empty despite populated schedules. Existing documented limitation; obtain timezone semantics before a separate adapter fix. No blind UTC/local-time assignment and no new 3A regression. |
| **Schedule envelopes agree; completeness/date meaning differ.** 06 is keyed by `series_1/2/3`; 12 is a bare array. 09 Cup race 5696 is absent from 06; 06's first Cup `date_scheduled` differs from `race_date`. | Main [`models.py:179`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L179) intentionally consumes global 06, not bare 12. [`models.py:233`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L233) parses session arrays; [`models.py:292`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L292) retains detailed-only races. Basic starts use `date_scheduled`. These functions are unchanged in 3A. | Main/3A: race 5696 is not inherently dropped by the merge. Universal completeness, cancellation and authoritative revised-start selection remain unverified. Resolve scheduled-versus-actual date semantics in later schedule work; not a 3A blocker. |
| **Numeric strings/nulls need endpoint-specific handling.** 14 `LapSpeed` has 17,611 numeric strings and 36 nulls; lap-zero `LapTime` is null. 22 wins/top-five/top-ten/poles mix integers and strings. | 3A [`timing.py:91`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/timing.py#L91) accepts finite numeric strings and returns unknown for null/invalid optional timing. This live parser is not a historical parser. | 3A's numeric handling agrees with 01's integer/number variation. Future points and Phase 4 must support their observed string/null combinations without zero defaults. No current code reads 14/22. |
| **Sentinels and pit shapes cannot be generalized.** Findings record 999 averages with null ranks in 17/24, -1 pit durations in 18, zero-time embedded pit entries, and `positions_gained_lossed` versus standalone pit fields. Driver metadata includes empty strings and year-0001 dates. | 3A [`timing.py:91`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/timing.py#L91) rejects nonpositive lap time/speed, but would accept positive 999 if reused indiscriminately. Main/3A ignore pits, historical averages and DOB/DOD; [`reference.py:115`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/reference.py#L115) and [`reference.py:179`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/reference.py#L179) read supported directory/track metadata only. | Future 3B/3C/Phase 4: define sentinel policies per field after semantic confirmation; array length is not a completed pit-stop count. No evidence of a 999 sentinel in consumed 01 lap metrics, so do not invent a global filter. Not a 3A blocker. |
| **Enums, units and freshness semantics remain unverified.** 01 has flag 9, statuses 1/3, lap 312 and zero laps remaining. Observed code domains do not define their meanings. Fresh headers/source clocks cannot prove an active race or coherent scoring. | Main [`models.py:333`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/models.py#L333) maps community flag/run codes. 3A [`timing.py:44`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/timing.py#L44) maps only status 1 to running; [`live_view.py:33`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/live_view.py#L33) requires health `ok` for scoring and supported flags for progress. [`live_driver_sensor.py:34`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/live_driver_sensor.py#L34) labels lap time seconds but leaves delta units unspecified; `elapsed_seconds` in [`models.py:381`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/9aa4e0f495c71d9f636114aaddfa9c248c86f9cf/custom_components/nascar_race_center/models.py#L381) remains a semantic assumption. | Main and 3A: no contradiction established, but the package cannot certify those mappings/units, the 15-minute age policy, transitions, official results or concurrent-series coverage. **Blocks claims of validated live/production readiness**, not a newly confirmed structural fix for this experimental PR. |
| **Empty/denied responses remain outside implementation.** 25 has only `response.news.article: []`; 26–28 report HTTP 403 `MissingKey`. 20 supplies media metadata only. | The existing [`endpoints.py`](https://github.com/rosslandgraf/ha-nascar-race-center/blob/fb881201a31d7c320c263f4d83e4a09b2b789c11/custom_components/nascar_race_center/endpoints.py) and provider do not consume these feeds. | Future scope: no populated article schema, Drive JSON schema or playback permission established. No authentication workaround or expansion warranted. No 3A blocker. |

## Recommended follow-up changes, separately for review

1. Before adding pits/stages/points, design explicit context validation and
   capability/unknown states for mismatches and zero or absent IDs. Add
   appropriately sourced structural and replay coverage in that future code PR;
   do not attach the global stage/points snapshots to 3A's current leaderboard.
2. In a schedule-focused change, establish the timezone contract for naive
   UTC-named fields and precedence of scheduled versus revised race times before
   changing `_timestamp` callers. Keep unmatched detailed races and the current
   safe unknown behavior until that contract is supported.
3. In Phase 4, implement separate historical envelopes, driver/session namespace
   mappings, numeric-string/null normalization and per-field sentinel rules.
   Do not reuse the live parser as a universal historical decoder.
4. Before claiming active-session acceptance, obtain authorized original
   captures/replays that verify source clock meaning, flag/status transitions,
   lap units, gaps, freshness, reset/series switching and optional-feed outages.
   Future automation work still requires baseline suppression and durable
   restart/replay deduplication. Permission, polling cadence, media rights and
   public release gates remain unresolved; MIT licenses project code only.

No code fixes are included or requested on PR #3 by this documentation change.
Merge this reference PR first if convenient so reviewers can cite the evidence;
there is no code dependency or required merge order. PR #3's separate `docs/api/`
library records earlier synthetic/proxy evidence. Preserve it and reconcile its
historical wording with this supplied observation set in a later documentation
change. If both branches edit README, resolve only that documentation overlap
during normal review; do not rewrite the Phase 3A branch as part of this import.

## Checks performed and limits

- ZIP member safety/inventory inspection; read `START_HERE.md` first; reviewed
  metadata, structural samples, profiles, findings and relationship evidence.
- Distribution SHA-256 verification before and after import: **77 entries**;
  checksum file itself is excluded by its design. All **78 archive files** retain
  their paths and bytes, with no extra files inside the imported package.
- Parsed all **58 JSON and three XML files**; checked manifest endpoint/artifact
  inventory and request-evidence consistency. The denial entries have null JSON
  filenames; their separately linked XML artifacts match their recorded hashes.
  Checked **120 relative Markdown links/anchors**
  in the import, assessment and repository index; external URLs were
  not fetched. Reviewed imported file types/content for raw captures and secrets.
- Read-only parser probes with prepared Python 3.14.8: both reviewed versions
  parse the captured offset/seven-fractional-digit timestamp to
  `2026-10-21T11:04:25.019123+00:00`, reject naive/year-0001 naive dates and handle
  decimal integer strings/null/negative integers conservatively. Handmade 3A
  probes also confirm string car numbers, numeric-string lap times, null/negative
  optional timing and scoring suppression for unknown freshness. These scratch
  probes are not committed tests, raw-response replay or live-session validation.
- Final path/diff review and `git diff --check`; no integration, fixture, test,
  dependency, workflow or runtime files changed. Repository configuration has
  no dedicated Markdown/documentation lint command.
- **Not run for this documentation-only change:** pytest suite, Ruff, mypy,
  Hassfest, HACS, HA runtime/browser checks, NASCAR network probes or active-session
  replay. PR #3's historical 330-test/check reports were read, not rerun here;
  hosted checks on the new PR must be reported separately.
