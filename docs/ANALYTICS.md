# Historical analytics contract v1 (Phase 4B)

The analytics layer consumes the immutable [Phase 4A history models](HISTORY.md).
It calculates evidence-limited numerical descriptions of recorded observations.
It supplies no HTTP/WebSocket route, HA service, frontend, entity or persistent
archive. Phase 5 owns authentication, transport, client formatting and charts.
MIT licenses the code only; [NASCAR data-use gates](DATA_USE.md) remain open.

## Internal API for Phase 5

```python
from custom_components.nascar_race_center.analytics_models import AnalyticsQuery
from custom_components.nascar_race_center.history_models import (
    HistoricalRaceKey,
    HistoryDataset,
)

# Fictional illustrative selection; use the consumer's explicitly selected race.
query = AnalyticsQuery(
    HistoricalRaceKey(2024, 1, 88001),
    driver_ids=(99002, 99003),
    first_lap=1,
    last_lap=200,
    windows=(5, 10),
    time_basis="all_available",
)
result = await entry.runtime_data.analytics.async_get(
    query,
    (
        HistoryDataset.LAPS,
        HistoryDataset.WEEKEND,
        HistoryDataset.STAGES,
        HistoryDataset.LOOP,
        HistoryDataset.AVERAGES,
    ),
)
```

The dataset tuple is required, nonempty, distinct and explicit. Request only
needed datasets. The service calls the existing `runtime_data.history.async_get`
once with that selection. It never downloads adjacent races, polls, retries,
prefetches, discovers IDs or calls a provider/HTTP client directly. A consumer
that already has history can call the pure
`analytics.analyze_history(history_response, query)` without retrieval or HA.

The same `AnalyticsResult` supports every screen size. Its immutable frozen/slots
models expose `contract_version=1`, the complete race key and selected NASCAR IDs
in `query`, per-dataset `evidence`, driver `samples`, compressed missing-lap
`gaps`, `coverage`, time `metrics`, consecutive runs, rolling windows,
lap-indexed `positions`, pairwise `comparisons`, `performance` rows and small
`race_metrics`. Scalars have `name`, `value`, `method`, `unit`, classification and
an unavailable `reason`. `Metric.available` means `value is not None`, so reported
or derived zero remains distinct from missing data. No provider JSON is exported.

`performance.result` retains selected reported race results: start/finish,
completed/led laps, race/playoff points, source finishing-status text and other
Phase 4A fields. `performance.sessions` retains selected nested session results
with separate weekend-run and timing-run fields; each result preserves its own
results-run ID. `race_timing_run_id` and archived stage-run IDs are separate.
Numeric equality across these namespaces never establishes association. Session
average `Title` strings remain labels with source array indexes, not run IDs.
Session rows are exposed as reported observations, never pooled with race laps.

Invalid selections raise `ValueError` before I/O; a closed service raises
`RuntimeError`. Cancellation propagates. Identity/schema/resource problems in
one normalized dataset yield invalid evidence and unavailable dependent metrics;
valid independent peers survive. This is an internal Python contract: Phase 5
must supply its own authorized transport and bounded client retention.

## Inclusion, ordering and coverage

For each selected driver, use only observations whose recorded lap number is in
the inclusive `[first_lap, last_lap]` selection. There is no lap-zero heuristic:
a lap-zero null is excluded because it has no time. A numeric lap time enters
time calculations only when it is finite, strictly positive and not Boolean.
Missing/null values count as `missing_times`; zero, negative, NaN, infinity and
invalid types count as `invalid_times`. Nonfinite values are omitted from the
output numeric field and retain an exclusion reason; no JSON NaN is produced.

There is no documented lap-time sentinel or verified unit. In particular a
positive lap time of 999 passes this numeric rule; an arbitrary magnitude filter
would invent source semantics. Reported *average* fields independently preserve
Phase 4A `candidate_sentinel` labels for 999/-1/zero. These values never feed a
derived time statistic. Reported loop metrics preserve exact field names,
signed values and nulls. No source rating, closing-window, passing or long-run
average formula is reconstructed or assumed equivalent to a derived measure.

`samples` preserve original within-driver order and full-input `source_index`,
reported lap number, finite original time and reported position. Computational
series/windows are ordered by lap number. Tied fastest times choose the smallest
recorded lap number. `consecutive_time_delta` is attached to the later numbered
lap only when its immediately preceding numbered lap is included and valid;
source array adjacency alone is insufficient. Derived classification applies to
selection, differences and summaries; reported source rows remain recorded.

Coverage reports requested lap-number count, recorded rows, absent lap numbers,
missing/invalid/valid times, included time-basis samples, valid times excluded by
that basis, usable positions and source rows outside the selected range. These
are counts, not estimates of a driver's race completion. Gaps are inclusive
compressed intervals, including leading/trailing absence within the selection.
A recorded null is a sample with an exclusion, distinct from an absent lap.
There is no invented lap, time, position, interpolation or automatic truncation.

