# Phase 4A — Historical data foundation validation

October 21, 2026 (America/New_York). Branch `phase4a-historical-foundation`
starts from latest merged main **3d1e6d31413736dc787332a1917918b79b9ce037**,
including Phase 3D-B / PR #8. Remote main was checked before implementation.
The inherited 615-test baseline remains in the full suite; **195 new cases**
exercise history. No separate untouched-baseline run is claimed for this task.

The project brief, AGENTS, roadmap, architecture, endpoint/field/provenance/audit
documents, supplied observed profiles/relationships and current transport,
provider, scoring, polling, lifecycle and validation implementation were reviewed.
Prepared Python **3.14.8**, Home Assistant **2026.10.2**, Ruff **0.17.1** and
mypy **2.4.0** were reused without onboarding or dependency reinstallation.

## Delivered scope and evidence

All seven requested datasets are implemented: historical weekend/results and
sessions; per-driver laps and flags; object-keyed lap notes; reported loop
statistics; historical Title/Items lap averages; archived pits; archived stages
and stage points. [HISTORY.md](HISTORY.md) is the exact field/model, endpoint,
status, retention/resource and consumer contract. The supplied observed profiles
13–19 and verified_relationships.json establish structural evidence; seven new
minimal handmade fixtures contain fictional values, with explicit provenance.
No redacted placeholder is used as a result, identifier or functional fixture.

Complete identity is `(season, series_id, race_id)`. Weekend race/results report
all three; loop rows report race/series; archived stages report race/run; other
historical feeds rely on explicitly labeled path context. Contradictory supplied
contexts fail the individual feed. No automatic inter-feed merge or join occurs.
Car numbers remain strings. NASCAR driver identity is never inferred from names,
car numbers, directory Driver_ID or membership_id. Weekend-run, timing-run,
results-run and stage-run fields retain distinct namespaces. Archived pits remain
race-scoped observations with no invented driver association. Source enum codes,
null/missing values, reported score zero and uncertain 999/-1/zero candidates
remain distinguishable. Existing Phase 3B pit/stage parsers are reused unchanged.

`HistoryStatus` distinguishes available, empty, not_yet_published,
unsupported_unverified, partial, network_access_failure and
invalid_schema_identity. Current CF evidence has no trustworthy publication
signal, so `not_yet_published` remains reserved for an evidenced provider signal;
404/410 explicitly retain unknown publication/coverage, never a guessed meaning.
No reported field, inspection Boolean or checkered observation establishes
official final classification.

## Actual checks

| Check | Executed result |
| --- | --- |
| Full `pytest -q` | **810 passed**, including all existing 615 cases and 195 new history cases |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed (complete checkout) |
| `mypy custom_components/nascar_race_center` | Passed; 33 integration source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Independent prepared HA runtime smoke | **1 passed**; authenticated REST/state/service dispatch, separate from integration behavior |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| GitHub Actions | Hosted results are recorded in the Phase 4A PR after completion; no unexecuted hosted check is claimed as passing here |
| HACS | Private-repository conditional skip remains, with the existing temporary brands exception; no full HACS approval |
| NASCAR requests during this assignment | **Zero** probes, captures or origin calls; every endpoint-shaped test call is synthetic/intercepted |
| HA OS/production installation and physical devices | Not exercised; existing acceptance gates remain open |

Official Hassfest used `script/` from HA commit
`8d7fd8b68677c2585be36ec86043308f403875b8` (tag 2026.10.2), retrieved under
ignored `work/home-assistant-core`. Git and local test sockets used supported
network-enabled execution with inherited proxy/TLS intact. No Docker rebuild,
denied-destination bypass, original dataset collection or NASCAR permission
change occurred.

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
pytest -q
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
PYTHONPATH=work/home-assistant-core python -m script.hassfest \
  --integration-path custom_components/nascar_race_center
