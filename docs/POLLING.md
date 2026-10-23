# Live polling policy and authorization boundary

Phase 3D-B implements a 10-second-capable scheduler. Its measured performance is
synthetic; actual NASCAR feed latency, automated-access permission and permitted
cadence remain unverified. No NASCAR requests were made for this phase.

## Configuration and current CF behavior

Existing and new entries default to **Conservative**. The existing
`live_interval` setting remains 300–3600 seconds; omitted settings preserve the
300-second default and configuration version 1. **Adaptive** is an additional
options-flow choice. `approaching_interval` defaults to 60 and accepts whole
seconds from 30 through 60. Entity IDs and event preferences are unchanged.

The provider's reviewed `PollingLimits` record is independent of options.
`CF_LIMITS` deliberately disables adaptive operation and retains its 300-second
floor. Selecting Adaptive or acknowledging data use cannot change that record.
CF uses the configured conservative minimum for supported active observations
and bounded approaching/scheduled practice, qualifying and race discovery. The
default is 300 seconds; gaps to the next session within six hours also use that
target. Nearby idle discovery is hourly; genuinely complete usable schedules
without a session within seven days use six hours. Missing/ambiguous schedule
coverage falls back to one hour. A higher configured minimum, failures, server
cache or cooldown can lengthen these intervals. CF's internal fallback cache TTL remains
60 seconds; its request floor prevents an expired fallback from causing an early
network request. Standalone pits, stages and points remain unpolled.

These are conservative engineering defaults, **not NASCAR-approved rates**.
Future CF activation requires independently verified permission covering the
specific endpoints, minimum interval, scope and retention, recorded with evidence
in DATA_USE.md and reviewed with the adapter's limits. Public accessibility and a
UI toggle are insufficient. Such a change must retain the transport floor and
all upstream constraints, then run the synthetic and separately authorized live
acceptance procedures. This PR supplies no permission record or fast CF switch.

Demo declares an offline 10-second-capable policy. The normal demo still returns
an empty live feed; it does not silently replay fixtures or simulate real NASCAR
activity. Explicit synthetic test providers exercise the faster path.

## Adaptive targets for a permitted provider

| Evidence/state | Target | Sustained upper request budget, excluding one startup read |
| --- | --- | --- |
| Fresh supported active race | 10 seconds | 360/hour |
| Fresh supported active practice | 10 seconds | 360/hour |
| Fresh supported active qualifying | 10 seconds | 360/hour |
| Known upcoming session, within 30 minutes | Configured 30–60 seconds | 120–60/hour |
| Scheduled discovery window / gap to next weekend session within six hours | 5 minutes | 12/hour |
| No imminent session; next known start within seven days | 1 hour | 1/hour |
| Overnight gap greater than six hours | 1 hour | 1/hour |
| Complete usable schedules without a session within seven days | 6 hours | 4/day |
| Missing/stale/failed schedules or unknown relevant start times | Conservative 1 hour | 1/hour |

The fastest applicable selected series wins. A published start is discovery
evidence only. At the scheduled start the approaching window becomes a bounded
five-minute discovery policy, never an active-session assertion. A supplied end
limits that window (at most eight hours); without an end, discovery lasts only
30 minutes, followed by hourly conservative checks within an eight-hour trailing
window. This does not fabricate a duration or calendar end. Canceled and
completed normalized schedule rows are excluded. Schedule `start_time_utc` / `end_time_utc` now have a narrow, corroborated UTC
contract; other ambiguous offset-free timestamps remain unknown. HA timezone
conversion happens after UTC normalization. No fixed NASCAR season dates or
track timezone are guessed. See [timestamp evidence](REAL_CF_EVIDENCE.md).

Only fresh selected-series observations with positive race/run identities and
recognized session kinds establish adaptive activity. A race additionally needs
an existing supported racing flag and positive reported lap. Practice and
qualifying instead need a reported `is_on_track=True` competitor; zero/unknown
lap counts and absent race flags are supported. Checkered/cold-track evidence
precludes activity. These use existing normalized fields, not new CF fields or
new status-code interpretations. Source timestamps in the future cannot establish
adaptive activity. Real active-session semantics still require validation.

Clock regression prevents fast polling, including across run/race/series changes.
A clock that stays at least 60 seconds behind now causes a minimum five-minute
interval, increasing to ten, twenty and sixty minutes on repeated reads. An
advancing current source recovers automatically. Provider failures have bounded
exponential backoff; Retry-After and transport cooldowns take precedence. A
transient outage of a previously reported adaptive session retries conservatively
instead of immediately waiting six hours. No missing interval is reconstructed.

## Scheduling, cache and restart ownership

One existing HA `LiveCoordinator` owns global live polling, independent of series,
favorite, entity, diagnostic and event-listener counts. No second live loop was
added. The existing HA refresh lock and shared client's request lock prevent
overlap. A schedule listener re-arms that same coordinator after revisions; a
deadline at the next approach boundary avoids sleeping past it. Source expiry
still updates availability locally without an HTTP request. Unload and failed or
cancelled setup remove the listener and timers.

