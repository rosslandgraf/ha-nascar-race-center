# Endpoint compatibility and evidence

**Current evidence (October 21, 2026):** all 28 original URLs were attempted by
anonymous HTTPS GET. Every request received proxy CONNECT 403, before a NASCAR
origin response. Origin HTTP statuses and response types remain unknown; zero
real JSON bodies were obtained. This does not establish NASCAR/Cloudflare denial
or universal inaccessibility. See the permanent
[endpoint catalog](api/ENDPOINT_CATALOG.md), [per-request evidence](api/probes/2026-10-21.json),
[schema reference](api/SCHEMA_REFERENCE.md) and [audit](api/AUDIT_REPORT.md).
The older direct-verification entries below mean origin/schema validation is
still unverified; the new catalog records each attempted request in detail.

The primary provider is `https://cf.nascar.com`. The owner's browser inventory dated **2026-10-20** reports 24 working URLs and four Error/Login results. Those reports are preserved below. They do not establish anonymous access, permission, JSON shape, freshness, or availability for another season/session.

No direct CF requests were made during Phase 1, Phase 2 or Phase 3A development: the managed environment's destination policy does not include `cf.nascar.com`. Tests use synthetic structural fixtures. Third-party source references, where available, support parser hypotheses; they do not independently verify today's CF service. The owner's Phase 2 confirmation of the seven schedule/reference URLs does not alter this distinction. See [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md) for parser-specific provenance and limitations.

In the table, **owner: working** and **owner: Error/Login** are owner reports, not automated verification. **Unverified** means no direct anonymous endpoint/schema/live-race check has run in this task. CI never polls CF.

| Category | Exact owner-tested URL | Owner report | Direct verification | Phase |
| --- | --- | --- | --- | --- |
| Live | https://cf.nascar.com/live/feeds/live-feed.json | Working | Unverified | Experimental session-context and Phase 3A timing adapter |
| Live | https://cf.nascar.com/live/feeds/live-flag-data.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-pit-data.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-points.json | Working | Unverified | Phase 3 |
| Live | https://cf.nascar.com/live/feeds/live-stage-points.json | Working | Unverified | Phase 3 |
| Schedule/reference | https://cf.nascar.com/cacher/2026/race_list_basic.json | Working | Unverified | Experimental adapter; embedded sessions supported in Phase 2 |
| Schedule/reference | https://cf.nascar.com/cacher/drivers.json | Working | Unverified | Experimental Phase 2 reference adapter |
| Schedule/reference | https://cf.nascar.com/cacher/tracks.json | Working | Unverified | Experimental Phase 2 reference adapter |
| Schedule/reference | https://cf.nascar.com/cacher/2026/1/schedule-feed.json | Working | Unverified | Experimental Phase 2 session enrichment |
| Schedule/reference | https://cf.nascar.com/cacher/2026/2/schedule-feed.json | Working | Unverified | Experimental Phase 2 session enrichment |
| Schedule/reference | https://cf.nascar.com/cacher/2026/3/schedule-feed.json | Working | Unverified | Experimental Phase 2 session enrichment |
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

The focused final Phase 2 review reread pinned community schemas through GitHub;
it made no NASCAR requests and left every direct-verification status above
unchanged. In particular, the referenced schedule consumer accepts offset-free
UTC-named times that this integration deliberately leaves unknown. See the
final contract review in [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md) for population
risks, mandatory envelopes and optional-field behavior.

Only URL patterns backed by parser evidence and fixtures may enter the provider catalog. Generalizing an owner-tested 2026/series-1 URL to another year/series remains a compatibility hypothesis until verified; unsupported responses must fail safely. Tests of mocked response parsing are not endpoint compatibility tests.

The CF provider uses the global season schedule `/cacher/{year}/race_list_basic.json`, optional `/cacher/{year}/{series}/schedule-feed.json` enrichment, independent `/cacher/drivers.json` and `/cacher/tracks.json` references, and the existing `/live/feeds/live-feed.json`. It does not enable the other listed endpoints. The basic schedule envelope is filtered by selected series in memory and cached across calls, avoiding a global-list request per series. Session feeds are fetched only for selected series/seasons. The next season remains optional until published. January also checks the prior season to discover cross-year weekends after a restart, retaining only events with known remaining times and continuing their refresh while needed.

Race/embedded-session fields and live enum parsing use [TannerYohe/nascar-api at 3ab85bb](https://github.com/TannerYohe/nascar-api/tree/3ab85bb543528d76521417b5534a6eedb09dcdf3). Detailed sessions and reference directories use the other pinned community sources in [SCHEMA_EVIDENCE.md](SCHEMA_EVIDENCE.md). These are third-party schema evidence backed by synthetic fixture tests, not independent current provider verification. No current CF status, cancellation flag, authoritative session ID or naive timestamp timezone is established.

Schedule polling remains on the six-hour coordinator cadence. In the absence of server cache directives, fallback response lifetimes are one hour for the basic global list, six hours for detailed session feeds, and 24 hours for driver/track references. References use a separate daily coordinator. ETag/Last-Modified, server cache directives, conditional requests and per-endpoint backoff retain their existing semantics.

The shared CF transport uses a 16-entry LRU response cache (the usual two-season, three-series request set plus references/live uses eleven endpoints), a 2 MiB response limit, and failure/cooldown bookkeeping each bounded to 24 endpoints. Negative cooldowns include access denial and missing feeds, so a failed shared global list is not requested repeatedly for every selected series in one refresh. A 429 pauses the host; other endpoint failures remain isolated. All consumers use Home Assistant's managed aiohttp session. A failed optional reference/enrichment endpoint cannot invalidate a usable independent schedule. Failed-season rows retained for diagnostics do not provide calendar events or next-race selections. A successful HTTP refresh remains a transport observation, not proof that provider content is current.

Before an authorized direct check, record the date, exact URL, ordinary anonymous client (no cookies or NASCAR authorization headers), HTTP result, minimal structural field notes, and applicable permission assumptions. Preserve no credentials or raw restricted assets. A successful historical response does not establish current live behavior, and a fresh HTTP response does not prove fresh timing data.

Excluded endpoints are not fallback login paths. The integration must not use the credential-protected `feed.nascar.com` Swagger service, NASCAR Drive token discovery, or a video proxy. SnappyTV metadata does not establish rights to stream or redistribute media.

## Phase 3A evidence update

The pinned community live model/document were reread before implementation;
[the live structural contract](../tests/fixtures/PHASE3A_LIVE.md) records the
additional fields and semantics that remain unknown. Global `live-feed.json`
now also normalizes `vehicles` and reported run/lap context. The adapter makes
no additional endpoint requests and never queries alternate series live paths
for concurrent coverage. Live pit/stage/points/flag-history URLs remain unused.
No CF URL was probed: network policy excludes the host, and data-use gates remain
unresolved. Every direct-verification status in this matrix remains unchanged.
