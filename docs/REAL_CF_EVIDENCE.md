# October 22 real-CF defect evidence

This is a source contract correction after merged PRs #15, #16 and #17. Baseline
main: `986e49fa458c827e306f37ef5b7d6524e58063e9`. The owner reports successful CF
operation on HA OS 2026.10.2. No NASCAR endpoint was fetched for this work.

## Evidence actually available

The task's pasted request is available. The referenced original diagnostics,
`schedule-feed.json` and `drivers.json` are **not attached to this workspace**.
The concrete excerpts/counts in that request and the repository's earlier
[observed structural archive](nascar-api-reference/START_HERE.md) were analyzed.
This is not a claim to have independently parsed the owner's three full files.
No original response body is committed, reconstructed or redistributed.

The owner reports HTTP 200/valid JSON with Cup 41 races /111 sessions, series 2
33/91 and Trucks 25/72; all start times were unknown. The driver response reportedly
has 915 rows, 772 positive IDs with usable names, 16 zero-ID rows, and four IDs
with competing names. The earlier archive independently records 915 driver rows,
49 tracks, offset-free schedule `*_utc` strings across all three series and a
Cup detailed-only race missing from the basic race list. Those profiles establish
shared field structures, not today's active source values or permission.

## Independent published-time corroboration

Read October 22, 2026, through the web research tool, **not CF feed retrieval**:

