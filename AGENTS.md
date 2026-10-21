# Development instructions

Read the complete [project brief](NASCAR_Race_Center_Codex_Brief.md) before making architectural changes. It is the primary product specification. Check [ROADMAP.md](ROADMAP.md), [ARCHITECTURE.md](ARCHITECTURE.md), and the latest validation report before choosing scope.

## Scope and delivery

- Work on a feature branch and open a reviewable pull request. Do not merge to `main`, deploy to the owner's production Home Assistant, or publish a release without explicit authorization.
- Phases 1 and 2 are reviewed and merged. Phase 3A covers live timing/leaderboards only; do not begin Phase 3B/3C, pits, stages, points or automation events without a new assignment. The roadmap distinguishes delivered features from future design.
- Preserve the existing MIT code license. NASCAR data, trademarks, imagery, and video have separate, unresolved rights. Do not imply that the code license grants data-use permission.
- Record completed features, actual checks, known gaps, endpoint evidence, and data-use assumptions in every PR. Never report an unexecuted check as passing.

## Restore the prepared environment

The managed development environment already has Python 3.14.8, Home Assistant 2026.10.2, and development tools. Do not repeat onboarding or rebuild it routinely.

```bash
source /workspace/.cloud-setup/nascar-race-center/activate.sh
python --version
hass --version
```

That activation path belongs to the prepared cloud environment, not the installed integration. On other machines use a Python 3.14 virtual environment with `requirements_test.txt`. Inspect existing environment instructions before installing anything. Never commit local Home Assistant `.storage`, logs, credentials, or environment files.

## Provider and data boundaries

- Before API-related work, read [docs/api/README.md](docs/api/README.md), the
  [endpoint catalog](docs/api/ENDPOINT_CATALOG.md), field reference, fixture
  provenance and latest API audit. Distinguish blocked transport from origin
  responses, synthetic contracts from observed schemas, and HTTP freshness from
  active-race evidence. Follow the library's feature-validation workflow.
- Manual authorized checks use `scripts/nascar_reference.py`; keep raw captures
  in ignored `work/`, review schema differences, and never automatically replace
  fixtures. Routine CI stays offline. Neither production nor demonstration mode
  may silently consume bundled fixtures as live data.
- Use only the documented `https://cf.nascar.com` endpoint catalog. Never require employee credentials, use the restricted Swagger API, guess tokens, scrape video, or infer playback rights.
- Keep demonstration mode usable without network access. CF mode requires explicit data-use authorization in configuration; permission to develop does not establish permission to distribute or poll NASCAR data.
- Inspect the managed environment network policy before network work. Do not bypass a denied destination or disable TLS verification.
- Distinguish owner browser reports, third-party schema references, synthetic fixture tests, anonymous direct probes, and active-session validation. Update [docs/ENDPOINTS.md](docs/ENDPOINTS.md) when evidence changes.
- Do not invent provider JSON fields. Add minimal handmade structural fixtures with provenance before supporting a shape. Prefer structural fixtures over redistributing feed payloads while rights are unresolved.
- Missing data is unknown/unavailable; never fabricate zero readings, results, race status, or driver statistics. Route live data by the series and race IDs actually supplied.

## Implementation rules

- Use typed asynchronous Python and Home Assistant's shared aiohttp session. No blocking I/O in the event loop, private HA APIs, package installs during setup, or credentials in logs.
- Keep HTTP transport, provider parsing, normalized immutable models, coordination, and entities separate. Features consume models, not provider dictionaries.
- Use independent schedule and live coordinators. Optional live failures must not disable valid schedules. Keep last successful data for diagnostics while marking failed/stale entities accurately.
- Respect cache validators, bounded response sizes, timeouts, cancellation, and server retry hints. Use conservative polling and backoff; no rapid retry loops or live network calls in automated tests.
- One config entry manages selected national series (IDs 1, 2, 3). Use config/options flows, translated labels, validated options, typed `runtime_data`, and clean unload/reload.
- Base identifiers on integration domain, series ID, NASCAR driver ID, and session/race ID as appropriate. Never use driver names or car numbers as identity. Preserve IDs across options changes and upgrades.
- Keep Recorder attributes small. Future leaderboards/history belong in dedicated data views. Future events require baseline suppression and durable deduplication across restart/replay before being exposed.
- Keep optional frontend code in its own package. Integration HACS packaging and dashboard card packaging are separate deliverables.

## Validation

```bash
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
```

Use the actual Home Assistant fixtures and realistic mocked structural responses. Cover UI validation, setup/unload/reload, selected-series routing, stable IDs, stale/failed feeds, malformed data, rate limiting, timezone/season boundaries, and cache behavior as relevant to the change. Add meaningful tests for changed behavior, not implementation mirrors. CI runs Hassfest. The official HACS action rejects private repositories, so its job is conditional on public visibility; do not change visibility just to run validation. Its temporary brands exception must also be removed before release readiness. Report both limits rather than claiming full HACS approval.

Do not expose tokens, sensitive headers, local `.storage`, or full raw provider bodies in diagnostics. Never send messages to external recipients unless the user explicitly authorized that communication.
