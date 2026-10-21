# Fictional contract preview

This development-only adapter is excluded from the production bundle. All names,
measurements and race keys are fictional. `contract.json` is exported through the
actual Phase 5A HA WebSocket serializers and Phase 4B analytics function by
`tests/test_frontend_contract.py`. That test checks schema drift during Python CI.

Regenerate intentionally from the repository with the prepared environment:

```sh
NRC_EXPORT_FRONTEND=1 pytest -q tests/test_frontend_contract.py
cd frontend && npm run format
```

No NASCAR request is made. The browser mock applies 200-row pagination and uses
an arbitrary fixed synthetic token; production uses the actual connection-bound
server token. Preview analytics is deliberately restricted to the exported
2024 / 88001 / drivers 99002,99003 / laps 1–48 / window 5 / all_available / all
seven datasets, so a chart never misrepresents a changed query. The preview
has a rich fictional live field, while the installed integration's offline
provider deliberately reports no active live session and empty lap observations.
The real card supports both, with explicit empty states.
