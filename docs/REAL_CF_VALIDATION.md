# Real-CF schedules, references and session discovery

Candidate **integration 0.2.1 / card 0.6.1**, Home Assistant Core 2026.10.2.
Starts from merged PR #17, `986e49fa458c827e306f37ef5b7d6524e58063e9`, including
PR #15 snapshot lifecycle and PR #16 live-source protections. This is one bug-fix
PR, not deployment, public HACS approval or a new NASCAR cadence authorization.

## Root causes and resulting behavior

1. Schedule sessions passed named UTC fields through the generic offset-required
   parser. Successful HTTP/JSON/schema parsing therefore discarded valid dates.
   Only `start_time_utc` / `end_time_utc` now accept offset-free complete date/time
   values as UTC, after independent published-time corroboration. Explicit offsets
   determine the instant; year-0001 and unusable durations stay unknown. Generic
   local/live times retain their stricter policy. The shared adapter covers all
   three series and preserves detailed-only races and independently valid feeds.
2. Consumers selected the first returned race or retained current race instead of
   the chronological next opportunity. Coordinator next-race selection, compact
   bootstrap sessions, Overview countdown/default selection and Race Weekend now
   prioritize future supported sessions. Completed/canceled and unsupported
   session kinds cannot become upcoming activity. Retained history remains
   accessible through its paginated view. Times/order remain outside session IDs.
3. Conservative discovery considered race starts, missing practice and qualifying
   before the race; unknown times could select six-hour off-season polling. It
   now reuses bounded session windows with the unchanged CF minimum. A known
   session can also bound prior-source nonadvancement delay while that source
   remains withheld. Schedule evidence never creates an active observation.
4. A single conflicting driver name rejected the whole directory. Records are
   now grouped by positive NASCAR identity, cosmetic case/whitespace variants
   merged, and incompatible identities quarantined individually. Current O'Reilly
   and legacy Xfinity slugs both map to series 2. Published per-series metadata
   wins over draft metadata; compatible missing fields merge, contradictory facts
   remain ambiguous. Secondary IDs and car numbers never replace NASCAR IDs.
5. The reported lap-averages 403 is an HTTP denial, not evidence of a parser bug.
   Allowlisted endpoint construction is unchanged. Per-dataset status now retains
   `access_denied` plus HTTP status in bounded diagnostics and the normal History
   disclosure, preserving successful independent results and existing cooldowns.

The owner's request reports 99 races /274 sessions across the three series with
all starts unknown, and a 915-row driver directory rejected despite many valid
IDs. The original three complete JSON/diagnostic files were unavailable. The
[evidence report](REAL_CF_EVIDENCE.md) distinguishes owner findings, inspected
earlier structural archive, independent public schedules and handmade test values.
It specifies exact timestamp rules, all-series before/after examples and the
four driver-ID cases. No new CF endpoint request was made.

The 915-row structural regression yields **772 candidate IDs, 769 usable IDs,
16 zero-ID rows and three quarantined IDs**: 4372, 4234 and 4151. Cosmetic case
4316 merges. These are reproduced expectations, not independently measured
normalization of the missing original file. Existing selected IDs survive even
when their reference metadata is quarantined or unavailable; live identity
continues to work independently of directory availability.

## Polling and resource decisions

The default configured conservative minimum is **300 seconds**. The provider
policy remains `cf_unverified_cadence`, adaptive permission false, provider floor
300 seconds. A configured higher minimum always wins.

| Evidence | Default target / reason |
| --- | --- |
| Supported current active practice, qualifying or race | 300 s / existing conservative activity branch |
| Known supported session within 30 minutes | 300 s / `approaching_session` |
| Bounded published session window | 300 s / `scheduled_window` |
| Next weekend session within six hours after an earlier session | 300 s / `between_sessions` |
| Known next session within seven days or overnight gap | 3,600 s / `idle` |
| Missing/stale/failed schedule coverage or ambiguous relevant times | 3,600 s / `conservative_fallback` |
| Complete usable schedules, no session within seven days | 21,600 s / `off_season` |

The nearest applicable selected-series opportunity wins. A local approach
boundary may shorten a timer but cannot bypass the minimum or issue an early
request. Known ends cap discovery at eight hours; unknown ends permit 30 minutes
of scheduled discovery, followed by hourly checks within an eight-hour trailing
window. This is a bounded discovery policy, not an inferred session duration.

Actual effective intervals can be longer than these targets. Nonadvancement
backoff remains 300/600/1,200/3,600 seconds except that known approaching/scheduled
windows cap that particular delay at **900 seconds**. Failure backoff is retained.
One regression verifies a 300-second target and 900-second retained-source delay,
then a 7,200-second transport pause overriding both. Configured higher minima,
freshness, conditional revalidation, Retry-After, host cooldown and persisted
request reservations remain authoritative. One global LiveCoordinator and the
shared request lock serve every series, favorite and card. No detail poller or
per-series live loop is added. See [full polling policy](POLLING.md).

Unchanged resource safeguards include:

- CF response size: **2 MiB**; driver parser: **10,000 rows**; schedule parsing and
  counters: bounded race/session loops; daily reference refresh and HTTP caching.
- Snapshot reservations: **two per user /four globally**, each at most **24 MiB /
  100,000 records**, five-minute maximum lifetime; explicit release/reuse and
  connection ownership remain intact. No snapshot limits or retention were raised.
