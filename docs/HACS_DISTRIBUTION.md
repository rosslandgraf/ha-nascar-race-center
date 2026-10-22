# Bundled HACS distribution candidate

Integration **0.2.0**, card **0.6.0**, HA Core **2026.10.2**. Starts from merged
PR #16, `7ca9d4d8d0ed837005adf366dcd5a5ecd9ae7a60`; preserves PR #15 and #16.
This is packaging preparation, not a release or completed public HACS approval.
See [owner migration, updates, rollback and uninstall](HACS_MIGRATION.md).

## Architecture and supported lifecycle

One normal HACS **Integration** download installs the complete
`custom_components/nascar_race_center/` directory: Python, translations, local
project icon, and the compiled card under `frontend/`. No second category/plugin
repository, npm installation on HA, runtime CDN or external web server is needed.
The TypeScript source remains a developer package outside the installed directory.

Domain `async_setup` uses HA's documented asynchronous HTTP API once per process.
`StaticPathConfig` exposes exactly the versioned JavaScript file, with standard
static caching. It never exposes a directory, Python, build metadata or settings.
A tiny public `HomeAssistantView` at **`/nascar_race_center/card.js`** has explicit
`Cache-Control: no-store` and imports the exact filename plus full SHA-256 query.
Static `cache_headers=False` alone does not guarantee no-store in this HA version;
the generated view makes this cache boundary explicit. Both routes contain only
code; existing authenticated administrator WebSocket data boundaries remain intact.

The executor validates bounded metadata (4 KiB), manifest (8 KiB), compatible
versions, filename, hash and artifact (180,000 bytes). The build also enforces a
50,000-byte gzip budget. Corrupt/missing optional assets produce loader 503 and
safe diagnostics while entities/automations keep working. Registration uses a
per-domain lock and state, independently of entry reload. No Lovelace collection,
private frontend API, `.storage` edit or production monkeypatch is introduced.

One manual resource edit preserves existing dashboards/card options. New custom
elements are guarded and the picker entry is deduplicated. Aliased loader URLs
import the same canonical module. Old 0.5.x unguarded resources must be removed
from the resource list before reloading; loading both versions is unsupported.
Already open documents keep their loaded element until document reload. There is
no hot update: replace the whole package, restart Core, then reload each browser.
Entry reload applies options but cannot replace imported Python or frontend code.

Supported static routes last for the HA process. Entry disable/unload stops data
work and denies entry-owned commands; public code can remain until restart.
After package files are removed, static requests return 404. Removing the package
is separate from deleting the config entry. No private router-unregistration
hack is used. Entity IDs, entry version, selected series, event/request ledgers,
provider permissions, polling and household configuration are unchanged.

## Official requirements audit

Read on 2026-10-22, using official source snapshots (not assumptions about dual
HACS categories):

