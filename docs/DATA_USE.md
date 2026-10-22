# Data use, licensing and publication

The repository already contains an MIT [LICENSE](../LICENSE) for project code. That license is retained. It grants no rights to NASCAR's data, names, trademarks, photographs, logos, video, or third-party material. The project is independent and is not presented as an official NASCAR product.

The owner's 2026-10-20 browser tests establish reported accessibility of some CF URLs in that browser. They do not establish anonymous access for ordinary users, permission for automated polling, storage/redistribution rights, permitted request rates, or playback rights. No NASCAR employee credentials, restricted Swagger access, login cookies or inferred tokens are needed or supported by the integration.

The integration defaults to offline demonstration data. The CF provider is experimental and requires the user to acknowledge that their intended access is authorized. This acknowledgement does not resolve the project's broader permission questions. Developers and reviewers should use demo mode and mocked tests until live access and usage have been cleared. No automated CF collection was performed for Phase 1, Phase 2 or Phase 3A development or CI. Schedule, reference and Phase 3A timing adapters rely on the [recorded community schema evidence](SCHEMA_EVIDENCE.md), not current CF captures.

Before public release, broad distribution, production collection, or an increase in polling frequency, the owner must review applicable terms and establish permission where required. Record the scope, rate limits, retention, redistribution and attribution requirements in this document. Public URL accessibility alone is insufficient. Do not claim that a passing HACS or Hassfest check grants data rights.

No NASCAR-controlled logos, driver photographs, video assets or full captured feed datasets are included. Fixtures are minimal handmade structural examples and must be marked as synthetic with source-shape provenance. Driver and track fixtures use fictional values except tiny owner-supplied identity regression cases; source media URL fields are ignored and not fetched. No third-party implementation or source dataset is vendored. Future optional dashboards use neutral placeholders or properly authorized user-supplied assets. Do not scrape NASCAR Drive, infer access tokens, proxy video, or treat SnappyTV metadata as permission for playback.

## Outstanding decisions

The October 21 API audit authorized a bounded manual anonymous GET pass over the
original 28 URLs. All were denied at the environment proxy CONNECT step; no
NASCAR body was collected. This task authorization does not establish broader
NASCAR polling, storage or redistribution rights. The new
[reference library](api/README.md) commits metadata and handmade fixtures only.
Eligible future raw captures stay in ignored `work/` with private file permissions
until a separate rights/content review; excluded/no-store bodies are not saved.

| Decision | Status |
| --- | --- |
| Project code license | Existing MIT retained |
| Anonymous CF access independent of owner browser session | Unverified |
| Automated access and permitted polling cadence | Unresolved |
| Data storage, historical retention and redistribution | Unresolved |
| Public integration/dashboard distribution | Owner approval and permission review pending |
| Branding/assets | Original local NRC assets supplied; owner publication approval pending |
| Production installation/public release | Owner-controlled; this PR does not install, deploy or publish |

The bundled distribution supplies original local NRC brand assets, supported by
current Home Assistant and HACS; no global Brands submission or brands ignore is
required. The old brands exception was removed in PR #17. Owner asset approval
remains a publication gate. The official HACS action rejects private repositories,
so its workflow job runs only for public repositories. A private skip is not a
pass. Public metadata, full unskipped validation and publication remain open;
visibility is unchanged and no release/deployment workflow is provided. The
exported preview uses a self-contained [distribution guide](DISTRIBUTION_DATA_USE.md)
with no private archive links. The current [CF correction](REAL_CF_VALIDATION.md)
made no CF requests and grants no additional data-use or cadence permission.


Phase 3D-B's [polling capability](POLLING.md) does not resolve any permission
row above. CF's reviewed policy retains its conservative defaults; neither the
Adaptive setting nor the existing acknowledgement enables faster CF requests.
A future change must document independently verified permitted limits here
before updating the CF provider record. Synthetic 10-second measurements are
not NASCAR performance measurements or permission evidence.


## Phase 4A historical retention

The [history interface](HISTORY.md) adds only explicit on-demand access to seven
observed historical patterns under the existing CF authorization configuration.
This development task made no NASCAR requests and grants no additional access,
collection, polling or redistribution rights. The two-document in-memory history
cache and consumer-owned immutable models are transient; historical bodies,
validators and results are not persisted in Recorder, HA Store, logs or raw
diagnostics. Unload/reload/stop clear cached history, and restart restores no
historical data. The documented memory/request bounds are engineering safeguards,
not a NASCAR-approved retention or cadence policy. Source data rights, permitted
uses, anonymous/current-context coverage and public distribution remain gates.
The MIT license continues to apply to project code only. Fictional handmade test
fixtures are not NASCAR results or an authorization to redistribute real data.