- Per-entry dashboard concurrency: **two requests per user /eight total**,
  **30 requests per 10 seconds per user** across tabs, bounded response pagination
  and subscriptions.
- New schedule-normalization summaries: **24 feeds**; recent historical dataset
  summaries: **24 entries**, cleared with the provider. Driver samples: at most
  **20 usable IDs and 20 ambiguous IDs**; reason counters contain no raw names or
  response bodies. Grouped duplicate driver records use sets for bounded work.

## Diagnostics

Existing transport/JSON/parser/source-health sections remain separate. New
`cf_pipeline.schedule_normalization` explains race/session coverage, known versus
unknown starts and bounded timestamp reason counts (`named_utc`, explicit offset,
missing, invalid, ambiguous timezone, year-0001 and invalid duration). These are
the **last successful normalization summaries**; current transport/parser status
must be consulted to distinguish an outage from fresh coverage.

`reference.driver_normalization` reports source/candidate/usable/rejected counts,
draft/publish and unknown-slug/numeric-team anomalies, plus bounded ID samples.
`history.recent_datasets` reports requested identifiers, dataset, availability,
HTTP status and sanitized reason. No tokens, sensitive headers, full response
bodies or owner settings are added. Existing polling diagnostics expose configured,
target/effective interval, constraint, reason and next network eligibility.

## Executed local validation

Prepared Python 3.14.8, HA 2026.10.2, Ruff 0.17.1, mypy 2.4.0, Node 24.19,
npm 11.9, TypeScript 5.9.3 and Playwright 1.56.1; existing environment reused.

| Check | Result |
| --- | --- |
| Complete Python suite | **1,138 passed** in 68.05 s; 86 additional cases beyond PR #17 |
| Ruff / format | Passed |
| mypy | Passed; 45 source files |
| Hassfest | Passed against pinned Core 2026.10.2; zero invalid integrations |
| Independent authenticated HA runtime/service smoke | **1 passed**; separate Core configuration check exit 0 |
| TypeScript / ESLint / Prettier | Passed |
| Frontend Vitest | **84 passed** |
| Chromium / Firefox / WebKit | **195 passed**, 65 per engine, in 7.8 minutes |
| Clean offline npm install/rebuild | Four bundled runtime artifacts reproduced byte for byte |
| Deterministic distribution | Two local exports identical; archive manifest verifies every member |
| Official HACS validation | **Skipped for private repository; not a pass** |

Browser coverage includes next weekends and chronological practice/qualifying/
race across all series, Eastern/Central/Pacific rendering, partial 403 disclosure,
snapshot pagination/reuse/expiry/multi-card cleanup, no-session details, source
changes, accessibility and native bundled serving. New native persistence cases
start **three real Core processes** against test-owned HA storage, replace the
whole component package, and roll back while preserving favorite IDs, entry and
entity mappings. Synthetic replacement card versions exercise the cache contract;
they do not claim an actual public HACS update or physical-device migration.

Python coverage retains PR #16 full-field, practice/qualifying/race, empty vehicles,
source regression and series/run/race transition checks; PR #15 ownership,
cancellation, active-request protection and bounded snapshot lifecycle; PR #17
stable URL, byte integrity and package extraction. Native HA tests verify unchanged
automation/event IDs, startup baselines, persistence-before-publication and
household smoke behavior. This does not establish owner-household soak results.

Hosted results belong to the associated PR's checks for its final head. Required
quality, frontend/browser and Hassfest jobs must pass before review; the private
HACS skip must remain explicit. CI stays offline with respect to NASCAR and its
distribution artifact remains a private, unpublished preview.

## Artifacts, upgrade and remaining acceptance

The bundled card is **157,418 bytes**, gzip **39,311 bytes**, within unchanged
180,000 /50,000-byte limits. SHA-256:
`3940a7481faee061209e66d0d98de31ee8cd8809ba985d735b4a16f5cce8a310`.
The local preview ZIP is **185,052 bytes**, SHA-256
`00787375c31d4679c9dd0c027ecac2daaeca5a8260b8d23bd8b99b59cbba5388`
for destination `rosslandgraf/ha-nascar-race-center` (64 files plus `SHA256SUMS`).
The [57-file runtime/license manifest](REAL_CF_ARTIFACTS.sha256) pins the complete
candidate. Each distribution also contains its own `SHA256SUMS` after approved
destination URL rewriting; fixed timestamps/order/modes produce deterministic ZIPs.
The exporter includes all integration runtime files, licenses, local branding,
both upgrade guides, self-contained data-use guidance and the artifact manifest. It includes no captured raw data,
credentials, tests, local HA storage or private development history.

Follow the [exact 0.2.0 → 0.2.1 upgrade and rollback guide](REAL_CF_UPGRADE.md).
Keep the single `/nascar_race_center/card.js` resource, whole-package pairing,
existing entry/entity/favorite identities and persisted CF eligibility. Core
restart and document reload select the new bytes. Rollback restores the whole
0.2.0 /0.6.0 pair from PR #17, not a separately copied JS file.

Remaining acceptance: owner comparison against the original full JSON files;
authorized active practice, qualifying and race observations for all three series;
actual 403 dataset coverage/permission; physical HA OS/companion migration and
household soak; permitted cadence and NASCAR data rights. Public destination,
metadata/asset approval, official unskipped HACS validation and release publication
remain separate gates. No owner HA installation, provider, data-use setting,
automation, polling permission, public visibility, tag or release was changed.
