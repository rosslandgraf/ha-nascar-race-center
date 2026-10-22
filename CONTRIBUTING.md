# Contributing

Read [AGENTS.md](AGENTS.md), the complete [brief](NASCAR_Race_Center_Codex_Brief.md), and the [roadmap](ROADMAP.md). Phases 1 and 2 are reviewed and merged. Keep Phase 3A limited to live timing/leaderboards; later pit/stage/points/event work requires a new assignment. Keep changes focused and open a pull request; no direct merge, production installation or public release is part of normal development.

## Development environment

The prepared cloud environment is already installed. Restore its toolchain:

```bash
cd /workspace/ha-nascar-race-center
source /workspace/.cloud-setup/nascar-race-center/activate.sh
python --version
hass --version
```

Expected baseline: Python 3.14.8 and Home Assistant 2026.10.2. Do not use the host's default Python or repeat onboarding. On a different machine, create a Python 3.14 virtual environment and install `requirements_test.txt`; Home Assistant tests may also need the system TurboJPEG library. CI uses Ubuntu 24.04 and its `libturbojpeg` package; Debian and other distributions may use a different package name. The integration itself uses Home Assistant's existing dependencies and must not install packages during setup.

Run the project checks:

```bash
ruff check .
ruff format --check .
mypy custom_components/nascar_race_center
pytest -q
```

Tests run against actual Home Assistant test fixtures with mocked providers/HTTP, without NASCAR access. Keep fixtures minimal and synthetic until redistribution permission is established. Document response-shape evidence and include meaningful error, time, cache and lifecycle cases for changed behavior. Do not commit local HA configuration, `.storage`, databases, logs, secrets, or environment files.

## API reference workflow

Before implementing a feed-dependent feature, read the
[API library](docs/api/README.md), [endpoint catalog](docs/api/ENDPOINT_CATALOG.md),
[field dictionary](docs/api/SCHEMA_REFERENCE.md) and
[latest API audit](docs/api/AUDIT_REPORT.md). Fixtures now live in
`tests/fixtures/nascar/`, with individual provenance and unchanged fictional data.
Consult current real responses when authorized/practical and record exact
URL/time/IDs and evidence limits. The developer-only
`python scripts/nascar_reference.py --authorized --endpoint live_feed` command
stores eligible raw JSON locally under ignored `work/`; `--baseline` reports
schema differences. Review them before editing documentation or authoring a
minimal synthetic regression. It never updates reviewed fixtures automatically.
Keep live checks separate from ordinary CI and leave production on its actual
network adapters/polling architecture. See the library for network and data-use
boundaries; an inaccessible response is not permission to invent its schema.

## Restored-runtime verification

The prepared environment also contains an independent runtime smoke test. It validates the environment's authenticated HA API and service dispatch; it is separate from integration tests:

```bash
pytest -q \
  -c /workspace/.cloud-setup/nascar-race-center/validation/pytest.ini \
  /workspace/.cloud-setup/nascar-race-center/validation/test_homeassistant_runtime.py
hass --script check_config \
  --config /workspace/.cloud-setup/nascar-race-center/hass-config
```

These paths are environment helpers, not installed integration dependencies. Never point validation commands at production. Use the integration in demonstration mode for local review.

## CI and review

GitHub Actions runs the pinned Python/HA test baseline, Ruff, mypy, Hassfest and HACS integration validation. Action wrappers are pinned to reviewed commit SHAs. Upstream Hassfest/HACS wrappers currently use their maintained validator container tags, so validator behavior can change independently of this repository. Review failures against current official requirements.

The upstream HACS validator rejects private repositories, so its CI job runs only when the repository is public. Keep this project private until the owner authorizes publication; a skipped job is not successful HACS validation. The current workflow has no brands exception: the Integration contains an original local NRC icon supported by current HA/HACS. Owner asset approval and the full official validator on an approved public repository remain gates. CI does not contact CF, publish releases, install on production, or establish data-use rights. Report actual results and outstanding checks in the PR, including any action still queued or requiring first-run approval.

For current guidance see Home Assistant [manifest](https://contributors.home-assistant.io/core/integrations/manifest/), [config flow](https://contributors.home-assistant.io/core/integrations/config-flow/) and [data fetching](https://contributors.home-assistant.io/core/integrations/fetching-data/) documentation, plus HACS [integration](https://www.hacs.dev/docs/publish/integration/) and [validation action](https://www.hacs.dev/docs/publish/action/) requirements.

The frontend build writes directly into the installed component's `frontend/`
directory. Run `npm --prefix frontend run build` before Python packaging tests.
See [packaging/reproducibility](docs/HACS_DISTRIBUTION.md) for the local-only
exporter and the explicit publication boundary. No workflow publishes releases.