## Exact formulas and sample requirements

Let `x_1 ... x_n` be valid times in the chosen time basis. All calculations use
the reported numerical scale, labeled `source_lap_time_unit_unverified`; no
seconds, speed unit, green-flag classification or race condition is inferred.

| Metric | Definition / requirements |
| --- | --- |
| `fastest_reported_lap`, `minimum` | `min(x)` for `n >= 1`; `fastest_lap` is its observed lap number |
| `maximum` | `max(x)` for `n >= 1` |
| `mean` | Arithmetic mean `sum(x_i) / n` for `n >= 1` |
| `median` | Sorted middle value for odd n; arithmetic mean of two middle values for even n |
| `range` | `max(x) - min(x)` for `n >= 1` |
| `population_stddev` | `sqrt(sum((x_i - mean)^2) / n)`; deliberately requires `n >= 2` |
| `coefficient_of_variation` | Population standard deviation divided by positive arithmetic mean; dimensionless fraction, `n >= 2` |
| `consecutive_time_delta` | `time(lap) - time(lap-1)` for a valid included consecutive pair |
| `mean_absolute_consecutive_change` | Mean of absolute consecutive deltas, requiring at least one such pair |
| `consecutive_pair_count` | Number of those pairs; zero is a valid derived count |

Population deviation describes the selected observations, with denominator `n`,
not the inferential sample estimate with `n-1`. It and coefficient of variation
are unavailable for one observation, rather than implying meaningful consistency
from a singleton. Neither measures driver skill, tire degradation or conditions.
No confidence, full-race representativeness or official fastest-lap claim follows
from these statistics. Missing times are not zero and never enter denominators.

The implementation uses accurate `math.fsum` arithmetic and Python's stable
`statistics.pstdev`, which avoids cancellation for nearly equal large values.
Means fall back to scaled summation if an intermediate sum overflows; median
avoids overflow when averaging middle values. Nonrepresentable derived values
return unavailable with `numerical_range`, never infinity. Floating-point
rounding still applies. Calculations are deterministic for identical immutable
inputs, including the unchanged input provenance timestamps; no clock is read.

## Consecutive windows and comparison basis

Window sizes are a caller-selected distinct tuple from **5, 10, 15, 20, 25, 30**;
the default is `(5,)`, and `()` disables rolling output. A maximal consecutive
run contains valid included observations at every integer lap number. Every
overlapping N-lap window within each sufficient run supplies start/end laps,
sample count N, arithmetic mean, median, minimum and maximum. `best_N_lap_mean`
is the minimum of these window means. Insufficient runs return no windows and
an unavailable best mean with `no_sufficient_contiguous_window`. Missing or
invalid times always break a run. Windows never imply pit cycles or tire age.

- `all_available`: each driver uses all its own valid selected-range times.
  Unequal counts remain explicit. Independently best windows can start on
  different laps; they do not establish comparable track or race conditions.
- `overlapping_valid_laps`: intersect valid recorded lap numbers across **all**
  selected drivers before time summaries and windows. Missing selected drivers
  produce an empty common basis. This does not establish simultaneous timestamps
  or conditions. Position observations continue to use their own complete series.
- A particular contiguous interval can be selected by setting first/last lap
  explicitly. Selecting exactly N lap numbers yields one N-lap window only if
  every necessary valid observation is present in the selected basis.

Every ordered-selection pair of distinct drivers supplies comparable time
metric values, including each configured best window mean. Differences are
`left - right`; relative percentage is `100 * (left - right) / right`. A missing
operand yields `metric_unavailable`; a zero reference yields unavailable relative
percentage with `zero_reference_value`. Negative time differences describe lower
numerical observations, not proven better strategy. Both driver sample counts
and the query basis accompany each pair; consecutive-pair denominators remain
in each driver's metrics. No ranking combines different measurement types.
Reported loop/average groups remain separate from these derived comparisons.

## Positions, results and stages

Usable position observations are strict integer ranks 1–100, consistent with
the historical model's maximum 100 drivers. Missing/zero/-1/999/Boolean positions
remain unusable for position calculations; raw reported values are retained.
`positions.points` are lap-indexed, preserving source indexes. Start/end mean
the earliest/latest *usable observed* position in range, not grid/finish.
Observed change is first minus last and requires two distinct observed laps.
Best/worst are minimum/maximum usable rank. The count of samples at position one
is explicitly `first_position_observation_count`; it is never official laps led.
With no usable positions it is unavailable, rather than a fabricated zero.
No position change is described as an on-track pass or filled across gaps.

Reported weekend `laps_led` stays in the source result, separate from sample
counts. No field in the supported historical result model reports position
difference: `reported_position_difference` is explicitly unavailable.
`start_finish_position_change` is separately **derived**, reported starting
position minus reported finishing position, requiring two usable positions.
DNF/status/disqualification text/flags and incomplete completed-lap counts are
retained without interpreting finishing-status vocabulary or inventing results.
Race summaries expose only directly reported scheduled/actual laps. No winner,
official final classification, championship standings or points are inferred.

