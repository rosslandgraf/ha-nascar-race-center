import { MockHass } from "./mock";
import type { NascarRaceCenterCard } from "../src/card";
import type { Section } from "../src/types";
const params = new URLSearchParams(location.search);
const resource =
  params.get("bundle") === "true"
    ? "/dist/nascar-race-center-card-0.5.0.js"
    : "/src/card.ts";
await import(/* @vite-ignore */ resource);
const Card = customElements.get("nascar-race-center-card")!;
const hass = new MockHass();
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