| Requirement | Evidence and candidate status |
| --- | --- |
| Exactly one integration; all runtime files underneath it | [HACS integration requirements](https://www.hacs.dev/docs/publish/integration/), [source snapshot](https://github.com/hacs/documentation/blob/4f06a5bd11088a21a453fdcb3eda1603353e6c8a/source/docs/publish/integration.md). The normal recursive Integration downloader includes nested `frontend/` and `brand/`. |
| Supported asynchronous static registration | [HA API announcement](https://developers.home-assistant.io/blog/2024/06/18/async_register_static_paths/). Uses `await hass.http.async_register_static_paths([StaticPathConfig(...)])`, not removed synchronous API. Actual Core 2026.10.2 tested. |
| Resource registration | [HA resource documentation](https://developers.home-assistant.io/docs/frontend/custom-ui/registering-resources/). Resources UI or existing YAML list, one-time manual setup. No private Lovelace storage access. |
| `hacs.json` | [Official configuration](https://www.hacs.dev/docs/publish/start/). Root file declares integration name, minimum HA 2026.10.2 and `content_in_root: false`. No dashboard category, `zip_release`, or obsolete `render_readme`. Normal repository layout is the download contract. |
| Manifest | Existing domain/name/codeowners/config flow/documentation/issues preserved; version 0.2.0, public `http` dependency. Local exporter rewrites documentation/issues for the explicitly selected future repository. Hassfest validates actual manifest/runtime. |
| Tags/releases and update tracking | [HACS publishing](https://www.hacs.dev/docs/publish/start/) and [Integration downloader source](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/custom_components/hacs/repositories/integration.py). The remote tag audit returned no tags. No release is created by this PR; the connector does not expose a release listing. Publish a real `v0.2.0` GitHub release only after approval; tags alone are not the release-based update channel. Each distribution update advances manifest version, even if only JS changes. |
| Public repository | [Official private-repository FAQ](https://www.hacs.dev/docs/faq/private_repositories/). This development repo is confirmed **private**, unarchived, default `main`. Private custom repositories are also unsupported. GitHub authentication does not remove this restriction. |
| Repository metadata | Public destination must have descriptive README/description/topics, issues enabled, recognized MIT license and correct reachable documentation/issues URLs. Root README/LICENSE exist here. The connected metadata response did not expose description/topics/issues/license recognition; these remain explicit public-destination preflight checks, not verified claims. |
| Local brand assets | [HA brand guidance](https://developers.home-assistant.io/docs/core/integration/brand_images/), [current HACS validator](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/custom_components/hacs/validate/brands.py). HA supports local assets since 2026.3; HACS accepts `brand/icon.png` before checking global Brands. Original geometric NRC monogram, PNG 256×256 plus SVG/provenance, generated by `scripts/build_brand.py`. No NASCAR media/font. No global Brands submission is required by this supported local route. Owner approval of original asset remains a publication gate. |
| HACS/Hassfest CI | Existing pinned wrappers retained; **brands ignore removed**. Official HACS action still skips private development because upstream rejects private repositories. A skip is not a pass. Exported public preview includes this validation workflow with no ignored checks. Hassfest and full code/browser suites run separately. |
| Default catalog vs custom repository | [HACS inclusion requirements](https://www.hacs.dev/docs/publish/include/). A public custom repository is the initial proposed adoption route after full validation/release. Default-catalog inclusion is a separate future submission requiring all current requirements and review. Neither is claimed complete. |

Additional inspected official snapshots: HA developer docs
`50b518898989b67bb76b69827f227aa6f0acd32a`, HACS action wrapper
`1ebf01c408f29afcb6406bd431bc98fd8cbb15aa`, Core 2026.10.2
`8d7fd8b68677c2585be36ec86043308f403875b8`.

## Distribution choice and publication gates

| Option | Tradeoff | Decision |
| --- | --- | --- |
| A. Separate future public distribution | Curated runtime/docs avoid exposing private development history and observational packages. Requires a second approved repository and explicit versioned export/publication. | Recommended, pending owner approval. One public Integration still installs both Python and JS. |
| B. Make existing repository public | Simplifies source/update identity but exposes all history and documentation, including files removed from HEAD. Requires independent privacy, rights and history review plus metadata fixes. | Possible only after separate explicit approval. Do not change visibility to pass a check. |
| C. Separate public dashboard plugin | Requires another public repository, install, version and compatibility/update boundary. Useful if the card later needs independent distribution. | Unnecessary for this supported bundled architecture. Manual approved private preview remains available, but is not HACS. No official private-HACS alternative was found. |

Before adoption, the owner must explicitly approve: the public destination and
curated export (or full-history visibility review for B), original asset/code
publication and exact release. Review third-party notices and keep MIT code
rights separate from NASCAR data access/redistribution. This PR grants no new
CF permission, terms acceptance or polling rights. Then verify public repository
metadata, run official HACS/Hassfest without ignores on that destination, review
the deterministic artifact, and explicitly authorize its versioned release.
Creating a public repository, publishing a tag/release and owner installation
are future actions; none is automatic or performed by this PR.

For a concrete future authorization, first review/merge this PR, then identify
the exact public `owner/repository` and explicitly approve creation/publication
of its reviewed exported files, original NRC asset and `v0.2.0` release. For B,
also explicitly approve exposing the existing repository's full history. Re-export
with that destination, review the resulting checksums and full public validator
results, and authorize that exact artifact/release before publication. After it
exists, the owner follows steps 1–10 in the migration guide to adopt through HACS.
PR approval alone is not authorization to publish or install on the owner's HA.

## Reproducible local preparation

```sh
# Prepared environment: source /workspace/.cloud-setup/nascar-race-center/activate.sh
npm --prefix frontend ci
npm --prefix frontend run build
npm --prefix frontend run check:bundle
python scripts/build_brand.py
python scripts/build_distribution.py \
  --repository rosslandgraf/ha-nascar-race-center \
  --output work/distribution-preview
sha256sum -c docs/HACS_PACKAGING_ARTIFACTS.sha256
```

Use a new output directory each time. This explicit repository argument is the
current **private** identity for inspection, not a claim it can be installed in
HACS. Re-export only after a future destination is approved: rewritten URLs
change manifest/archive checksums. The exporter has no network, install, GitHub,
visibility or publication operations. It allowlists runtime assets, excludes
development/observation data, rejects symlinks/unexpected files/damaged JS and
writes sorted `SHA256SUMS`, `DISTRIBUTION.json` (`published: false`) and a fixed
ZIP (sorted paths, timestamps 1980-01-01, 0644 permissions, pinned compression).
The ZIP is a preview/manual-install artifact; normal HACS uses the repository's
component tree, not an undocumented release ZIP arrangement.

CI builds a private preview artifact with read-only contents permission; no
workflow creates repositories, releases or tags. A future approved distribution
must commit the reviewed tree, run full official validation, publish the tested
version/hash and never rewrite an existing release in place. HACS download
tracking is distinct from HA config entries: explicitly choose/re-download a
release during manual adoption, verify installed version, then restart Core.

## Executed validation and limitations

Local checks on Python 3.14.8, HA 2026.10.2, Node 24.19 / npm 11.9:

| Check | Result |
| --- | --- |
| Full Python suite, including native HTTP, entry reload/unload, stable IDs and existing household automation smoke | **1,052 passed** (66.53 s). Nine bundled-frontend cases and five distribution cases added. The malformed-ledger test now scopes its storage double to the integration ledger instead of corrupting core HTTP storage. |
| Ruff / format | Passed, 167 Python files formatted. |
| mypy | Passed, 45 integration source files. |
| Hassfest | Passed against pinned Core 2026.10.2, one integration, zero invalid integrations. |
| Independent authenticated HA runtime/service smoke and config check | Passed (one runtime test; config checker exit 0). These are development environment checks, not physical owner acceptance. |
| Frontend lint / TypeScript / Vitest | Passed; **84 tests**. |
| Full Chromium / Firefox / WebKit | **183 passed** (61 per engine, 7.2 min), including all nine new packaging scenarios and existing snapshot/source/empty-state/accessibility checks. |
| Clean offline npm install/rebuild | All four bundled runtime files byte-for-byte identical. Original PNG/SVG regenerate identically. Two preview archives byte-for-byte identical. |
| Official HACS | **Blocked/skipped: private repository**, not a pass. No brands ignore remains. Public-destination metadata and full validation remain gates. |

Native tests cover exact artifact bytes/cache headers/304 behavior, private-source
404s, multiple clients, concurrent idempotent registration, preserved entity IDs
across reload/re-enable, unloaded-entry data denial, removed-file 404, damaged
optional bundles and deterministic HACS-layout extraction. Browser cases install
only a copied component tree into actual test-owned HA subprocesses, then check
module alias/multiple-client loading, same-URL upgrade/rollback after real process
restarts, and one-time manual resource migration with saved entry/title/series
and unrelated resource preserved. That migration regression also corrected the
initial selector display for a configured non-first series.

Artifacts: [complete installed-file SHA-256 manifest](HACS_PACKAGING_ARTIFACTS.sha256).
The card is **155,427 bytes**, gzip **38,871 bytes**, within unchanged 180,000 /
50,000-byte budgets. Its SHA-256 is
`24e89e3cddefdf66703679057e116cfb51bfa0c8c613b6ded9b3f7c4a73e2f94`.
The deterministic private preview for explicit repository identity
`rosslandgraf/ha-nascar-race-center` has ZIP SHA-256
`6fcbc6eb97f6556a3a6d0615c7daf0c9f4a837167a0f71a348b19b2b7716c89a`.
Changing the approved destination or exported files requires a new archive/hash;
these bytes are not a public release.
No NASCAR endpoint, owner provider/configuration/polling or Home Assistant
installation was touched. Test-only HA runtimes use copied component trees and
loopback HTTP; fictional dashboard data never enters the production bundle.
Actual public HACS download/update/uninstall UI, owner HA OS filesystem permissions,
companion/tablet cache behavior, physical migration/rollback and household soak
remain owner acceptance checks after approval. A test-owned localStorage resource
list models the documented one-time resource edit; tests do not mutate an owner's
Lovelace storage or claim to automate the HACS UI. Synthetic 0.6.1/legacy modules
exercise version transitions; they are not real releases or redistributed old
0.5.3 artifacts.

Hosted validation is linked from [PR #17](https://github.com/rosslandgraf/ha-nascar-race-center/pull/17).
Check that PR's latest-head results; local successes above do not imply a pending
hosted job has passed. Browser screenshots/measurements are retained as CI
artifacts; historical Phase 5C committed captures are preserved.