pytest -q -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
git diff --check
```

## Measured request, lifecycle and resource behavior

Actual HA fixtures exercise CF startup, on-demand retrieval, ordinary refreshes,
reload, modeled process restart, shutdown, failed/cancelled setup and offline
demo. These are integration tests, not just calls to parsing helpers.

- Three selected series retain the **seven GET** single-season startup budget:
  one basic schedule, three session schedules, one global live and two references.
  Historical detail GETs are **zero** at startup and during ordinary
  live/schedule/reference/scoring refreshes.
- Twenty concurrent actual-HA consumers requesting the same historical lap feed
  produce **one additional GET** (total eight). Another read uses cache (still
  eight). Reload clears history, reuses existing non-history cache/throttle state
  and issues **zero additional historical GETs**. Ten simulated hours after unload
  issue no further requests.
- Separate broker tests use thirty concurrent consumers, including no-cache and
  no-store responses, with **one GET**. A selected feed performs one attempt and
  no automatic retry; a request can explicitly select at most seven datasets.
- Actual Recorder measurement: ten reads of all seven offline history datasets
  add **zero state rows**. Entity registry IDs are unchanged by history reads;
  diagnostics contain no driver name, lap fields or raw historical response.
- One cancelled shared waiter leaves the other's read usable. Last-waiter
  cancellation aborts an actual blocked transport stream and releases its lock.
  Shutdown before queued child tasks start prevents late I/O.
  Entry unload, reload and HA stop cancel/drain in-flight reads and close the old
  service. Failed/cancelled setup closes history; process-state loss restores no
  historical body/validator/result. The HA shared session remains caller-owned.
- History has a separate **two-document LRU**, verified not to evict live data.
  Each decompressed JSON document is limited to **2 MiB**. Input/response cache,
  normalized-model and consumer ownership limits are distinguished in HISTORY.md;
  decoded-object memory is larger than source bytes. Broker retention ends after
  the final waiter, and lifecycle cleanup clears cached raw data/validators.
- Requests are bounded to **eight distinct in-flight keys**. A ninth key returns
  `request_budget` with no I/O. Same race IDs across years/series use distinct
  request/cache keys. The one-hour fallback, 60-second per-path floor, existing
  bounded throttle metadata, upstream directives and host-wide rate-limit rules
  apply; these are engineering safeguards, not NASCAR permission.
- Tests reject >5,000 laps per driver, >50,000 total lap rows and oversized notes
  without silently truncating results. An additional synthetic normalization
  measurement accepted **50,000 minimal lap records**, **739,463 JSON bytes**,
  with **3,602,808 retained / 4,300,056 peak traced allocation bytes**. This
  measures normalization allocations only, excluding preexisting input, HTTP JSON
  decoding, caller-held models and other HA state; it is not a whole-process RAM
  ceiling or an original NASCAR dataset measurement.

Synthetic cases cover all three series, 2019/2024/2026, reused race IDs, missing
and empty results/laps, partial peers, context conflicts, separate driver/run
namespaces, nullable/zero/sentinel/unknown/signed enum values, duplicate IDs,
malformed/Boolean/numeric-string/nonfinite/extreme inputs, wrong envelopes,
bounded arrays/cache and request tables, cache expiry, 304/validators, no-store,
success/error Retry-After, 403/404/410/429/503, network failure and cancellation.
History 429 also suppresses other endpoint network requests through the existing
host-wide control. Existing adaptive scheduler/performance, stale/feed handling,
favorite/sensor/calendar IDs, Recorder budgets, event baseline and durable
deduplication/persistence-before-publication cases all remain passing.

## Consumer boundary and remaining gates

Phase 4B and Phase 5 should call
`entry.runtime_data.history.async_get(HistoricalRaceKey(...), datasets_tuple)`
and consume each immutable `HistoryResult` with its availability/provenance.
They must not call live coordinators to download history, access provider JSON,
persist raw datasets or treat source statistics as derived/official results.
The current API exposes no dashboard route; a future authenticated view must
apply its own consumer lifetime, retention and authorization constraints.

The single observed examples do not prove endpoint availability across years,
series or races. Lap/notes/average/pit content identity beyond path provenance
remains unverified; note driver references and pit name/car matches are not
trusted joins. Timing/speed units, source timezone, status-code definitions,
candidate sentinel meanings, race finality, scoring/rating/closing-window formulas,
unobserved weekend pit_reports/infractions item shapes, legacy practice-average
variants, original-data replay and current anonymous/active-session behavior
remain unsupported or unverified. Requests above resource limits fail explicitly;
there is no pagination, permanent archive, bulk season detail or speculative URL.
The shared serialized transport can delay other consumers behind on-demand I/O.

Data-use, cadence, permitted retention/redistribution and media rights remain
unresolved. MIT remains code-only. No SnappyTV/Drive/recap integration, NASCAR
network request, original data redistribution, public visibility change, merge,
deployment, release, Phase 4B analytics or Phase 5 dashboard is included.
