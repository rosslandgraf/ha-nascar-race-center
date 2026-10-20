# NASCAR Race Center

A Home Assistant custom integration being developed for NASCAR's three national series. **Phase 1 is a development foundation, not a public release.** The default offline demonstration works without NASCAR access. An experimental CF adapter is available only after explicit data-use authorization.

The long-term target includes race-weekend schedules, timing/scoring, favorite drivers, championship points, historical analytics, automations and an optional responsive dashboard. See the complete [specification](NASCAR_Race_Center_Codex_Brief.md) and [phased roadmap](ROADMAP.md).

## Phase 1 scope

- UI configuration and options for one integration entry and selected national series (IDs 1, 2 and 3).
- Demonstration provider, typed CF adapter, asynchronous HTTP/cache/error boundaries, and separate schedule/live updates.
- Essential next-race, schedule, session-type, flag and current-lap entities, plus freshness/provider diagnostics.
- Mocked provider and Home Assistant lifecycle tests, Ruff/mypy checks, Hassfest and HACS validation workflows.

Full weekend calendars, favorite-driver tracking, timing leaderboards, pits/stages/points, automation events, history/analytics and custom cards are future phases. Phase 2 begins after Phase 1 review. The [validation report](docs/VALIDATION.md) records precisely which checks ran; configured CI is not a claim that every check passed.

## Development installation

Use an isolated development Home Assistant 2026.10.2 instance with Python 3.14. Copy only `custom_components/nascar_race_center` into that instance's `config/custom_components/` directory and restart it. In **Settings → Devices & services → Add integration**, choose **NASCAR Race Center**, leave the source set to **Demonstration**, and select the series to monitor. No YAML or NASCAR credentials are required.

Demonstration names and observations are synthetic and must not be used as actual race information. Options can change the source and selected series; the entry reloads to apply changes. CF mode should only be selected when the intended access is authorized, with the acknowledgement enabled. It may fail on access restrictions or unverified schema changes. The integration never asks for NASCAR employee credentials.

Remove the entry from **Settings → Devices & services** to unload entities and polling. To remove the integration files completely, delete `config/custom_components/nascar_race_center` in the development instance and restart. This task does not install anything on the owner's production Home Assistant.

## Data availability and permissions

The [endpoint matrix](docs/ENDPOINTS.md) preserves the owner's 24 successful and four failed browser reports. Those reports are not independent anonymous-access, schema or live-race verification. This environment's network policy excludes the CF host, so development and CI use structural mocks. Live session freshness, anonymous access and data-use permissions remain unverified.

The existing [MIT license](LICENSE) applies to project code; NASCAR data and media rights are separate and unresolved. Read the [data-use note](docs/DATA_USE.md) before enabling CF access. No NASCAR-controlled logos, photos, video or full feed captures are distributed. No public release or production deployment is authorized by Phase 1.

## HACS status

The repository uses a HACS-compatible integration layout and includes `hacs.json` and validation workflows. It is not yet release-ready or approved for the HACS default catalog. CI temporarily skips the HACS brands check while authorized branding is pending; that exception and all permission/release gates must be resolved before public distribution. The optional frontend card will be packaged separately in a later phase.

## Development

Use the already prepared environment; do not repeat onboarding. See [CONTRIBUTING.md](CONTRIBUTING.md) for restoration and exact validation commands, [AGENTS.md](AGENTS.md) for permanent development rules, and [ARCHITECTURE.md](ARCHITECTURE.md) for provider, model and coordinator boundaries.
