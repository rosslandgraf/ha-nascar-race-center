# NASCAR Race Center card 0.5.0

A local, independently built Lit custom Lovelace card for dashboard API v1.
Five connected views: Race Center, Live Timing, Race Weekend, History and Analytics.

See [configuration, manual installation and architecture](../docs/FRONTEND.md)
and [executed validation with actual-card screenshots](../docs/PHASE5B_VALIDATION.md).

```sh
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run check:bundle
# Uses /usr/bin/chromium in the prepared cloud environment:
npm run test:browser
# Elsewhere:
npx playwright install chromium
CHROMIUM_PATH=bundled npm run test:browser
```

The versioned ES module is `dist/nascar-race-center-card-0.5.0.js`; Lit is included.
No runtime package installation, CDN, remote font or additional JS request.
`npm run dev` serves `/demo/`, a clearly fictional development-only contract
preview. `?bundle=true` exercises the committed production bundle. Neither the
preview adapter nor its test data is included in the production module.

This package is private development software. It does not publish, deploy,
register a resource, install into HA, or constitute a HACS dashboard plugin.
The integration's existing HACS packaging remains separate. MIT applies to code,
not NASCAR data, brands or media; no controlled assets are bundled.
