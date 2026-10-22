import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
const license = `/*! NASCAR Race Center card 0.6.0
${readFileSync(new URL("./LICENSE", import.meta.url), "utf8")}
${readFileSync(new URL("./THIRD_PARTY_NOTICES.md", import.meta.url), "utf8")}
*/\n`;
export default defineConfig({
  plugins: [
    {
      name: "preserve-bundled-license-notices",
      generateBundle(_options, bundle) {
        for (const output of Object.values(bundle))
          if (output.type === "chunk") output.code = license + output.code;
      },
    },
  ],
  publicDir: "../custom_components/nascar_race_center/frontend",
  build: {
    outDir: "../custom_components/nascar_race_center/frontend",
    copyPublicDir: false,
    lib: {
      entry: "src/card.ts",
      formats: ["es"],
      fileName: () => "nascar-race-center-card-0.6.0.js",
    },
    target: "es2022",
    sourcemap: false,
    emptyOutDir: true,
  },
  server: { fs: { allow: [".."] } },
});