Weekend and archived stage observations retain their source dataset, stage
number, reported position/points and the archived `stage_run` identity. They
are not merged or used to compute scores. Overlapping non-null disagreements in
position or points mark both observations `conflict=True`, add a caveat and make
the aggregate partial; neither source silently wins. Conflicting archived race,
season, series, namespace or run context invalidates that independent dataset.
Archived pit rows and commentary references never join a driver by name, car
number, source row position or matching numeric run values. Pits/notes can be
requested through history but this analytics contract exports only their evidence.

## Provenance, availability and identity

Every dataset's original `HistoryProvenance`, status and fixed reason are retained
in `evidence`. Complete requested race keys must match the response and every
provenance key. Weekend reported keys and archived stage contexts are rechecked.
Duplicate datasets, NASCAR driver IDs, driver/lap numbers, stage identities,
weekend-run identities, reported metric labels and conflicting results-run IDs
are rejected in their own scope. No deduplication chooses an arbitrary row.
Driver names, car numbers, directory IDs and membership IDs are never join keys.

`reported_identity`, `path_context_only`, `fictional` and coverage labels remain
distinct. Path context allows explicitly scoped descriptions; it cannot certify
lap/average content identity or cross-season/series coverage. A failed or
`not_validated` result cannot supply calculations. HTTP success/cache/receipt time
does not prove source freshness, completeness or finality. Unrequested datasets
remain absent; source empty/unsupported/not-published/network/invalid states
retain their Phase 4A meanings without inference or alternate endpoint fallback.

Aggregate status is `invalid` if no usable observations remain after invalid
input, `unavailable` if no supported selected observations remain, `partial` for
failed peers, conflicting stage observations or incomplete requested lap data,
and `available` otherwise. Individual unavailable scalars still carry reasons;
an available response does not promise every possible field or window exists.
Driver lap status records missing drivers, unavailable feeds, range absence,
invalid/missing samples, position gaps and basis exclusions independently.

## Computational and lifecycle bounds

- 1–8 distinct positive NASCAR IDs; at most 28 pairwise rows.
- Inclusive nonnegative lap range of at most 5,000 numbers; defaults 0–4,999.
  Set actual bounds explicitly, for example 1–5,000. Lap numbers may be at most
  10^10, matching Phase 4A; no array is allocated up to that numerical value.
- Projected rolling work `drivers * range_length * window_count <= 60,000`.
  Oversized selections raise before retrieval. All six windows with eight drivers
  allow at most 1,250 lap numbers; the default single window allows 5,000.
- At most 40,000 selected lap samples and 60,000 rolling windows per response;
  compressed gap/position/run objects also scale with selected rows. Reported
  groups retain only selected drivers and the fixed supported metric labels.
- Phase 4A source limits remain: 100 drivers, 5,000 rows per driver, 50,000 total
  lap rows, one loop group, 30 average/weekend sessions and 20 stage groups.
  Oversized or duplicate data fails explicitly; nothing is silently clipped.
- Source validation/indexing is linear in bounded source rows; sorting/median is
  `O(L log L)` per selected driver. Each rolling summary processes at most 30
  values; work is bounded by `O(30 * projected_rolling_work)` plus sorting those
  short windows. No race-by-race, driver-by-driver network loop is introduced.
- At most **two** distinct analytics requests per entry are in flight. Identical
  query/dataset-order selections share one retrieval and calculation, including
  source no-store responses. A third distinct request returns unavailable with
  `calculation_budget` and no retrieval. Different queries still share underlying
  history dataset flights and its eight-key request limit and two-document cache.
  A repeat of a cancelled selection whose worker is still draining returns
  `calculation_draining`; neither rejection performs calculations or returns rows.
- Calculations run in `hass.async_add_executor_job`; they cannot block HA's event
  loop. Cancellation cannot kill Python thread execution: the bounded pure job
  is drained before its slot is released. No late result is delivered after
  cancellation, and unload/reload/HA stop drains work before completing cleanup.
  One cancelled waiter preserves peers; the last waiter cancels/drains retrieval
  through HistoryService. Failed/cancelled setup also closes the analytics service.
- No completed result cache or persistent state is added. The broker releases
  normalized results after its last waiter; consumers own returned immutable
  objects and must bound retention. Repeated calls recalculate from the existing
  history/HTTP cache without new GETs while reusable. Startup and ordinary
  periodic refreshes perform **zero historical requests or calculations**.

No new endpoints, CF polling permission, entity IDs, Recorder rows, attributes,
automation events or HA Store content are introduced. No network access to NASCAR
is needed to test these calculations. See [Phase 4B validation](PHASE4B_VALIDATION.md)
for executed numerical, resource, integration and regression checks and the
remaining evidence limitations.
