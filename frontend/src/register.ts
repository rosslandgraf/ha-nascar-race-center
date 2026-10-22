/** Repeated supported resource aliases must never redefine global elements. */
export function defineOnce(
  name: string,
  constructor: CustomElementConstructor,
) {
  if (!customElements.get(name)) customElements.define(name, constructor);
}