| Primary publication | Narrow finding |
| --- | --- |
| [NASCAR Talladega weekend schedule](https://www.nascar.com/weekend-schedule/weekend-schedule-for-2026-talladega-superspeedway-chase-race/) | Truck qualifying October 23 at 12:30 p.m. ET, consistent with the owner's `start_time_utc: 2026-10-23T16:30:00` and track-local `11:30`. The page also lists Cup qualifying October 24 at 1 p.m. ET and O'Reilly qualifying at 11 a.m. ET. |
| [NASCAR qualifying-order article, October 21](https://www.nascar.com/news-media/2026/10/21/qualifying-orders-for-2026-talladega-superspeedway-chase-races/) | Independently authored prose corroborates those qualifying times and says no practice for any of the three series that weekend. No Talladega practice is invented. |
| [Homestead championship weekend schedule](https://www.homesteadmiamispeedway.com/nascar-championship-weekend-schedule/) | Lists Truck practice at 6:30 p.m., matching the supplied November 5 `23:30` UTC / `18:30` local pair after the DST change. This supports the UTC field interpretation without defining every local-time field as Eastern. |

The owner excerpt plus these publications and the earlier shared schema evidence
support a narrow UTC contract for **schedule `start_time_utc` / `end_time_utc`**.
This does not establish timezone semantics for `date_scheduled`, generic local
`start_time`, live `time_of_day_os`, or historical raw date strings. Do not
silently widen this helper to those fields.

## Timestamp conversion contract

1. Only the named schedule UTC fields accept complete offset-free ISO date/time
   strings. Assign UTC directly; never consult the HA server or track timezone.
   Seconds/fractions may be supplied; minute precision remains supported.
2. Explicit offsets, including `Z`, determine the instant and are normalized to
   aware UTC. An explicit nonzero offset is honored even in a UTC-named field.
3. Date-only, malformed/missing values and year-0001 sentinels remain unknown.
   An end at/before the start is unknown; an unknown start cannot acquire an end.
4. Generic `date_scheduled` still requires an explicit offset. A single valid
   UTC-designated **race session** may independently supply the basic race's
   start when its generic date is ambiguous. Never derive race start from practice.
5. Published detailed race sessions still supersede basic race timing. An unknown
   or ambiguous detailed race start clears an older basic start, so postponement
   cannot resurrect a stale date. A practice-only detail feed preserves a usable
   independent basic race start.
6. Session identity remains series/season/race/run-type/name based, excluding time
   and order. Time revisions reorder sessions without new IDs. Missing duration
   remains a labeled date marker in HA calendars, with its known local start in
   the description; no event length or timezone is invented.

Before/after examples (October 2026, UTC internally):

| Series | Offset-free UTC-designated input | Before | After / Eastern / Central / Pacific |
| --- | --- | --- | --- |
| Cup | `2026-10-24T17:00:00` | Unknown | `17:00Z` / 13:00 / 12:00 / 10:00 |
| O'Reilly | `2026-10-24T15:00:00` | Unknown | `15:00Z` / 11:00 / 10:00 / 08:00 |
| Trucks | `2026-10-23T16:30:00` | Unknown | `16:30Z` / 12:30 / 11:30 / 09:30 |

The Truck input is the owner's concrete excerpt. Cup/O'Reilly inputs in this
table are **synthetic shared-contract examples derived from independently
published ET times**, not inspected CF values for those series. On November 5,
`23:30Z` becomes 18:30 Eastern, 17:30 Central and 15:30 Pacific. ZoneInfo/HA/Intl
perform DST conversion; neither schedule parsing nor runtime host timezone does.

## Driver identity contract and reproduced normalization

`Nascar_Driver_ID` is the sole identity. Secondary `Driver_ID`, car number,
manufacturer and names never substitute. Missing/zero/invalid or over-20-digit
IDs cannot create a driver. Extra personal/date/media fields are ignored.

| Reported case | Handling |
| --- | --- |
| 4316: Cj McLaughlin / CJ McLaughlin | Same normalized case/whitespace spelling; one NASCAR ID with a deterministic display label. |
| 4372: Justin Carrol / Justin S Carroll | Quarantined; initials/spelling are not guessed equivalent. |
| 4234: Chad Finchum / Mike Senica | Quarantined; incompatible identities cannot share metadata. |
| 4151: Tim Viens / Timothy Viens | Quarantined; no unverified nickname alias. |

All independently valid IDs survive. Existing favorite IDs survive quarantine;
the selector offers preserved IDs with metadata-unavailable labels instead of
silently deleting them. Live timing can still use independently valid reported
NASCAR IDs without the directory. Failed directory refreshes cannot populate
selector names from retained failed metadata.

Current `nascar-oreilly-auto-parts-series` and legacy `nascar-xfinity-series` both
map to series 2. Unknown slugs preserve their reported label, without invented
series membership. Per-series published rows take priority over draft rows;
compatible partial published metadata fills gaps. Conflicting published car/team
facts stay ambiguous. Leading-zero badge strings survive; blank/numeric teams do
not become named teams, and manufacturer logo URLs do not become manufacturer
names. Draft-only directory metadata is not an active roster assertion.

The regression generator recreates **915 rows / 772 candidate IDs /16 zero IDs**
with fictional values except the four tiny reported name pairs. It yields
**769 usable IDs, three quarantined IDs**, and one merged cosmetic case. This is
a reproduced structural expectation, **not an independently verified count for
the missing original file**. The owner must compare normalization diagnostics on
the actual response after an approved update.

## Fixture provenance and scope

New `tests/test_real_cf_schedules.py`, `test_real_cf_drivers.py`,
`test_real_cf_polling.py`, `test_real_cf_history.py` and browser `real-cf.spec.ts`
use minimal handmade structures. Dates used for generic algorithm tests are
fictional; the explicitly identified Talladega/Homestead examples above have
owner/publication provenance. Existing Phase 3D-A structural fixtures remain
unchanged; their former timezone-rejection assertions now check the narrowed UTC
contract. No fixture is a runtime fallback. The native Core persistence test uses
Demonstration data and test-owned HA storage APIs, never edits `.storage` directly.

Remaining owner evidence: exact post-normalization counts for the unavailable
full files; current active practice/qualifying/race observations for all three
series; genuine session end/transition behavior and permitted source cadence.
Code permission, NASCAR data rights and public publication approval remain separate.
