# Handmade structural fixtures

These tiny JSON examples are authored for this project. The names, race IDs,
dates, laps, and values are fictional; they are **not NASCAR response captures**
or evidence of current anonymous access or live freshness. They contain no
images, logos, real driver records, videos, or account data.

Field spellings, flag codes, and the `series_N` envelope were checked against
the third-party client referenced by the project specification. See
[`docs/SCHEMA_EVIDENCE.md`](../../docs/SCHEMA_EVIDENCE.md) for pinned source
links and the limits of that evidence. Tests validate only this structural
contract; real endpoint schema and live-race acceptance gates remain open.

Phase 2 adds handmade driver/track examples in `drivers.json` and `tracks.json`.
Their IDs, names, teams and venue facts are fictional. The driver envelope and
field spellings come from the pinned `ooohfascinating/NascarApi` document;
numeric-string `Badge` car-number interpretation is corroborated by
`PyPlumber/Incorporator`, and exact supported series slugs by
`Harborofficial/Harbor`. Manufacturer-logo URLs are ignored, and no asset is
fetched. Multi-series directory rows test shared NASCAR identity and metadata
ambiguity, not an inferred active roster.

Schedule/session examples use the pinned `TannerYohe/nascar-api` embedded
schedule model and corroborated community `schedule-feed.json` array contract.
Known offset times, missing times, rescheduling, overlapping sessions, boundaries
and normalized canceled status cases are structural test scenarios. In
particular, synthetic status cases do not claim a verified CF cancellation
field. No naive timestamp timezone, missing duration or unpublished session is
invented. The evidence document records exact fields and pinned source links.

Phase 3A adds `live_timing.json`; its exact community references, supported
fields, defensive limits and unresolved semantics are in
[PHASE3A_LIVE.md](PHASE3A_LIVE.md). Replays mutate these fictional records;
no live field, driver directory, race result or timing capture is redistributed.