The transport enforces one network attempt per eligible slot, even for concurrent
refreshes and no-cache/no-store responses. A body whose internal fallback expired can be reused during the local request
floor without changing its source time. An expired explicit upstream freshness
lifetime or a no-cache revalidation requirement instead defers the read until
both revalidation and the request floor can be satisfied. Without a reusable
body, the read is also explicitly deferred. No-store bodies/validators are not cached.
Only an authorized shorter provider minimum can reduce the fallback TTL below
60; explicit upstream freshness always wins. ETag/Last-Modified, 304,
Cache-Control, Expires, Date and Age are respected. A 304 merges response metadata
without retaining the old response's Age/Date or changing the content clock.
Upstream lifetimes longer than one day are not shortened to an internal cap.
An extreme delay can cause an earlier bounded local timer wake, which still
cannot request a fresh upstream response before eligibility.

403 and other failures honor Retry-After; 429 pauses the shared CF host. Successful
200/304 responses with Retry-After also delay subsequent network access. Invalid
JSON and oversize responses now receive transport backoff as well. There are no
in-call retries. Source freshness never comes from HTTP success or revalidation.

CF's bounded in-memory client/cache/cooldowns survive entry reloads, avoiding
reload-induced requests and preserving usable observations. Removing the entry
releases that cache. Across an HA process restart, only a compact HA Store record
survives: next live-request eligibility and an optional host-wide 429 deadline.
The request slot is reserved and its write verified **before** I/O. Cancellation
retains the reservation; corruption or storage failure blocks live requests.
Host cooldowns also prevent schedule/reference requests after a restart. No raw
body, validator, credential, field history or race observation is persisted here.
After a real restart with an outstanding slot and no body, live entities may stay
unavailable until a permitted read; schedules remain independent except during a
host-wide rate limit. Clearing storage, restoring an older backup or separate HA
instances are outside this single-installation reservation guarantee.

## Diagnostics and consumer compatibility

`live.polling` reports configured and provider policies, fast permission,
configured conservative minimum, approach setting, selected target, effective
interval, reason, limiting constraint, content age, failure/nonadvancement counts
and time until network eligibility. `cf_pipeline.transport[path]` adds latest
attempt and successful JSON/304 response timestamps alongside existing delivery
(`network`, `cache`, `revalidated`, `cooldown`, `cancelled`), HTTP/JSON outcomes and
response-header receipt time. These describe transport, not origin verification
or source freshness. Existing source time/health diagnostics remain separate.

Sensors consume the same normalized models promptly. No sensor or event consumer
makes a request. No new entity attributes, history samples or event types are
introduced. Phase 3C race-only meanings, deduplication, silent restart/switch
baselines and persistence-before-publication remain intact. Faster practice
polling does not create practice automation events or change session-progress
sensor semantics. The full field remains in bounded runtime memory.

See [executed validation and measured budgets](PHASE3DB_VALIDATION.md).

## Historical CF-readiness correction (0.1.2)

Conservative CF now recognizes fresh on-track practice/qualifying at zero race
laps and uses the existing configured conservative minimum (300 seconds by
default). Empty/cold/withheld/regressed CF timing does not choose the activity
branch. First reported activity may select that interval while its display says
activity-unconfirmed; a cache read does not change the activity assessment.
No CF adaptive activation or floor reduction is included. At 0.1.2, between/completed
sessions still used race-based 900/3,600/21,600-second discovery, not the permitted
synthetic provider's faster approach/gap targets. Unknown schedule times could
therefore mean six-hour discovery; 0.2.1 supersedes that behavior. The [exact targets and remaining limits](CF_READINESS_VALIDATION.md#polling-and-resource-decisions)
and [owner acceptance procedure](CF_OWNER_ACCEPTANCE.md) document that earlier behavior rather than a promise
that CF refreshes every five minutes in every state.


## Real-CF schedule correction (0.2.1)

Conservative CF shares the existing bounded session-window calculation across
all selected series, clamped to its configured minimum and the unchanged
300-second provider floor. It never enables 10-second adaptive CF polling.
Practice and qualifying can be discovered before the race; an unknown schedule
is not evidence of an off-season. A scheduled window is only discovery evidence.

If retained/regressed timing would otherwise increase nonadvancement backoff to
one hour, **known approaching/scheduled windows** cap that particular delay at
900 seconds. This permits discovering a replacement run while retained content
stays withheld. Failure backoff, configured higher minimums, server freshness,
Retry-After, cooldowns and persisted network eligibility still take precedence.
Outside those windows, existing 300/600/1,200/3,600-second nonadvancement backoff
remains intact. No additional coordinator, per-card request or standalone detail
poller is introduced. [Current decisions and executed validation](REAL_CF_VALIDATION.md)
separate target intervals from actual network eligibility.
