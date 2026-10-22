/** Build-only metadata. The runtime serves only this reviewed integration tree. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, copyFileSync } from "node:fs";
const root = new URL(
  "../../custom_components/nascar_race_center/",
  import.meta.url,
);
const pkg = JSON.parse(
  readFileSync(new URL("../package.json", import.meta.url)),
);
const manifest = JSON.parse(readFileSync(new URL("manifest.json", root)));
const filename = `nascar-race-center-card-${pkg.version}.js`;
const sha256 = createHash("sha256")
  .update(readFileSync(new URL(`frontend/${filename}`, root)))
  .digest("hex");
writeFileSync(
  new URL("frontend/bundle.json", root),
  JSON.stringify(
    {
      integration_version: manifest.version,
      card_version: pkg.version,
      filename,
      sha256,
    },
    null,
    2,
  ) + "\n",
);
for (const name of ["LICENSE", "THIRD_PARTY_NOTICES.md"])
  copyFileSync(
    new URL(`../${name}`, import.meta.url),
    new URL(`frontend/${name}`, root),
  );
