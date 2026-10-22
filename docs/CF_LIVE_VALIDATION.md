# Authorized end-to-end CF validation on Home Assistant OS

For the **0.1.2 / 0.5.3** candidate on the owner's existing installation, use
[the current update and before/during/after acceptance procedure](CF_OWNER_ACCEPTANCE.md)
and [readiness evidence](CF_READINESS_VALIDATION.md). The older generic procedure
below is retained as historical guidance; no source or hardware test is claimed.

This is a future operator procedure. It has **not** been executed against NASCAR
or the owner's HA OS system. Development permission and a passing PR do not grant
NASCAR polling permission or permission to install on production.

1. Confirm NASCAR data-use/polling authorization and an approved testing window
   for the existing request cadence. Confirm that the test HA OS network permits
   `https://cf.nascar.com` through its normal configuration. Stop if denied;
   keep TLS verification and normal proxies. Do not use alternate hosts/IPs,
   credentials, cookies, Drive or restricted Swagger access. Record the permission
   scope privately. The integration's acknowledgement is a user assertion.
2. On an owner-approved **test** HA OS instance, take a backup and record HA Core,
   OS/Supervisor versions and the reviewed PR commit. Use the existing development
   installation process: copy only `custom_components/nascar_race_center` into
   `/config/custom_components/`, then restart HA. Do this only after installation
   is separately approved; this assignment performs no deployment. No `work/`,
   fixtures, `.storage` or prepared cloud activation script belongs on HA OS.
3. First select **Demonstration** in Settings → Devices & services → NASCAR Race
   Center. Check fictional schedule/favorite metadata and clean reload. This mode
   needs no NASCAR access and has no live race. Leave racing events and user
   blueprints disabled for this provider test. Do not create new automations.
4. Switch the entry to **NASCAR CF**, acknowledge data-use authorization only if
   established, select the series to observe and a permitted real NASCAR driver
   ID. Review favorites after leaving demo; its fictional IDs are not real drivers.
   Keep polling options unchanged. Setup starts ordinary provider requests.
5. Download diagnostics from the integration entry after setup. Check the four
   layers below, and compare reported IDs to the independently known session
   being tested. Use scheduled refreshes; do not loop reloads or force updates to
   obtain faster observations. On 429/503, stop manual testing and respect
   Retry-After/backoff. Do not clear caches or reload to evade cooldowns.
6. During the approved window, download a second diagnostic sample after a normal
   refresh. Compare source time and IDs, not just local response time. Check a
   selected favorite's position and current stage against the known reported
   session. The other series must say `not_reported` if the global feed describes
   only one series. Missing/stale/unknown data may legitimately remain unavailable.
7. At the end, switch back to demo or disable the test entry to stop CF polling.
   Confirm clean reload/unload and preserved entity IDs/favorites. Store only
   approved minimal evidence privately; review diagnostic files before sharing.
   Do not commit full bodies, credentials, local HA storage or provider datasets.

## Read the four layers

| Question | Diagnostic evidence / expected interpretation |
| --- | --- |
| Did a request obtain a response? | `cf_pipeline.transport[path].delivery`, `transport`, `http_status`, `response_at`. `connection_error` with null status is a network failure, not a NASCAR HTTP denial. A response status can come from an intermediary. `cache`/`cooldown` means no new request for this read; `revalidated` means 304 reused a prior body. |
| Was the body valid JSON? | `json_status=valid`, separate from HTTP success. `invalid` or `too_large` explains body failure. `not_checked` covers denied/error responses and attempts that supplied no eligible body. JSON `null` follows the existing no-session contract; it is not proof of an active session. |
| Did the expected data parse? | `cf_pipeline.parsers`: `basic:YEAR:SERIES`, `sessions:YEAR:SERIES` and `/live/feeds/live-feed.json`. Require `parsed`, then inspect `live.series_id`, `race_id`, `run_id` against the intended session. `context_conflict` rejected contradictory optional schedule track IDs. `reference.failed_feeds` and counts identify reference parsing/read failures. |
| Did HA receive usable data? | Check per-series `series_health`, `usable_timing`, source clock/staleness, optional timing/pit/stage failures, schedule race/session/unknown-time counts and actual entity availability. `retained_last_good=true` is diagnostic context after failure. Known freshness and the correct selected series are required for live timing; a successful HTTP response alone is insufficient. |

Offset-free schedule strings, even `*_utc`, currently produce unknown starts;
next-race/calendar entries can be absent while race counts and names succeed.
Do not patch in a timezone just to populate the calendar. Obtain a documented
provider contract before changing that policy. Numeric `time_of_day` is not a
substitute source timestamp. Unknown codes remain available numerically without
new status meanings. Standalone pits/stages/points should remain
`unsupported_association` and should cause no automatic GETs.

## Minimal result record

Record the reviewed commit; HA Core/OS/Supervisor versions; approved permission
scope/window; UTC observation times; selected series/favorite NASCAR IDs;
reported series/race/run IDs; per-endpoint delivery/HTTP/JSON/parser outcomes;
source clock progression; usable/unavailable entity examples; request counts if
available through approved monitoring; and reload/unload result. Distinguish
success, schema failure, transport restriction and unavailable source facts.
A valid JSON response for another race/session is not acceptance.

Close the **connection** gate only with an actual permitted response; the
**active-session** gate additionally needs known session identity and source
progression. Timezone/status/unit meanings, event transitions, off-season
behavior and standalone associations require their own authorized evidence.
Never infer data/polling/redistribution rights from technical success.

If a raw sample is separately approved and necessary, follow the selective
[manual reference workflow](api/README.md) on an authorized normal client and
retain it privately under ignored `work/`. That is an additional request requiring
its own scope; no capture or probe is necessary to follow the diagnostic procedure.
