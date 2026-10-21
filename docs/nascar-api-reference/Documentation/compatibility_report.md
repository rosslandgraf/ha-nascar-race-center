# Phase compatibility

The brief defines PR 1–6 and feature groups but does not define Phase 3A, 3B or 3C. The mappings below are provisional capability groupings, not a claim about the repository roadmap. Confirm phase definitions in the development project.

| Phase | Provisional scope | Useful verified endpoint IDs | Evidence and remaining gates |
|---|---|---|---|
| 1 | Foundation, schedule, basic status/flags | 01,02,06,08–12 | Structures captured; timestamps and code semantics need contract validation. Data rights unresolved. |
| 2 | Multi-series schedules/calendars, driver selection | 06–12 | Three series schedules and reference namespaces observed; UTC strings lack explicit offset, seasonal rollover and rescheduling behavior untested. |
| 3A | Live leaderboard and lifecycle | 01–02,21 | Positions, lap metrics, stage context and flags observed; no active-session replay or concurrent-series validation; global-feed context inconsistent. |
| 3B | Pits, stage points, championship movement/events | 03–05,18–19,22–23 | Structures usable as parser references; stage/global race mismatch, points zero IDs and context-free pit rows prevent safe automatic joins. Event transitions and official scoring remain unverified. |
| 3C | Historical analytics and comparisons | 13–17,19,24 | Historical results/laps/loop statistics/averages verified structurally; numeric strings, sentinels and session namespaces need normalization. Derived metrics need validation. |

Driver recap 25 provides no populated recap schema. SnappyTV 20 is optional metadata only. Drive 26–28 is access-controlled and outside core scope. No phase is declared release-ready from one snapshot. This package does not validate Home Assistant runtime behavior or HACS checks.
