# Endpoint compatibility and evidence

The primary provider is `https://cf.nascar.com`. The owner's browser inventory dated **2026-10-20** reports 24 working URLs and four Error/Login results. Those reports are preserved below. They do not establish anonymous access, permission, JSON shape, freshness, or availability for another season/session.

No direct CF requests were made during Phase 1 development: the managed environment's destination policy does not include `cf.nascar.com`. Tests use synthetic structural fixtures. Third-party source references, where available, support parser hypotheses; they do not independently verify today's CF service. See [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md) for parser-specific provenance and limitations.

In the table, **owner: working** and **owner: Error/Login** are owner reports, not automated verification. **Unverified** means no direct anonymous endpoint/schema/live-race check has run in this task. CI never polls CF.

| Category | Exact owner-tested URL | Owner report | Direct verification | Phase |
| --- | --- | --- | --- | --- |
| Live | https://cf.nascar.com/live/feeds/live-feed.json | Working | Unverified | Experimental Phase 1 adapter |
| Live | https://cf.nascar.com/live/feeds/live-flag-data.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-pit-data.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-points.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-stage-points.json | Working | Unverified | Phase 3 |
| Schedule/reference | https://cf.nascar.com/cacher/2026/race_list_basic.json | Working | Unverified | Experimental Phase 1 adapter |
| Schedule/reference | https://cf.nascar.com/cacher/drivers.json | Working | Unverified | Phase 2 |
| Schedule/reference | https://cf.nascar.com/cacher/tracks.json | Working | Unverified | Phase 2 |
| Schedule/reference | https://cf.nascar.com/cacher/2026/1/schedule-feed.json | Working | Unverified | Phase 2 session enrichment |
| Schedule/reference | https://cf.nascar.com/cacher/2026/2/schedule-feed.json | Working | Unverified | Phase 2 session enrichment |
| Schedule/reference | https://cf.nascar.com/cacher/2026/3/schedule-feed.json | Working | Unverified | Phase 2 session enrichment |
| Schedule/reference | https://cf.nascar.com/cacher/2026/1/race_list_basic.json | Working | Unverified | Reference only; adapter uses global schedule |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/weekend-feed.json | Working | Unverified | Phase 4 |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/lap-times.json | Working | Unverified | Phase 4 |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/lap-notes.json | Working | Unverified | Phase 4 |
| Historical/statistical | https://cf.nascar.com/loopstats/prod/2024/1/5392.json | Working | Unverified | Phase 4 |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/lap-averages.json | Working | Unverified | Phase 4 |
| Historical/statistical | https://cf.nascar.com/cacher/2026/1/5626/live-pit-data.json | Working | Unverified | Phase 3/4 |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/live-stage-points.json | Working | Unverified | Phase 3/4 |
| Historical/statistical | https://cf.nascar.com/cacher/2024/1/5392/snappytv.json | Working | Unverified | Metadata only; no playback implementation |
| Legacy/race-specific | https://cf.nascar.com/live/feeds/series_1/5170/live_feed.json | Working | Unverified | Reference only; no current-session guarantee |
| Legacy/race-specific | https://cf.nascar.com/live/feeds/series_1/5170/live_points.json | Working | Unverified | Reference only |
| Legacy/race-specific | https://cf.nascar.com/cacher/live/series_1/5170/live-pit-data.json | Working | Unverified | Reference only |
| Legacy/race-specific | https://cf.nascar.com/cacher/2019/2/4817/lapAvg_nxs_practice_1.json | Working | Unverified | Phase 4 legacy reference |
| Excluded | https://cf.nascar.com/cacher/2024/1/5392/driver-recap.json | Error/Login | Unverified | Excluded from core |
| Excluded | https://cf.nascar.com/drive/1/configs-ng.json | Error/Login | Unverified | Excluded |
| Excluded | https://cf.nascar.com/drive/2/configs-ng.json | Error/Login | Unverified | Excluded |
| Excluded | https://cf.nascar.com/drive/3/configs-ng.json | Error/Login | Unverified | Excluded |

## Interpretation and future verification

Only URL patterns backed by parser evidence and fixtures may enter the provider catalog. Generalizing an owner-tested 2026/series-1 URL to another year/series remains a compatibility hypothesis until verified; unsupported responses must fail safely. Tests of mocked response parsing are not endpoint compatibility tests.

The Phase 1 CF adapter requests only the global season schedule `/cacher/{year}/race_list_basic.json` and `/live/feeds/live-feed.json`. The schedule envelope is filtered by selected series in memory and cached across calls, avoiding a request per series. Schedule field and live enum parsing are based on the Python models in [TannerYohe/nascar-api at 3ab85bb](https://github.com/TannerYohe/nascar-api/tree/3ab85bb543528d76521417b5534a6eedb09dcdf3) and the references detailed in [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md), with synthetic fixtures; they remain third-party schema evidence rather than current provider verification.

Before an authorized direct check, record the date, exact URL, ordinary anonymous client (no cookies or NASCAR authorization headers), HTTP result, minimal structural field notes, and applicable permission assumptions. Preserve no credentials or raw restricted assets. A successful historical response does not establish current live behavior, and a fresh HTTP response does not prove fresh timing data.

Excluded endpoints are not fallback login paths. The integration must not use the credential-protected `feed.nascar.com` Swagger service, NASCAR Drive token discovery, or a video proxy. SnappyTV metadata does not establish rights to stream or redistribute media.
