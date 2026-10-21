import { afterEach, describe, expect, it, vi } from "vitest";
import { NascarRaceCenterCard } from "../src/card";
import { MockHass } from "../demo/mock";
const cards: NascarRaceCenterCard[] = [];
function create(entry = "FICTIONAL_ENTRY") {
  const hass = new MockHass(),
    card = new NascarRaceCenterCard();
  card.setConfig({
    type: "custom:nascar-race-center-card",
    ...(entry ? { entry_id: entry } : {}),
  });
  card.hass = hass;
  document.body.append(card);
  cards.push(card);
  return { hass, card };
}
async function settled(card: NascarRaceCenterCard) {
  await vi.waitFor(
    () => expect(card.shadowRoot?.textContent).toContain("Fictional 300"),
    { timeout: 3000 },
  );
  await card.updateComplete;
}
function click(card: NascarRaceCenterCard, text: string) {
  const button = [...card.shadowRoot!.querySelectorAll("button")].find(
    (b) => b.textContent?.trim() === text,
  );
  expect(button).toBeDefined();
  button!.click();
}
afterEach(() => {
  cards.splice(0).forEach((c) => c.remove());
  vi.restoreAllMocks();
});
describe("Lovelace lifecycle and independent card state", () => {
  it("validates configuration and registers picker/sizing/editor APIs", () => {
    const card = new NascarRaceCenterCard();
    expect(() =>
      card.setConfig({ type: "custom:nascar-race-center-card", series_id: 99 }),
    ).toThrow();
    expect(() =>
      card.setConfig({ type: "custom:nascar-race-center-card", entry_id: "" }),
    ).toThrow();
    expect(card.getGridOptions().columns).toBe("full");
    expect(card.getCardSize()).toBeGreaterThan(0);
    expect(NascarRaceCenterCard.getConfigElement().tagName).toContain("EDITOR");
  });
  it("discovers entries explicitly and saves a selection without inferring entity IDs", async () => {
    const { card, hass } = create("");
    await vi.waitFor(() =>
      expect(card.shadowRoot?.textContent).toContain("Fictional offline entry"),
    );
    const select = card.shadowRoot!.querySelector(
      "main select",
    ) as HTMLSelectElement;
    select.value = "FICTIONAL_ENTRY";
    select.dispatchEvent(new Event("change"));
    await settled(card);
    expect(hass.requests[0].type).toBe("config_entries/get");
  });
  it("shows admin-only access denial with no data requests", async () => {
    const { card, hass } = create();
    hass.user.is_admin = false;
    card.hass = { ...hass, callWS: hass.callWS.bind(hass) };
    await vi.waitFor(() =>
      expect(card.shadowRoot?.textContent).toContain(
        "Administrator access is required",
      ),
    );
    expect(hass.requests).toHaveLength(0);
  });
  it("highlights favorites and subscribes without entity update rerenders", async () => {
    const { card, hass } = create();
    await settled(card);
    click(card, "Live Timing");
    await card.updateComplete;
    const tower = card.shadowRoot!.querySelector("nrc-leaderboard")!;
    await (tower as unknown as { updateComplete: Promise<boolean> })
      .updateComplete;
    expect(tower.shadowRoot!.querySelectorAll(".favorite-row")).toHaveLength(1);
    const updates = vi.spyOn(card, "requestUpdate");
    card.hass = { ...hass, callWS: hass.callWS.bind(hass) };
    expect(updates).not.toHaveBeenCalled();
    expect(hass.connection.callbacks.size).toBe(1);
  });
  it("releases subscriptions outside live tabs and on disconnect", async () => {
    const { card, hass } = create();
    await settled(card);
    click(card, "History");
    await vi.waitFor(() => expect(hass.connection.callbacks.size).toBe(0));
    click(card, "Race Center");
    await vi.waitFor(() => expect(hass.connection.callbacks.size).toBe(1));
    card.remove();
    await vi.waitFor(() => expect(hass.connection.callbacks.size).toBe(0));
    expect(
      [...hass.connection.listeners.values()].every((v) => v.size === 0),
    ).toBe(true);
  });
  it("switches series without retaining old standings", async () => {
    const { card, hass } = create();
    await settled(card);
    const select = card.shadowRoot!.querySelector(
      "select",
    ) as HTMLSelectElement;
    select.value = "2";
    select.dispatchEvent(new Event("change"));
    await vi.waitFor(() =>
      expect(hass.connection.requests.at(-1)?.series_id).toBe(2),
    );
    await vi.waitFor(() =>
      expect(card.shadowRoot?.textContent).toContain("not reported"),
    );
    expect(card.shadowRoot?.textContent).not.toContain("Fictional 300");
    expect(hass.connection.callbacks.size).toBe(1);
  });
  it("handles race/session transitions and freshness updates", async () => {
    const { card, hass } = create();
    await settled(card);
    hass.connection.push({
      session: {
        ...hass.connection.live(1).data.session!,
        run_name: "Fictional qualifying",
        status: "qualifying",
      },
    });
    await vi.waitFor(() =>
      expect(card.shadowRoot?.textContent).toContain("Fictional qualifying"),
    );
    hass.connection.availability = "stale";
    hass.connection.push();
    await vi.waitFor(() =>
      expect(card.shadowRoot?.textContent).toContain("Stale · timing withheld"),
    );
    expect(card.shadowRoot?.textContent).not.toContain("Fictional qualifying");
  });
  it("reboots from bootstrap after connection recovery", async () => {
    const { card, hass } = create();
    await settled(card);
    hass.connection.emit("disconnected");
    await vi.waitFor(() => expect(hass.connection.callbacks.size).toBe(0));
    hass.connection.emit("ready");
    await settled(card);
    expect(
      hass.requests.filter((r) => String(r.type).endsWith("/bootstrap")),
    ).toHaveLength(2);
    expect(hass.connection.callbacks.size).toBe(1);
  });
  it("keeps two card instances independent", async () => {
    const a = create(),
      b = create();
    b.card.hass = a.hass;
    await Promise.all([settled(a.card), settled(b.card)]);
    click(a.card, "History");
    await vi.waitFor(() => expect(a.hass.connection.callbacks.size).toBe(1));
    expect(a.hass.connection.callbacks.size).toBe(1);
    expect(
      b.card.shadowRoot!.querySelector("[aria-current=page]")?.textContent,
    ).toContain("Race Center");
  });
  it("cleans up delayed subscription acknowledgements after removal", async () => {
    const { card, hass } = create();
    hass.connection.delay = 100;
    await vi.waitFor(() => expect(hass.connection.requests).toHaveLength(1));
    card.remove();
    await vi.waitFor(() => expect(hass.connection.callbacks.size).toBe(0));
  });
  it("ignores callbacks from an old series after rapid switching", async () => {
    const { card, hass } = create();
    await settled(card);
    const old = [...hass.connection.callbacks.values()][0].callback;
    const wire = hass.connection.live(1);
    const select = card.shadowRoot!.querySelector(
      "select",
    ) as HTMLSelectElement;
    select.value = "2";
    select.dispatchEvent(new Event("change"));
    await vi.waitFor(() =>
      expect(hass.connection.requests.at(-1)?.series_id).toBe(2),
    );
    old(wire);
    await card.updateComplete;
    expect(card.shadowRoot?.textContent).not.toContain("Fictional 300");
    expect(hass.connection.callbacks.size).toBe(1);
  });
});
