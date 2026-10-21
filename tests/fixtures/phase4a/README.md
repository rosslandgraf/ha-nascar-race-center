# Phase 4A structural fixtures

All seven JSON files are handmade, minimal, **fictional** examples. No original
NASCAR response was collected or copied. Field casing/nesting comes from supplied
observed profiles 13–19 in `docs/nascar-api-reference/Documentation/field_profiles.json`.
IDs 88001/99002/77001/70001, names, dates and measurements are invented test data.
The run IDs deliberately differ across namespaces. Car strings retain leading
zeros. Unknown flag/run codes, lap-zero nulls, repeated note driver references,
missing averages, 999/null rank and -1/zero pit candidates exercise conservative
semantics, not verified sentinel definitions. Fixtures are never a runtime source.

Tests explicitly mutate season/series/identity and malformed values to establish
software behavior across national series and years. Those cases do not establish
real cross-context endpoint coverage, finality, units or data-use permission.
