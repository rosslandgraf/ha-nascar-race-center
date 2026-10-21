# NASCAR Race Center

A Home Assistant custom integration for NASCAR's three national series, with season schedules, native calendars, experimental live timing and favorite-driver tracking. **Phase 3B remains private development, with live source validation and release gates outstanding.** The default offline demonstration works without NASCAR access. An experimental CF adapter is available only after explicit data-use authorization.

The long-term target includes race-weekend schedules, timing/scoring, favorite drivers, championship points, historical analytics, automations and an optional responsive dashboard. See the complete [specification](NASCAR_Race_Center_Codex_Brief.md) and [phased roadmap](ROADMAP.md).

Development reference: [API library](docs/api/README.md),
[all 28 endpoints](docs/api/ENDPOINT_CATALOG.md),
[field dictionary and evidence limits](docs/api/SCHEMA_REFERENCE.md), and
[October 21 API audit](docs/api/AUDIT_REPORT.md). All 28 fresh attempts were
blocked at proxy CONNECT, before any NASCAR response. The separately supplied [observed package](docs/nascar-api-reference/START_HERE.md)
corroborates structures but exposes conflicting contexts; active-session behavior
and permission remain unverified. See [Phase 3B evidence](docs/PHASE3B_EVIDENCE.md).

## Available features

- UI configuration and options for one integration entry, selected national series (IDs 1, 2 and 3), and multiple favorite drivers.
- Normalized season races, weekend sessions, drivers and tracks; optional practice/qualifying/race schedule enrichment where supplied.
- A native Home Assistant calendar per selected series, with documented fallbacks for unknown duration.
- Favorite-driver metadata identified by NASCAR driver ID, preserving identity across name, car-number, team and series changes.
- Demonstration provider, experimental CF adapter, asynchronous shared-session HTTP/cache/error boundaries, and independent schedule, reference and live updates.
- Existing next-race, schedule, session-type, flag and current-lap entities, plus freshness/provider diagnostics.
- Typed live field with driver-ID lookup, reported positions, gaps, last/best laps, source speed fields, laps completed and laps-led intervals.
- Race leader, reported lap totals/remaining laps and evidence-limited session progress; favorite-driver live sensors independent of the reference directory.
- Mocked provider and Home Assistant lifecycle tests, Ruff/mypy checks, Hassfest and HACS validation workflows.

Phase 3B adds embedded pit/current-stage observations and conservative standalone scoring adapters; live association of standalone feeds remains blocked where identity/freshness is unproven. Automation events, history/analytics and custom cards remain future phases. The normalized leaderboard is available to integration consumers in memory; a user-facing full-field dashboard/data endpoint is a later deliverable. The [validation report](docs/VALIDATION.md) records precisely which checks ran; configured CI is not a claim that every check passed. Real CF response schemas, cancellation/status fields and timestamp semantics remain unverified; [schema evidence](docs/SCHEMA_EVIDENCE.md) distinguishes community references from current service validation.

## Development installation

Use an isolated development Home Assistant 2026.10.2 instance with Python 3.14. Copy only `custom_components/nascar_race_center` into that instance's `config/custom_components/` directory and restart it. In **Settings → Devices & services → Add integration**, choose **NASCAR Race Center**, leave the source set to **Demonstration**, and select the series to monitor. No YAML or NASCAR credentials are required.

Demonstration names and observations are synthetic and must not be used as actual race information. Use the integration's **Configure** action to change the source, selected series or favorites; the entry reloads to apply changes. CF mode should only be selected when the intended access is authorized, with the acknowledgement enabled. It may fail on access restrictions or unverified schema changes. The integration never asks for NASCAR employee credentials.

Remove the entry from **Settings → Devices & services** to unload entities and polling. To remove the integration files completely, delete `config/custom_components/nascar_race_center` in the development instance and restart. This task does not install anything on the owner's production Home Assistant.

## Data availability and permissions

