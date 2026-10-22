import { MockHass } from "./mock";
import type { NascarRaceCenterCard } from "../src/card";
import type { Section } from "../src/types";
const params = new URLSearchParams(location.search);
const resource =
  params.get("bundle") === "true"
    ? "/nascar-race-center-card-0.6.0.js"
    : "/src/card.ts";
if (params.get("bundle") === "true") {
  // Public artifacts must load as-is, without Vite source transforms.
  await new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.type = "module";
    script.src = resource;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Compiled preview failed to load"));
    document.head.append(script);
  });
} else await import(/* @vite-ignore */ resource);
const Card = customElements.get("nascar-race-center-card")!;
const hass = new MockHass();
if (params.get("loading") === "true") hass.delay = 2000;
const card = new Card() as NascarRaceCenterCard;
if (params.get("state")) hass.connection.availability = params.get("state")!;
if (params.get("admin") === "false") hass.user.is_admin = false;
performance.mark("nrc-mount");
card.setConfig({
  type: "custom:nascar-race-center-card",
  entry_id: params.get("entry") === "choose" ? undefined : "FICTIONAL_ENTRY",
  section: (params.get("section") ?? "Race Center") as Section,
});
card.hass = hass;
document.body.append(card);
void card.updateComplete.then(() =>
  performance.measure("nrc-first-render", "nrc-mount"),
);
(
  window as unknown as {
    nrcDemo: { hass: MockHass; card: NascarRaceCenterCard };
  }
).nrcDemo = { hass, card };
