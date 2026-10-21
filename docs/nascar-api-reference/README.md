# NASCAR API Reference Package

**Start with [START_HERE.md](START_HERE.md)** for the executive summary, all endpoint details, complete field dictionary, identifier relationships and implementation limits in one document.

28 supplied endpoint URLs tested anonymously. 25 returned JSON: 24 populated responses and one empty article envelope. Three Drive configuration URLs returned HTTP 403 MissingKey XML. See Documentation/manifest.json for exact capture times, statuses, source hashes and file provenance.

This package contains **value-redacted structural samples derived from real responses**, not raw NASCAR response fixtures. Redistribution permission for raw responses is unresolved. No source media, credentials or cookies are included. Every scalar in the structural JSON is replaced by a same-type placeholder; repeated array shapes are collapsed. Those placeholders are not NASCAR facts, date examples, valid identities or valid replay data. Do not commit them under tests/fixtures as original captures.

## Start here, Codex
1. Read Documentation/findings.md and compatibility_report.md, then endpoint_catalog.md.
2. Inspect schema_reference.md and machine-readable field_profiles.json for every observed path, type counts, null/empty counts, absent fields and string-format observations. Profiles inspect all source records, not just the first array element.
3. Use identifier_observations.json, observed_code_domains.json and verified_relationships.json for namespace and join evidence. These retain limited factual IDs/codes; media URLs and narrative payloads are excluded.
4. Review discrepancies.md before comparing the repository's existing models. The repository and its original synthetic schemas were not available in this run.
5. Implement tolerant provider-specific adapters. Preserve source shape and unknown values; check event context before combining feeds. Keep redacted samples out of production fallback logic.
6. Before claiming live validation, obtain permitted raw snapshots during known sessions and test timezones, flags, gaps, transitions, replay/deduplication, stale feeds, overlapping series and rollover. This archive supplies structural evidence, not production acceptance.

Documentation/source_brief.md is the complete supplied brief. Request evidence files contain safe selected response headers, curl results and hashes; Drive XML error files preserve exact denial text. Manifest source hashes describe private original responses, while checksums.sha256 describes distributed files. No original raw captures are included in the ZIP. No authenticated requests, retries, token discovery, media retrieval or project modifications were performed.