The [endpoint matrix](docs/ENDPOINTS.md) preserves the owner's 24 successful and four failed browser reports. Those reports are not independent anonymous-access, schema or live-race verification. This environment's network policy excludes the CF host, so development and CI use structural mocks. Live session freshness, anonymous access and data-use permissions remain unverified.

The existing [MIT license](LICENSE) applies to project code; NASCAR data and media rights are separate and unresolved. Read the [data-use note](docs/DATA_USE.md) before enabling CF access. No NASCAR-controlled logos, photos, video or full feed captures are distributed. No public release or production deployment is authorized by this development task.

## HACS status

The repository uses a HACS-compatible integration layout and includes `hacs.json` and validation workflows. It is not yet release-ready or approved for the HACS default catalog. The official HACS action rejects private repositories, so its job is conditional on public visibility and is skipped during private development. When available, it temporarily skips the brands check while authorized branding is pending. Full HACS validation, branding and all permission/release gates must be resolved before public distribution. The optional frontend card will be packaged separately in a later phase.

## Development

Use the already prepared environment; do not repeat onboarding. See [CONTRIBUTING.md](CONTRIBUTING.md) for restoration and exact validation commands, [AGENTS.md](AGENTS.md) for permanent development rules, and [ARCHITECTURE.md](ARCHITECTURE.md) for provider, model and coordinator boundaries.

The [observed NASCAR API reference package](docs/nascar-api-reference/START_HERE.md) documents 28 captured endpoint attempts. Read the [repository assessment](docs/NASCAR_API_REFERENCE_ASSESSMENT.md) for agreement with main and the separate Phase 3A PR, unresolved semantics and merge considerations. Its redacted structural samples are documentation, not response fixtures or production fallback data; captured observations do not establish current live-session behavior.

## Calendars and schedule times

CF schedule dates require an explicit `Z` or numeric timezone offset. A date such as `2026-11-01T12:30:00` or `2026-11-01` has no verified timezone semantics and stays **unknown**; the integration never assumes UTC, Eastern time, the track timezone, or Home Assistant's timezone. Such races remain in the schedule count but are excluded from next-race selection and race-window polling. If every start is unknown, both next-race entities are unknown; with mixed data, they show the next race **among starts with verified offsets**, which may omit an earlier undated race. Check `unknown_start_times` on the scheduled-races sensor or `schedule.unknown_start_time_counts` and `timestamp_policy` in downloaded diagnostics. Real CF start times remain a validation limitation until source timezone semantics are evidenced; see [schema evidence](docs/SCHEMA_EVIDENCE.md).

Open Home Assistant's **Calendar** view and select the NASCAR series calendars. Timed sessions require valid start/end values with explicit timezone offsets and a later end; Home Assistant displays them in the configured local timezone. A session with a known start but no reliable end is represented as a clearly labeled all-day notice, with its known start in the description. This avoids inventing practice or race duration. Sessions without a usable start are omitted. Weekend entries describe the local calendar dates covered by known sessions; they are date-range summaries, not claims that racing runs continuously. Canceled events are omitted when a normalized provider identifies them. No current CF cancellation/status field has been verified, so source cancellation detection remains limited.

Schedule changes update the same internal event identity when race/session names and IDs remain stable. Dates and list order do not determine session identity. A source rename can change a derived session ID because the documented feed shapes do not expose an authoritative session ID. Detailed race-session times take precedence: a detailed unknown/TBD start clears an older basic-list time rather than presenting it as confirmed.

The current season is refreshed throughout the year, with optional next-season requests in November/December. January also checks the previous season after a restart, retaining known future/ongoing cross-year weekends and continuing their refresh while needed. An unpublished future schedule does not discard a usable current schedule. Failed-season rows remain diagnostic context but are excluded from next-race selection, calendar events and normal schedule counts; a usable independent season can remain available.

## Favorite drivers and reference metadata

