# Data use, licensing and publication

The repository already contains an MIT [LICENSE](../LICENSE) for project code. That license is retained. It grants no rights to NASCAR's data, names, trademarks, photographs, logos, video, or third-party material. The project is independent and is not presented as an official NASCAR product.

The owner's 2026-10-20 browser tests establish reported accessibility of some CF URLs in that browser. They do not establish anonymous access for ordinary users, permission for automated polling, storage/redistribution rights, permitted request rates, or playback rights. No NASCAR employee credentials, restricted Swagger access, login cookies or inferred tokens are needed or supported by the integration.

The integration defaults to offline demonstration data. The CF provider is experimental and requires the user to acknowledge that their intended access is authorized. This acknowledgement does not resolve the project's broader permission questions. Developers and reviewers should use demo mode and mocked tests until live access and usage have been cleared. No automated CF collection was performed for Phase 1 or Phase 2 development or CI. Phase 2's schedule, driver and track adapters rely on the [recorded community schema evidence](SCHEMA_EVIDENCE.md), not current CF captures.

Before public release, broad distribution, production collection, or an increase in polling frequency, the owner must review applicable terms and establish permission where required. Record the scope, rate limits, retention, redistribution and attribution requirements in this document. Public URL accessibility alone is insufficient. Do not claim that a passing HACS or Hassfest check grants data rights.

No NASCAR-controlled logos, driver photographs, video assets or full captured feed datasets are included. Fixtures are minimal handmade structural examples and must be marked as synthetic with source-shape provenance. Driver and track fixtures use fictional names and IDs; source media URL fields are ignored and not fetched. No third-party implementation or source dataset is vendored. Future optional dashboards use neutral placeholders or properly authorized user-supplied assets. Do not scrape NASCAR Drive, infer access tokens, proxy video, or treat SnappyTV metadata as permission for playback.

## Outstanding decisions

| Decision | Status |
| --- | --- |
| Project code license | Existing MIT retained |
| Anonymous CF access independent of owner browser session | Unverified |
| Automated access and permitted polling cadence | Unresolved |
| Data storage, historical retention and redistribution | Unresolved |
| Public integration/dashboard distribution | Owner approval and permission review pending |
| Branding/assets and Home Assistant brands submission | Deferred; no NASCAR assets distributed |
| Production installation/public release | Not authorized by the Phase 2 task |

HACS integration requirements include a Home Assistant brands entry. CI continues to skip the `brands` validation while authorized branding is unresolved; this exception is a release blocker. The official HACS action was attempted during Phase 1 and refused this private repository. Its workflow job runs only for public repositories, without changing visibility or making private-development CI fail. Full HACS validation remains unexecuted. The validator is configured with comments disabled and no release/deployment workflow is provided.
