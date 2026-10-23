# NASCAR Race Center

A Home Assistant custom integration with its bundled Lovelace dashboard. One
HACS **Integration** installation manages both Python and the compiled card.
Requires Home Assistant Core 2026.10.2 or newer; this candidate is integration
0.2.1 / card 0.6.1. Code and original NRC icon: MIT; bundled Lit notices are
included. This independent project is not endorsed by NASCAR.

This is a distribution preview until its owner approves public publication,
branding, privacy and source/data-use boundaries. A private repository cannot
be installed through HACS, including Custom repositories. Do not add NASCAR
credentials or treat code publication as permission to collect/distribute data.

After an approved public repository and reviewed release exist, add that repository
in HACS → Custom repositories, category **Integration**, and download the approved
version. Restart Core after updates. Keep the existing NASCAR config entry,
selected series, favorites, entity IDs and dashboard. Do not create a replacement
entry. HACS package tracking and HA integration configuration are separate.

Register exactly one **JavaScript Module** resource:
`/nascar_race_center/card.js`. For an existing manual installation, edit the old
NASCAR `/local/...` resource to this URL once, preserving all unrelated resources
and card settings. Close/reload browser documents after updating. Future updates
need no JavaScript copying or resource URL changes. An already open browser does
not hot-replace custom elements; restart/reload is part of the update procedure.

See [migration, updates, uninstall and rollback](UPGRADE.md). The compiled module
and its compatible version/hash are inside `custom_components/nascar_race_center/frontend/`.
HACS uses the normal integration directory layout, not a second dashboard category
or a special release ZIP asset. Only public code is served; dashboard data still
uses the existing authenticated administrator WebSocket API.

Demonstration is offline and intentionally has no active real race. CF remains
experimental and requires separately established access/use/cadence permission.
The existing conservative 300-second floor is unchanged; it is not a promise of
five-minute refreshes or a NASCAR-approved rate. Live source behavior, standalone
scoring associations and data redistribution rights remain evidence gates.
See [data-use boundaries](DATA_USE.md).

Named UTC schedule fields accept offset-free UTC; generic local dates remain
unknown. Driver-name conflicts are isolated per NASCAR ID, and current O'Reilly
and legacy Xfinity slugs both map to series 2. Session-aware discovery respects
the same 300-second CF floor, user minimum, caching and backoff.