Choose up to 50 favorites through **Configure** at any time. The selector supports multiple choices and search; cached directory labels include the driver name, NASCAR ID and available series/car/team details. Initial setup accepts optional numeric IDs, with named directory choices available after setup. Forms never fetch CF data. If the directory is unavailable or has not loaded yet, enter a positive numeric NASCAR driver ID; selected IDs remain editable even when their directory records are missing. Favorites can span all three national series independently of the series being monitored.

Demonstration options are explicitly marked **Demo** and use fictional driver IDs. Switching data sources preserves selected IDs without matching by name or car number; review favorites when moving from demonstration to CF mode, because a fictional ID does not identify a real NASCAR driver.

Each selected driver gets one metadata sensor, whose state is the known driver name and whose compact attributes include the NASCAR ID, reported series associations and available car number, team and manufacturer. Up to three `series_metadata` records preserve unambiguous series-specific car/team/manufacturer facts. Live observations use their own sensors, described below. Opt-in pit and scoring summaries are described below. Multiple series records share one driver identity; ambiguous car/team details are not flattened into a guessed current value. The general directory does not prove an active entry or current roster. Source manufacturer-logo URLs are ignored.

Adding/removing favorites reloads the entry. Existing favorites retain their unique IDs across reference changes and series changes. A missing, failed or more-than-seven-days-old driver reference makes its metadata sensor unavailable while preserving the selection. Track reference metadata enriches calendar descriptions when available; losing the track feed leaves schedule-supplied track names usable. References refresh daily, independently of the six-hour schedule refresh, so a driver or track outage does not disable race calendars. These intervals describe the integration's conservative policy, not an independently approved NASCAR polling allowance.

## Entity inventory and compatibility

| Entity | Scope | Notes |
| --- | --- | --- |
| Next race / next race start / scheduled races | Per selected series | Existing Phase 1 IDs; unknown starts remain counted |
| Session type / flag / current lap | Per selected series | Existing IDs and experimental feed semantics retained |
| Leader / total laps / laps remaining / session progress | Per selected series | Only the reported series; unknown facts remain unknown |
| Reported field size | Per selected series | Normalized identified competitors; disabled by default |
| Favorite-driver live position | Per selected NASCAR driver ID | Current monitored global series; independent of references |
| Favorite last/best lap, gap, running status, positions gained | Per selected NASCAR driver ID | Disabled by default; enable chosen metrics in the entity registry |
| Feed status / last successful update / source stale | Per selected series | Existing transport and source freshness diagnostics; last update is disabled by default |
| Calendar | Per selected series | Read-only race weekends and supplied sessions; explicit time policy above |
| Favorite-driver metadata | Per selected NASCAR driver ID | Name and reliable reference facts only |

Existing Phase 1 entries require no manual migration: omitted favorites default to an empty selection, and source, authorization, selected series and polling settings retain their meanings. No full season list, directory or leaderboard is placed into Recorder attributes. A future dashboard will consume normalized models through its own data interface. Phases 3A/3B add metrics without changing existing unique IDs or config version.

## Experimental live timing and favorites

The global live feed reports one series/run at a time. Only that reported,
selected series supplies timing; other series show `not_reported`, with scoring
unavailable. No concurrent coverage is inferred. The leaderboard includes every
usable reported NASCAR driver identity, ordered by reported position, with
unranked entries last. A unique reported first position supplies the leader's
NASCAR ID, name and car number. Missing identities are counted in diagnostics;
duplicate driver IDs invalidate scoring without disabling valid flag/lap data.

Each favorite adds one enabled live-position sensor on its existing driver
device. Last lap, best lap, gap, running status and positions gained are created
disabled by default. Enable selected metrics through the device's entities in
Home Assistant. These sensors follow the NASCAR driver ID across race, run,
series, car and name changes; their compact attributes identify the current
series/race/run. A directory outage does not disable timing. A driver absent
from the current field is unavailable; a present driver with an omitted metric
has an unknown value. Removing a favorite removes its metadata and live sensors.

