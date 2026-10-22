# NASCAR Race Center card 0.5.3

Use integration **0.1.2** with this source-status update. See the
[owner upgrade/acceptance/rollback guide](../docs/CF_OWNER_ACCEPTANCE.md) and
[actual validation/evidence](../docs/CF_READINESS_VALIDATION.md). Merged snapshot
release and calm empty-state behavior remain supported. Real active CF sessions
remain an owner acceptance gate.

A local, independently built Lit custom Lovelace card for dashboard API v1.
Five connected views: Race Center, Live Timing, Race Weekend, History and Analytics.

See [configuration, manual installation and architecture](../docs/FRONTEND.md)
and [executed validation with actual-card screenshots](../docs/PHASE5C_VALIDATION.md).

```sh
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run check:bundle
# Local prepared environment has system Chromium:
NRC_BROWSERS=chromium npm run test:browser
# Full supported-engine matrix (also run by CI):
npx playwright install --with-deps chromium firefox webkit
CHROMIUM_PATH=bundled npm run test:browser
```

The versioned ES module is `dist/nascar-race-center-card-0.5.3.js`; Lit is included.
No runtime package installation, CDN, remote font or additional JS request.
`npm run dev` serves `/demo/`, a clearly fictional development-only contract
preview. `?bundle=true` exercises the committed production bundle. Neither the
preview adapter nor its test data is included in the production module.

This package is private development software. It does not publish, deploy,
register a resource, install into HA, or constitute a HACS dashboard plugin.
The integration's existing HACS packaging remains separate. MIT applies to code,
not NASCAR data, brands or media; no controlled assets are bundled.

Phase 5C extends the existing Lit components: card-local density, touch timing
columns, keyboard driver navigation, chart inspection, cached-page/selection reuse
and record-specific summaries. New English source labels live in `src/messages.ts`.
No backend contract or provider cadence changes. Test selectors should use named
controls: the masthead now has density and series selectors.

`NRC_BROWSERS` is an explicit comma-separated engine subset for environments that
cannot install every engine. Omission runs Chromium, Firefox and WebKit. Record
what actually ran; engine configuration alone is not validation evidence. To keep
downloads within the workspace use `PLAYWRIGHT_BROWSERS_PATH=../work/browsers` and
`npm ci --cache ../work/npm-cache`. The preview's `?loading=true` uses a delayed
fictional adapter only. Screenshots are browser-rendered into
`docs/screenshots/phase5c/<engine>/`; retained Phase 5B scenarios write fresh
comparison captures into ignored `work/phase5b-regression/`.
