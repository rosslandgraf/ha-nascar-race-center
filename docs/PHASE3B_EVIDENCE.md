# Phase 3B evidence and conservative interpretation

Primary evidence is the imported [observed package](nascar-api-reference/START_HERE.md),
particularly endpoint profiles 01/03/04/05/18/19, the field dictionary and
[verified relationships](nascar-api-reference/Documentation/verified_relationships.json).
It contains redacted structures, not replay fixtures or scoring specifications.
This assignment authorizes evidence-limited implementation; active-session and
permission gates remain open. No NASCAR requests are needed for development.

| Capability | Supported facts | Boundary / blocker |
| --- | --- | --- |
| Embedded pits (01) | Parent NASCAR driver ID, entry lap/leader lap, reported entry/exit clocks, in/out ranks, signed `positions_gained_lossed` | Parent race/run and source freshness gate every value. No verified clock units, elapsed subtraction, completed-stop count, on-pit-road status or tire activity. Zero/negative physical clocks stay unknown. |
| Standalone pits (03/18) | Car/name, laps, reported clocks/durations, tire-change Booleans, type, ranks and signed movement | Global feed has no race/run/series/driver IDs or source clock. Never join by name/car or receipt time. Archived path context is historical provenance, not live identity. |
| Embedded stage (01) | `stage_num`, `finish_at_lap`, `laps_in_stage` | No `current - 1` completed-stage calculation; no finish inferred from lap crossing. |
| Stage results (05/19) | Reported stage number and NASCAR-ID results/position/stage points | Global observed race 5168 differs from leaderboard 5633. Missing series/source clock and unverified cross-feed run namespace prevent attachment even if numeric race/run IDs happen to match. Results presence is not official finality. |
| Championship points (04/22) | NASCAR driver ID, reported position/points/race points, bonuses, stage scores/flags and raw delta fields | Observed context IDs are zero. Never replace with active IDs, join on membership ID, calculate totals, infer delta units or rank changes, or promote checkered data to official results. |

All standalone datasets remain separate. Normalized provenance distinguishes
source identity, source content time and local retrieval time. Context validation
rejects conflicts, unknown identifiers, namespace differences, stale/unknown
source times and nonrace sessions. A shared optional-feed coordinator isolates
failures, retains last-good data only for diagnostics, and replaces whole
successful datasets rather than merging rows across polls. It makes at most one
request per global feed per slow refresh, independent of favorites/series count;
no historical probes or fallback URL searches. Existing transport handles cache
validators, bounded bodies/caches, negative cooldowns and host-wide 429 pauses.
No faster polling permission is implied.

Handmade synthetic fixtures and replay tests will exercise the normalized trusted
provider boundary as well as the real CF parser restrictions. Synthetic provider
context/freshness is never backfilled into CF data and is not evidence of an
actual NASCAR scoring formula, official result, allowed cadence or live behavior.
