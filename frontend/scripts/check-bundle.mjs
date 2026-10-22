import { readFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
const filename = new URL(
  "../dist/nascar-race-center-card-0.5.3.js",
  import.meta.url,
);
const bundle = readFileSync(filename);
const text = bundle.toString();
if (bundle.length > 180000 || gzipSync(bundle).length > 50000)
  throw new Error("Bundle exceeds the Phase 5B transfer budget");
if (
  /FICTIONAL_ENTRY|Fictional Driver|fictional contract preview|https:\/\/cf\.nascar\.com/i.test(
    text,
  )
)
  throw new Error(
    "Test data or provider URL leaked into the production bundle",
  );
if (/\bimport\s*\(|\bimport\s*[{*]/.test(text))
  throw new Error("Runtime module download found");
console.log(
  JSON.stringify({
    file: filename.pathname,
    bytes: bundle.length,
    gzip_bytes: gzipSync(bundle).length,
  }),
);

if (
  !text.includes("MIT License") ||
  !text.includes("BSD 3-Clause License") ||
  !text.includes("Copyright (c) 2026 Ross Landgraf")
)
  throw new Error("Missing bundled license notices");