Last/best lap times use seconds. The gap preserves the reported `delta` with no
assigned unit: negative-value/lapped-car semantics are unverified. Only vehicle
status code 1 maps to `running`; other codes remain unknown, never guessed as
retired or finished. Positions gained means reported starting position minus
reported current position, not movement since the previous poll. Source speed
fields and laps-led intervals remain in the normalized model; no interval total,
interval-to-next, team, pit, stage or points value is fabricated.

Session type retains its existing meaning (practice/qualifying/race). The new
session-progress sensor uses `active` only for a fresh, positive-lap observation
with a recognized green/yellow/red/white flag. A fresh checkered observation is
`completed`, which does not mean official results are final. Cold/hot-track,
unknown flag, missing/implausibly future source time or lap-zero observations
cannot establish activity. Other states include `stale`, `not_reported`,
`no_active_session`, unknown and unavailable. No automation events are emitted.

A successful HTTP response/304 cannot prove fresh scoring. Explicit-offset
source time is evaluated separately, with the existing five-minute future-clock
tolerance and 15-minute stale threshold. Unknown source freshness is reported
as `freshness_unknown`: the leaderboard, leader, field size, reported lap totals,
remaining laps and all favorite live metrics are unavailable until source
freshness is established. Active/completed progress stays unknown. The existing
Phase 1 session-type, flag and current-lap entities retain their reported-value
behavior; consult feed status for their freshness. Stale or failed scoring is
also unavailable; retained models remain diagnostic context. Reported lap totals
and remaining laps are never calculated from each other; practice sentinel
totals are not race distances.

No CF endpoints or polling loops were added. The existing conservative
300–3600-second minimum, schedule windows, cache validators and backoff remain.
Unknown and track-only flags cannot accelerate polling. Full fields stay in
memory, with at most 100 vehicle rows; there are no per-nonfavorite entities or
whole-field Recorder attributes. Live sensors skip unchanged samples. Legacy
`source_updated_at` attributes identify the last meaningful sensor sample;
diagnostics expose the latest source and successful transport timestamps.
The optional last-successful-update sensor remains disabled by default.

All CF timing remains experimental. The [structural fixture contract](tests/fixtures/PHASE3A_LIVE.md)
records community evidence and unsupported semantics; no direct CF request or
active-session verification was possible. Offline demonstration still supplies
fictional schedules/references and an empty live feed. Synthetic live replay is
exercised through mocked provider and actual Home Assistant tests.


## Phase 3B pits, stages and championship points

Current stage uses the live feed's embedded stage descriptor. Each favorite can
opt into **Last reported pit lap**, which includes a small set of reported entry/
exit clocks, lap/ranks and signed movement from that driver's embedded records.
Clock units, completed-stop counts and pit durations are not inferred. Empty or
ambiguous pit records cannot invent a last stop. All values require a fresh
matching monitored race source; there is no per-driver request.

Three per-series diagnostic sensors explain standalone pit, stage-result and
championship-point capability. The observed global pits lack race/driver IDs,
stages reference a different race and lack series/source time, and points have
zero context IDs. These datasets remain separate in memory and **cannot currently
supply active-race scores**. Fresh HTTP responses cannot resolve those blockers.
No name/car/membership-ID or numeric cross-namespace join is attempted.

Reported stage position/points and provisional championship position/totals/race
points are opt-in favorite summaries. Reported stage-result-set count and
provisional championship leader are opt-in race summaries. These remain
unavailable unless a provider establishes the required identity and source time;
CF currently cannot. No totals, completed stages, scoring rules, championship
rank changes or official finality are calculated from incomplete evidence.
Checkered never promotes provisional scores to official results.

One shared optional refresh reads the three global feeds, at least 15 minutes
apart during supported active racing and six hours otherwise. Failures remain
independent; server backoff and cache validators apply. These defaults do not
establish NASCAR polling permission. See [Phase 3B validation](docs/PHASE3B_VALIDATION.md)
for executed checks, measured request/Recorder budgets and remaining work.
