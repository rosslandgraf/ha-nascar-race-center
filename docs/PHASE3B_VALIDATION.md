# Phase 3B delivery and validation

October 21, 2026 (America/New_York). Branch `phase-3b-live-pits-stages-points`
starts at latest main `54d7d34`, containing merged PRs #3 and #4. The untouched
330-test baseline passed before implementation. Logical checkpoints were committed
and pushed during work. See [evidence and blockers](PHASE3B_EVIDENCE.md).

## Delivered behavior

- Parent-identified embedded pit records with reported laps, clocks, ranks and
  signed movement; source misspelling handled explicitly. Current stage and
  reported stage-lap descriptor share the live source's freshness/context gate.
  No completed-stop counts, pit duration subtraction or stage completion inference.
- Immutable standalone pit activity, stage results/points and championship
  position/points/race points/bonuses/stage scores/raw deltas. Global feed
  snapshots remain separate; optional results never supply another race/session.
- Explicit context, namespace, provenance, freshness and capability checks.
  Missing/zero IDs never become active IDs; car/name/membership identity is never
  substituted. Mixed contexts, historical scope and run namespaces are rejected.
- Fourth independent coordinator and shared transport/cache; bounded whole-feed
  retention, independent failures/retry hints, 15-minute active / six-hour idle
  polling, local expiry and entry-owned shutdown. No per-favorite/per-series
  feed requests, alternate URL search, historical fetch or persisted raw capture.
- Current-stage and diagnostic capability sensors; opt-in race stage-result-set
  count and provisional championship leader; three opt-in favorite summaries.
  Existing entity/configuration identity, demo and Phase 1–3A behavior preserved.
  Full datasets remain in memory. No events, notifications or Phase 3C work.

## Actual validation

Prepared Python **3.14.8**, Home Assistant **2026.10.2**; no onboarding,
dependency reinstall or production configuration changes. All NASCAR access in
these checks is mocked. Fixture values are handmade synthetic; structural keys
are checked against the imported package without treating placeholders as facts.

| Check | Result |
| --- | --- |
| Complete `pytest -q` | **428 passed** (330 baseline + 98 additional cases) |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 88 files |
| `mypy custom_components/nascar_race_center` | Passed; 25 source files |
| Official HA 2026.10.2 Hassfest | Passed; one integration, zero invalid |
| Independent prepared-runtime smoke test | Passed; one authenticated REST/state/service test |
| Prepared `hass --script check_config` | Passed; exit zero |
| `git diff --check` | Passed |
| HACS | Skipped while private; brands exception and full validation remain release gates |
| New NASCAR probes / original-capture replay / active race verification | Not run; network policy and unresolved data/polling permissions respected |
| Manual frontend/browser review | Not run; no frontend delivered; real HA fixtures exercise entities/options |

Hassfest used official HA commit `8d7fd8b68677c2585be36ec86043308f403875b8`
with only its scripts extracted into ignored `work/home-assistant-core`.
Commands needing fixture/multiprocessing sockets, Git or public source retrieval
used supported network-enabled execution with inherited proxy and TLS intact.
No denied destination was requested or bypassed. Hosted checks are recorded in
the pull request separately from these local results.

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

Coverage includes all three series, series/race/run/practice switches, unknown,
zero/negative/mismatched identifiers, namespace collisions, mixed contexts,
optional missing/null/sentinel fields, malformed/bounded/duplicate schemas,
pit entry/exit updates, ambiguous same-lap records, stage transitions/replacement,
reported championship changes, absent totals, nonfinal checkered observations,
stale/missing/future source clocks, independent source expiry, outages/403/429/503,
unexpected coordinator errors, cancellation, cache hits/304, favorites cleanup,
reload, failed/cancelled setup, queued and late in-flight shutdown behavior.

A fresh three-series CF setup with unavailable references makes **10 mocked GETs**:
the seven existing requests plus exactly one each for global pits/stages/points.
Immediate primary and scoring refreshes add **zero GETs** through shared caching.
An optional pit 429 makes **eight GETs** total and suppresses the following two
optional requests through host-wide backoff; a 403/503 isolates that endpoint.
No extra requests depend on the number of favorite drivers.

Actual in-memory Recorder measurement covers five advancing timestamps plus
nonfavorite timing changes: **zero new rows** for the unchanged favorite pit
summary and current stage. A subsequent changed pit exit clock produces exactly
**one favorite pit row**, with no new stage row. Existing Phase 3A Recorder
measurements remain in the complete passing suite. These are synthetic measured
budgets, not a live-session or production Recorder benchmark.

## Known limitations and remaining work

CF standalone stage results and championship scores are intentionally unavailable
as active-race entities: missing/zero IDs, unverified run namespaces and missing
source clocks cannot pass association. Standalone pit tire/type/duration facts
remain unbound in memory because that feed supplies neither context nor NASCAR
driver IDs. Embedded pits/current stage work when the parent feed is usable.
Trusted normalized synthetic providers demonstrate supported scoring rendering;
production never fills CF gaps with those facts or fixtures.

No evidence supports completed-stage counts from current stage, a verified
completed-stop count, pit-clock units, a points formula, championship position
movement, or official finalized results. Raw points deltas retain their source
names without invented units/meaning. Obtain authorized original observations,
explicit run mappings, timestamp/finality semantics and data/polling permission
before enabling blocked live relationships. Historical acquisition is Phase 4;
event deduplication/automation/notifications remain Phase 3C. HACS, branding,
broader compatibility and active-session acceptance remain release gates.
No merge, deployment, publishing or visibility change was performed.
