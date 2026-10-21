/*! NASCAR Race Center card 0.5.0
MIT License

Copyright (c) 2026 Ross Landgraf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Bundled third-party software

The runtime bundle includes Lit, lit-element, lit-html and @lit/reactive-element,
licensed under BSD-3-Clause. Their notices are included below and in the built
JavaScript license banner. Development-only dependency licenses remain in their
installed packages; those packages are not included in the runtime artifact.

## lit

BSD 3-Clause License

Copyright (c) 2017 Google LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## lit-element

BSD 3-Clause License

Copyright (c) 2017 Google LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## lit-html

BSD 3-Clause License

Copyright (c) 2017 Google LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## @lit/reactive-element

BSD 3-Clause License

Copyright (c) 2017 Google LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


*/
const K = globalThis, le = K.ShadowRoot && (K.ShadyCSS === void 0 || K.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, ce = Symbol(), ve = /* @__PURE__ */ new WeakMap();
let Te = class {
  constructor(e, t, s) {
    if (this._$cssResult$ = !0, s !== ce) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = t;
  }
  get styleSheet() {
    let e = this.o;
    const t = this.t;
    if (le && e === void 0) {
      const s = t !== void 0 && t.length === 1;
      s && (e = ve.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), s && ve.set(t, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Ve = (r) => new Te(typeof r == "string" ? r : r + "", void 0, ce), X = (r, ...e) => {
  const t = r.length === 1 ? r[0] : e.reduce((s, i, a) => s + ((n) => {
    if (n._$cssResult$ === !0) return n.cssText;
    if (typeof n == "number") return n;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + n + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(i) + r[a + 1], r[0]);
  return new Te(t, r, ce);
}, Je = (r, e) => {
  if (le) r.adoptedStyleSheets = e.map((t) => t instanceof CSSStyleSheet ? t : t.styleSheet);
  else for (const t of e) {
    const s = document.createElement("style"), i = K.litNonce;
    i !== void 0 && s.setAttribute("nonce", i), s.textContent = t.cssText, r.appendChild(s);
  }
}, me = le ? (r) => r : (r) => r instanceof CSSStyleSheet ? ((e) => {
  let t = "";
  for (const s of e.cssRules) t += s.cssText;
  return Ve(t);
})(r) : r;
const { is: Ge, defineProperty: Ke, getOwnPropertyDescriptor: Ze, getOwnPropertyNames: Ye, getOwnPropertySymbols: Xe, getPrototypeOf: Qe } = Object, Q = globalThis, ge = Q.trustedTypes, et = ge ? ge.emptyScript : "", tt = Q.reactiveElementPolyfillSupport, F = (r, e) => r, ae = { toAttribute(r, e) {
  switch (e) {
    case Boolean:
      r = r ? et : null;
      break;
    case Object:
    case Array:
      r = r == null ? r : JSON.stringify(r);
  }
  return r;
}, fromAttribute(r, e) {
  let t = r;
  switch (e) {
    case Boolean:
      t = r !== null;
      break;
    case Number:
      t = r === null ? null : Number(r);
      break;
    case Object:
    case Array:
      try {
        t = JSON.parse(r);
      } catch {
        t = null;
      }
  }
  return t;
} }, ze = (r, e) => !Ge(r, e), fe = { attribute: !0, type: String, converter: ae, reflect: !1, useDefault: !1, hasChanged: ze };
Symbol.metadata ??= Symbol("metadata"), Q.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
let P = class extends HTMLElement {
  static addInitializer(e) {
    this._$Ei(), (this.l ??= []).push(e);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(e, t = fe) {
    if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
      const s = Symbol(), i = this.getPropertyDescriptor(e, s, t);
      i !== void 0 && Ke(this.prototype, e, i);
    }
  }
  static getPropertyDescriptor(e, t, s) {
    const { get: i, set: a } = Ze(this.prototype, e) ?? { get() {
      return this[t];
    }, set(n) {
      this[t] = n;
    } };
    return { get: i, set(n) {
      const c = i?.call(this);
      a?.call(this, n), this.requestUpdate(e, c, s);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) ?? fe;
  }
  static _$Ei() {
    if (this.hasOwnProperty(F("elementProperties"))) return;
    const e = Qe(this);
    e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(F("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(F("properties"))) {
      const t = this.properties, s = [...Ye(t), ...Xe(t)];
      for (const i of s) this.createProperty(i, t[i]);
    }
    const e = this[Symbol.metadata];
    if (e !== null) {
      const t = litPropertyMetadata.get(e);
      if (t !== void 0) for (const [s, i] of t) this.elementProperties.set(s, i);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t, s] of this.elementProperties) {
      const i = this._$Eu(t, s);
      i !== void 0 && this._$Eh.set(i, t);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(e) {
    const t = [];
    if (Array.isArray(e)) {
      const s = new Set(e.flat(1 / 0).reverse());
      for (const i of s) t.unshift(me(i));
    } else e !== void 0 && t.push(me(e));
    return t;
  }
  static _$Eu(e, t) {
    const s = t.attribute;
    return s === !1 ? void 0 : typeof s == "string" ? s : typeof e == "string" ? e.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((e) => e(this));
  }
  addController(e) {
    (this._$EO ??= /* @__PURE__ */ new Set()).add(e), this.renderRoot !== void 0 && this.isConnected && e.hostConnected?.();
  }
  removeController(e) {
    this._$EO?.delete(e);
  }
  _$E_() {
    const e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
    for (const s of t.keys()) this.hasOwnProperty(s) && (e.set(s, this[s]), delete this[s]);
    e.size > 0 && (this._$Ep = e);
  }
  createRenderRoot() {
    const e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return Je(e, this.constructor.elementStyles), e;
  }
  connectedCallback() {
    this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(!0), this._$EO?.forEach((e) => e.hostConnected?.());
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((e) => e.hostDisconnected?.());
  }
  attributeChangedCallback(e, t, s) {
    this._$AK(e, s);
  }
  _$ET(e, t) {
    const s = this.constructor.elementProperties.get(e), i = this.constructor._$Eu(e, s);
    if (i !== void 0 && s.reflect === !0) {
      const a = (s.converter?.toAttribute !== void 0 ? s.converter : ae).toAttribute(t, s.type);
      this._$Em = e, a == null ? this.removeAttribute(i) : this.setAttribute(i, a), this._$Em = null;
    }
  }
  _$AK(e, t) {
    const s = this.constructor, i = s._$Eh.get(e);
    if (i !== void 0 && this._$Em !== i) {
      const a = s.getPropertyOptions(i), n = typeof a.converter == "function" ? { fromAttribute: a.converter } : a.converter?.fromAttribute !== void 0 ? a.converter : ae;
      this._$Em = i;
      const c = n.fromAttribute(t, a.type);
      this[i] = c ?? this._$Ej?.get(i) ?? c, this._$Em = null;
    }
  }
  requestUpdate(e, t, s, i = !1, a) {
    if (e !== void 0) {
      const n = this.constructor;
      if (i === !1 && (a = this[e]), s ??= n.getPropertyOptions(e), !((s.hasChanged ?? ze)(a, t) || s.useDefault && s.reflect && a === this._$Ej?.get(e) && !this.hasAttribute(n._$Eu(e, s)))) return;
      this.C(e, t, s);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(e, t, { useDefault: s, reflect: i, wrapped: a }, n) {
    s && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(e) && (this._$Ej.set(e, n ?? t ?? this[e]), a !== !0 || n !== void 0) || (this._$AL.has(e) || (this.hasUpdated || s || (t = void 0), this._$AL.set(e, t)), i === !0 && this._$Em !== e && (this._$Eq ??= /* @__PURE__ */ new Set()).add(e));
  }
  async _$EP() {
    this.isUpdatePending = !0;
    try {
      await this._$ES;
    } catch (t) {
      Promise.reject(t);
    }
    const e = this.scheduleUpdate();
    return e != null && await e, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
        for (const [i, a] of this._$Ep) this[i] = a;
        this._$Ep = void 0;
      }
      const s = this.constructor.elementProperties;
      if (s.size > 0) for (const [i, a] of s) {
        const { wrapped: n } = a, c = this[i];
        n !== !0 || this._$AL.has(i) || c === void 0 || this.C(i, void 0, a, c);
      }
    }
    let e = !1;
    const t = this._$AL;
    try {
      e = this.shouldUpdate(t), e ? (this.willUpdate(t), this._$EO?.forEach((s) => s.hostUpdate?.()), this.update(t)) : this._$EM();
    } catch (s) {
      throw e = !1, this._$EM(), s;
    }
    e && this._$AE(t);
  }
  willUpdate(e) {
  }
  _$AE(e) {
    this._$EO?.forEach((t) => t.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(e) {
    return !0;
  }
  update(e) {
    this._$Eq &&= this._$Eq.forEach((t) => this._$ET(t, this[t])), this._$EM();
  }
  updated(e) {
  }
  firstUpdated(e) {
  }
};
P.elementStyles = [], P.shadowRootOptions = { mode: "open" }, P[F("elementProperties")] = /* @__PURE__ */ new Map(), P[F("finalized")] = /* @__PURE__ */ new Map(), tt?.({ ReactiveElement: P }), (Q.reactiveElementVersions ??= []).push("2.1.2");
const de = globalThis, $e = (r) => r, Y = de.trustedTypes, be = Y ? Y.createPolicy("lit-html", { createHTML: (r) => r }) : void 0, Ie = "$lit$", A = `lit$${Math.random().toFixed(9).slice(2)}$`, Le = "?" + A, st = `<${Le}>`, D = document, B = () => D.createComment(""), W = (r) => r === null || typeof r != "object" && typeof r != "function", he = Array.isArray, it = (r) => he(r) || typeof r?.[Symbol.iterator] == "function", te = `[ 	
\f\r]`, q = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, ye = /-->/g, _e = />/g, S = RegExp(`>|${te}(?:([^\\s"'>=/]+)(${te}*=${te}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), xe = /'/g, we = /"/g, qe = /^(?:script|style|textarea|title)$/i, He = (r) => (e, ...t) => ({ _$litType$: r, strings: e, values: t }), l = He(1), T = He(2), N = Symbol.for("lit-noChange"), h = Symbol.for("lit-nothing"), Ae = /* @__PURE__ */ new WeakMap(), R = D.createTreeWalker(D, 129);
function Oe(r, e) {
  if (!he(r) || !r.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return be !== void 0 ? be.createHTML(e) : e;
}
const rt = (r, e) => {
  const t = r.length - 1, s = [];
  let i, a = e === 2 ? "<svg>" : e === 3 ? "<math>" : "", n = q;
  for (let c = 0; c < t; c++) {
    const o = r[c];
    let u, $, p = -1, d = 0;
    for (; d < o.length && (n.lastIndex = d, $ = n.exec(o), $ !== null); ) d = n.lastIndex, n === q ? $[1] === "!--" ? n = ye : $[1] !== void 0 ? n = _e : $[2] !== void 0 ? (qe.test($[2]) && (i = RegExp("</" + $[2], "g")), n = S) : $[3] !== void 0 && (n = S) : n === S ? $[0] === ">" ? (n = i ?? q, p = -1) : $[1] === void 0 ? p = -2 : (p = n.lastIndex - $[2].length, u = $[1], n = $[3] === void 0 ? S : $[3] === '"' ? we : xe) : n === we || n === xe ? n = S : n === ye || n === _e ? n = q : (n = S, i = void 0);
    const v = n === S && r[c + 1].startsWith("/>") ? " " : "";
    a += n === q ? o + st : p >= 0 ? (s.push(u), o.slice(0, p) + Ie + o.slice(p) + A + v) : o + A + (p === -2 ? c : v);
  }
  return [Oe(r, a + (r[t] || "<?>") + (e === 2 ? "</svg>" : e === 3 ? "</math>" : "")), s];
};
class j {
  constructor({ strings: e, _$litType$: t }, s) {
    let i;
    this.parts = [];
    let a = 0, n = 0;
    const c = e.length - 1, o = this.parts, [u, $] = rt(e, t);
    if (this.el = j.createElement(u, s), R.currentNode = this.el.content, t === 2 || t === 3) {
      const p = this.el.content.firstChild;
      p.replaceWith(...p.childNodes);
    }
    for (; (i = R.nextNode()) !== null && o.length < c; ) {
      if (i.nodeType === 1) {
        if (i.hasAttributes()) for (const p of i.getAttributeNames()) if (p.endsWith(Ie)) {
          const d = $[n++], v = i.getAttribute(p).split(A), g = /([.?@])?(.*)/.exec(d);
          o.push({ type: 1, index: a, name: g[2], strings: v, ctor: g[1] === "." ? nt : g[1] === "?" ? ot : g[1] === "@" ? lt : ee }), i.removeAttribute(p);
        } else p.startsWith(A) && (o.push({ type: 6, index: a }), i.removeAttribute(p));
        if (qe.test(i.tagName)) {
          const p = i.textContent.split(A), d = p.length - 1;
          if (d > 0) {
            i.textContent = Y ? Y.emptyScript : "";
            for (let v = 0; v < d; v++) i.append(p[v], B()), R.nextNode(), o.push({ type: 2, index: ++a });
            i.append(p[d], B());
          }
        }
      } else if (i.nodeType === 8) if (i.data === Le) o.push({ type: 2, index: a });
      else {
        let p = -1;
        for (; (p = i.data.indexOf(A, p + 1)) !== -1; ) o.push({ type: 7, index: a }), p += A.length - 1;
      }
      a++;
    }
  }
  static createElement(e, t) {
    const s = D.createElement("template");
    return s.innerHTML = e, s;
  }
}
function I(r, e, t = r, s) {
  if (e === N) return e;
  let i = s !== void 0 ? t._$Co?.[s] : t._$Cl;
  const a = W(e) ? void 0 : e._$litDirective$;
  return i?.constructor !== a && (i?._$AO?.(!1), a === void 0 ? i = void 0 : (i = new a(r), i._$AT(r, t, s)), s !== void 0 ? (t._$Co ??= [])[s] = i : t._$Cl = i), i !== void 0 && (e = I(r, i._$AS(r, e.values), i, s)), e;
}
class at {
  constructor(e, t) {
    this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(e) {
    const { el: { content: t }, parts: s } = this._$AD, i = (e?.creationScope ?? D).importNode(t, !0);
    R.currentNode = i;
    let a = R.nextNode(), n = 0, c = 0, o = s[0];
    for (; o !== void 0; ) {
      if (n === o.index) {
        let u;
        o.type === 2 ? u = new L(a, a.nextSibling, this, e) : o.type === 1 ? u = new o.ctor(a, o.name, o.strings, this, e) : o.type === 6 && (u = new ct(a, this, e)), this._$AV.push(u), o = s[++c];
      }
      n !== o?.index && (a = R.nextNode(), n++);
    }
    return R.currentNode = D, i;
  }
  p(e) {
    let t = 0;
    for (const s of this._$AV) s !== void 0 && (s.strings !== void 0 ? (s._$AI(e, s, t), t += s.strings.length - 2) : s._$AI(e[t])), t++;
  }
}
class L {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(e, t, s, i) {
    this.type = 2, this._$AH = h, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = s, this.options = i, this._$Cv = i?.isConnected ?? !0;
  }
  get parentNode() {
    let e = this._$AA.parentNode;
    const t = this._$AM;
    return t !== void 0 && e?.nodeType === 11 && (e = t.parentNode), e;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(e, t = this) {
    e = I(this, e, t), W(e) ? e === h || e == null || e === "" ? (this._$AH !== h && this._$AR(), this._$AH = h) : e !== this._$AH && e !== N && this._(e) : e._$litType$ !== void 0 ? this.$(e) : e.nodeType !== void 0 ? this.T(e) : it(e) ? this.k(e) : this._(e);
  }
  O(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  T(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
  }
  _(e) {
    this._$AH !== h && W(this._$AH) ? this._$AA.nextSibling.data = e : this.T(D.createTextNode(e)), this._$AH = e;
  }
  $(e) {
    const { values: t, _$litType$: s } = e, i = typeof s == "number" ? this._$AC(e) : (s.el === void 0 && (s.el = j.createElement(Oe(s.h, s.h[0]), this.options)), s);
    if (this._$AH?._$AD === i) this._$AH.p(t);
    else {
      const a = new at(i, this), n = a.u(this.options);
      a.p(t), this.T(n), this._$AH = a;
    }
  }
  _$AC(e) {
    let t = Ae.get(e.strings);
    return t === void 0 && Ae.set(e.strings, t = new j(e)), t;
  }
  k(e) {
    he(this._$AH) || (this._$AH = [], this._$AR());
    const t = this._$AH;
    let s, i = 0;
    for (const a of e) i === t.length ? t.push(s = new L(this.O(B()), this.O(B()), this, this.options)) : s = t[i], s._$AI(a), i++;
    i < t.length && (this._$AR(s && s._$AB.nextSibling, i), t.length = i);
  }
  _$AR(e = this._$AA.nextSibling, t) {
    for (this._$AP?.(!1, !0, t); e !== this._$AB; ) {
      const s = $e(e).nextSibling;
      $e(e).remove(), e = s;
    }
  }
  setConnected(e) {
    this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
  }
}
class ee {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(e, t, s, i, a) {
    this.type = 1, this._$AH = h, this._$AN = void 0, this.element = e, this.name = t, this._$AM = i, this.options = a, s.length > 2 || s[0] !== "" || s[1] !== "" ? (this._$AH = Array(s.length - 1).fill(new String()), this.strings = s) : this._$AH = h;
  }
  _$AI(e, t = this, s, i) {
    const a = this.strings;
    let n = !1;
    if (a === void 0) e = I(this, e, t, 0), n = !W(e) || e !== this._$AH && e !== N, n && (this._$AH = e);
    else {
      const c = e;
      let o, u;
      for (e = a[0], o = 0; o < a.length - 1; o++) u = I(this, c[s + o], t, o), u === N && (u = this._$AH[o]), n ||= !W(u) || u !== this._$AH[o], u === h ? e = h : e !== h && (e += (u ?? "") + a[o + 1]), this._$AH[o] = u;
    }
    n && !i && this.j(e);
  }
  j(e) {
    e === h ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class nt extends ee {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === h ? void 0 : e;
  }
}
class ot extends ee {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    this.element.toggleAttribute(this.name, !!e && e !== h);
  }
}
class lt extends ee {
  constructor(e, t, s, i, a) {
    super(e, t, s, i, a), this.type = 5;
  }
  _$AI(e, t = this) {
    if ((e = I(this, e, t, 0) ?? h) === N) return;
    const s = this._$AH, i = e === h && s !== h || e.capture !== s.capture || e.once !== s.once || e.passive !== s.passive, a = e !== h && (s === h || i);
    i && this.element.removeEventListener(this.name, this, s), a && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
  }
}
class ct {
  constructor(e, t, s) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = s;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    I(this, e);
  }
}
const dt = { I: L }, ht = de.litHtmlPolyfillSupport;
ht?.(j, L), (de.litHtmlVersions ??= []).push("3.3.3");
const pt = (r, e, t) => {
  const s = t?.renderBefore ?? e;
  let i = s._$litPart$;
  if (i === void 0) {
    const a = t?.renderBefore ?? null;
    s._$litPart$ = i = new L(e.insertBefore(B(), a), a, void 0, t ?? {});
  }
  return i._$AI(r), i;
};
const pe = globalThis;
let w = class extends P {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    const e = super.createRenderRoot();
    return this.renderOptions.renderBefore ??= e.firstChild, e;
  }
  update(e) {
    const t = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = pt(t, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    super.connectedCallback(), this._$Do?.setConnected(!0);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._$Do?.setConnected(!1);
  }
  render() {
    return N;
  }
};
w._$litElement$ = !0, w.finalized = !0, pe.litElementHydrateSupport?.({ LitElement: w });
const ut = pe.litElementPolyfillSupport;
ut?.({ LitElement: w });
(pe.litElementVersions ??= []).push("4.2.2");
const ne = [
  "Race Center",
  "Live Timing",
  "Race Weekend",
  "History",
  "Analytics"
], U = {
  1: "Cup Series",
  2: "National Series 2",
  3: "Truck Series"
}, ke = [
  "weekend",
  "laps",
  "notes",
  "loop",
  "averages",
  "pits",
  "stages"
], vt = "nascar_race_center/dashboard/";
class y extends Error {
  constructor(e, t) {
    super(t || e), this.code = e, this.name = "DashboardError";
  }
}
function Fe(r) {
  return typeof r == "object" && r !== null && "code" in r ? String(r.code) : "connection_error";
}
const mt = {
  unauthorized: "Administrator access is required for dashboard API v1. Sign in with an administrator account.",
  entry_unavailable: "This integration entry is missing, unloaded, or restarting. Select a loaded NASCAR Race Center entry, then reconnect.",
  invalid_format: "The request or API version is unsupported. Card 0.5 requires dashboard API v1 (Phase 5A).",
  api_version: "Incompatible dashboard API. Card 0.5 requires API v1.",
  unknown_command: "Dashboard API is unavailable. Install the Phase 5A integration or newer API v1 implementation.",
  snapshot_expired: "This five-minute selection expired. Restart the selection to load a new snapshot.",
  snapshot_invalid: "The snapshot is no longer valid on this connection. Restart the selection.",
  snapshot_changed: "The source changed while paging. Restart the selection to avoid mixing records.",
  snapshot_limit: "Snapshot capacity is in use (two per user, four globally). Reuse an open selection or wait up to five minutes before retrying.",
  request_limit: "Too many simultaneous requests. Wait for the current request to finish, then retry.",
  rate_limited: "Request limit reached. Wait at least 10 seconds, then retry.",
  invalid_selection: "The selection is invalid or the series is not monitored by this entry.",
  invalid_response: "The API response did not match the documented v1 shape.",
  unsafe_identifier: "This identifier cannot be sent losslessly as a JavaScript integer.",
  connection_error: "Connection interrupted. Reconnect to Home Assistant or retry.",
  retention_limit: "Client retention limit reached. Use the next page to view more records."
};
function Be(r) {
  const e = Fe(r);
  return mt[e] || `Data unavailable (${e.replaceAll("_", " ")}). Narrow the selection or retry.`;
}
function J(r, e = 1e10) {
  if (!/^\d+$/.test(r) || BigInt(r) < 1n || BigInt(r) > BigInt(e) || BigInt(r) > BigInt(Number.MAX_SAFE_INTEGER))
    throw new y("unsafe_identifier");
  return Number(r);
}
function H(r) {
  return typeof r == "object" && r !== null && !Array.isArray(r);
}
function Se(r, e) {
  if (H(r) && r.type === "result") {
    if (r.success === !1)
      throw new y(
        H(r.error) ? String(r.error.code) : "invalid_response"
      );
    r = r.result;
  } else H(r) && r.type === "event" && (r = r.event);
  if (!H(r) || r.api_version !== 1)
    throw new y("api_version");
  if (r.entry_id !== e || !H(r.data))
    throw new y("invalid_response");
  return r;
}
function Ce(r, e) {
  if (r.identity?.series_id !== e || typeof r.availability != "string" || r.leaderboard !== null && (!Array.isArray(r.leaderboard) || r.leaderboard.length > 100 || r.leaderboard.some((t) => typeof t.driver_id != "string")))
    throw new y("invalid_response");
  return r.availability === "ok" && r.stale === !1 ? r : { ...r, session: null, leaderboard: null, leader_driver_id: null };
}
const Ee = /* @__PURE__ */ new WeakMap();
function gt(r, e) {
  let t = Ee.get(r);
  t || (t = /* @__PURE__ */ new Map(), Ee.set(r, t));
  let s = t.get(e);
  return s || (s = { tail: Promise.resolve(), last: 0 }, t.set(e, s)), s;
}
class ft {
  constructor(e, t, s = () => !0) {
    this.hass = e, this.entry = t, this.active = s, this.controller = new AbortController();
  }
  dispose() {
    this.controller.abort();
  }
  async paced(e) {
    const t = gt(this.hass.connection, this.entry), s = t.tail.then(async () => {
      const i = Math.max(0, 370 - (Date.now() - t.last));
      if (this.controller.signal.aborted)
        throw new y("connection_error");
      if (i && await new Promise((a, n) => {
        const c = () => {
          clearTimeout(o), n(new y("connection_error"));
        }, o = setTimeout(() => {
          this.controller.signal.removeEventListener("abort", c), a();
        }, i);
        this.controller.signal.addEventListener("abort", c, {
          once: !0
        });
      }), this.controller.signal.aborted || !this.active())
        throw new y("connection_error");
      return t.last = Date.now(), e();
    });
    return t.tail = s.then(
      () => {
      },
      () => {
      }
    ), s;
  }
  message(e, t = {}) {
    return {
      type: vt + e,
      entry_id: this.entry,
      api_version: 1,
      ...t
    };
  }
  async request(e, t = {}) {
    const s = await this.paced(
      () => this.hass.callWS(this.message(e, t))
    );
    return Se(s, this.entry).data;
  }
  async bootstrap() {
    const e = await this.request("bootstrap");
    if (!Array.isArray(e.series_ids) || !e.series_ids.length || e.series_ids.some((t) => ![1, 2, 3].includes(t)) || !Array.isArray(e.favorite_driver_ids) || e.favorite_driver_ids.some((t) => typeof t != "string") || !e.references || !Array.isArray(e.references.drivers) || !Array.isArray(e.references.tracks) || !Array.isArray(e.navigation) || !Array.isArray(e.upcoming) || !Array.isArray(e.source_state))
      throw new y("invalid_response");
    return e;
  }
  async live(e) {
    return Ce(
      await this.request("live", { series_id: e }),
      e
    );
  }
  async subscribe(e, t, s) {
    let i = 0;
    return this.paced(
      () => this.hass.connection.subscribeMessage(
        (a) => {
          try {
            const n = Se(a, this.entry), c = n.revision ?? n.data.revision;
            if (c !== void 0 && c <= i) return;
            if (n.data.availability === "entry_unavailable")
              throw new y("entry_unavailable");
            const o = Ce(n.data, e);
            i = c ?? i + 1, t(o);
          } catch (n) {
            s(n);
          }
        },
        this.message("subscribe_live", { series_id: e })
      )
    );
  }
  async page(e, t, s = 0, i) {
    const a = await this.request(e, {
      ...t,
      offset: s,
      limit: 200,
      ...i ? { snapshot: i } : {}
    });
    if (e === "analytics" && a.contract_version !== 1)
      throw new y("api_version");
    const n = e === "history" ? a.race : e === "analytics" ? a.query?.key : void 0;
    if ((e === "history" || e === "analytics") && (!n || n.series_id !== t.series_id || n.season !== t.season || n.race_id !== String(t.race_id)))
      throw new y("invalid_response");
    const c = a.pagination;
    if (!c || c.offset !== s || !Array.isArray(a.records) || a.records.length > 200 || c.returned !== a.records.length || !/^([a-f0-9]{64})$/.test(c.snapshot) || !Number.isInteger(c.total) || c.total < s + a.records.length || i && c.snapshot !== i || c.next_offset !== null && (c.next_offset !== s + a.records.length || c.next_offset <= s) || c.complete !== (c.next_offset === null))
      throw new y("invalid_response");
    return (e === "live_driver" || e === "live_scoring") && (a.records = a.records.map((o) => ({ ...o, kind: "detail" }))), a;
  }
  schedule(e, t = 0, s) {
    return this.page("schedule", e, t, s);
  }
  history(e, t = 0, s) {
    return this.page("history", e, t, s);
  }
  analytics(e, t = 0, s) {
    return this.page("analytics", e, t, s);
  }
  liveDriver(e, t = 0, s) {
    return this.page("live_driver", e, t, s);
  }
  liveScoring(e, t = 0, s) {
    return this.page("live_scoring", e, t, s);
  }
}
async function We(r) {
  const e = await r.callWS({
    type: "config_entries/get",
    domain: "nascar_race_center"
  });
  if (!Array.isArray(e)) throw new y("invalid_response");
  return e.filter((t) => t.domain === "nascar_race_center");
}
const m = (r) => r ? r.replaceAll("_", " ") : "Unknown";
function b(r, e, t = 0) {
  return typeof r == "number" && Number.isFinite(r) ? new Intl.NumberFormat(e === "none" ? "en-US" : e, {
    useGrouping: e !== "none",
    maximumFractionDigits: t
  }).format(r) : "—";
}
function M(r) {
  if (!r || !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)$/.test(
    r
  ))
    return null;
  const e = Date.parse(r);
  return Number.isFinite(e) ? e : null;
}
function E(r, e) {
  const t = M(r);
  return t === null ? "Time unconfirmed" : new Intl.DateTimeFormat(e?.locale?.language, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: e?.config?.time_zone,
    ...e?.locale?.time_format === "12" ? { hour12: !0 } : e?.locale?.time_format === "24" ? { hour12: !1 } : {}
  }).format(t);
}
function $t(r, e = Date.now()) {
  const t = M(r);
  if (t === null || t <= e) return null;
  const s = Math.ceil((t - e) / 6e4);
  return s >= 1440 ? `${Math.floor(s / 1440)}d ${Math.floor(s % 1440 / 60)}h` : `${Math.floor(s / 60)}h ${s % 60}m`;
}
function se(r) {
  const e = r?.availability;
  return e === "ok" && r?.stale === !1 ? { text: "Fresh source", tone: "green" } : e === "stale" || r?.stale === !0 ? { text: "Stale · timing withheld", tone: "yellow" } : e === "freshness_unknown" ? { text: "Freshness unknown", tone: "yellow" } : { text: e ? m(e) : "Awaiting source", tone: "neutral" };
}
function Re(r) {
  const e = {
    green: "green",
    yellow: "yellow",
    red: "red",
    white: "white",
    checkered: "checkered"
  }, t = r?.session?.flag;
  return t && e[t] ? { text: m(t), tone: e[t] } : {
    text: r?.session?.flag_state_code != null ? `Unknown flag (${r.session.flag_state_code})` : "Flag unreported",
    tone: "neutral"
  };
}
function bt(r, e, t = !1) {
  return r.map((s, i) => ({ row: s, index: i })).sort((s, i) => {
    const a = e === "position_change" ? s.row.position_change.value : s.row[e], n = e === "position_change" ? i.row.position_change.value : i.row[e];
    if (a == null && n == null) return s.index - i.index;
    if (a == null) return 1;
    if (n == null) return -1;
    const c = typeof a == "number" && typeof n == "number" ? a - n : typeof a == "boolean" && typeof n == "boolean" ? Number(a) - Number(n) : String(a).localeCompare(String(n), void 0, { numeric: !0 });
    return (t ? -c : c) || s.index - i.index;
  }).map((s) => s.row);
}
function yt(r) {
  return r.unit.includes("unverified") ? "source unit · unverified" : m(r.unit);
}
function Z(r) {
  const e = r?.locale?.number_format;
  return e === "none" ? "none" : e === "comma_decimal" ? "en-US" : e === "decimal_comma" ? "de-DE" : e === "space_comma" ? "fr-FR" : e === "system" ? void 0 : r?.locale?.language;
}
class ie {
  constructor(e, t, s) {
    this.command = e, this.selection = t, this.expectedLive = s, this.pages = /* @__PURE__ */ new Map(), this.loading = !1, this.created = 0, this.generation = 0, this.previousOffsets = [];
  }
  get records() {
    return [...this.pages.values()].sort((e, t) => e.pagination.offset - t.pagination.offset).flatMap((e) => e.records);
  }
  get expired() {
    return !!this.created && ["history", "analytics"].includes(this.command) && Date.now() - this.created >= 3e5;
  }
  get canPrevious() {
    return this.previousOffsets.length > 0;
  }
  invalidate() {
    this.generation++, this.loading = !1, this.pages.clear(), this.current = void 0, this.created = 0, this.previousOffsets = [], this.error = void 0;
  }
  async load(e, t = 0, s = !1) {
    if (this.loading) return;
    s && this.invalidate();
    const i = this.generation;
    if (this.expired) {
      this.error = new y("snapshot_expired");
      return;
    }
    const a = this.pages.get(t);
    if (a) {
      this.current = a, this.error = void 0;
      return;
    }
    this.loading = !0, this.error = void 0;
    try {
      const n = await e.page(
        this.command,
        this.selection,
        t,
        this.current?.pagination.snapshot
      );
      if (i !== this.generation) return;
      if (this.expectedLive && (n.identity?.series_id !== this.selection.series_id || n.identity?.race_id !== this.expectedLive.race_id || n.identity?.run_id !== this.expectedLive.run_id))
        throw new y("snapshot_changed");
      for (this.created || (this.created = Date.now()), this.pages.set(t, n), this.current = n; this.pages.size > 8; )
        this.pages.delete(this.pages.keys().next().value);
    } catch (n) {
      i === this.generation && (Fe(n) === "snapshot_changed" && (this.pages.clear(), this.current = void 0, this.previousOffsets = [], this.created = 0), this.error = n);
    } finally {
      i === this.generation && (this.loading = !1);
    }
  }
  async next(e) {
    const t = this.current?.pagination;
    if (!t || t.next_offset === null) return;
    const s = t.offset;
    await this.load(e, t.next_offset), this.current?.pagination.offset !== s && this.previousOffsets.push(s);
  }
  async previous(e) {
    const t = this.previousOffsets.at(-1);
    t !== void 0 && (await this.load(e, t), this.current?.pagination.offset === t && this.previousOffsets.pop());
  }
}
const V = X`
  :host {
    display: block;
    container-type: inline-size;
    color: var(--primary-text-color, #e8edf2);
    --nrc-accent: var(--accent-color, #a8ef75);
    --nrc-muted: var(--secondary-text-color, #a8b3bf);
    --nrc-base: var(
      --ha-card-background,
      var(--card-background-color, #151b23)
    );
    --nrc-panel: color-mix(in srgb, var(--nrc-base), white 3%);
    --nrc-line: color-mix(
      in srgb,
      var(--primary-text-color, #e8edf2),
      transparent 86%
    );
    font: 14px/1.5
      var(
        --paper-font-body1_-_font-family,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif
      );
    font-variant-numeric: tabular-nums;
  }
  * {
    box-sizing: border-box;
  }
  ha-card {
    display: block;
    overflow: hidden;
    background: var(--nrc-base);
    border: 1px solid var(--nrc-line);
    border-radius: var(--ha-card-border-radius, 20px);
    box-shadow: var(--ha-card-box-shadow, 0 18px 60px #0003);
  }
  button,
  input,
  select {
    font: inherit;
    color: inherit;
  }
  button,
  select,
  input {
    border: 1px solid var(--nrc-line);
    border-radius: 8px;
    background: var(--nrc-panel);
    padding: 9px 12px;
    min-height: 44px;
  }
  button {
    cursor: pointer;
    transition:
      background 0.15s,
      color 0.15s;
  }
  button:hover {
    background: color-mix(in srgb, var(--nrc-accent), transparent 88%);
  }
  button:disabled {
    cursor: default;
    opacity: 0.5;
  }
  button.primary {
    background: var(--nrc-accent);
    color: #15200e;
    border-color: var(--nrc-accent);
    font-weight: 700;
  }
  button.quiet {
    background: transparent;
  }
  input {
    min-width: 0;
    max-width: 100%;
  }
  select {
    max-width: 100%;
  }
  a {
    color: var(--nrc-accent);
  }
  :focus-visible {
    outline: 3px solid var(--primary-text-color, #e8edf2);
    outline-offset: 3px;
  }
  h1,
  h2,
  h3,
  p {
    margin: 0;
  }
  h1 {
    font-size: clamp(30px, 4cqi, 52px);
    letter-spacing: -0.045em;
    line-height: 1.1;
    font-weight: 750;
  }
  h2 {
    font-size: 22px;
    letter-spacing: -0.025em;
    line-height: 1.2;
  }
  h3 {
    font-size: 16px;
  }
  small,
  .muted {
    color: var(--nrc-muted);
  }
  small {
    font-size: 12px;
  }
  strong {
    font-weight: 700;
  }
  .eyebrow {
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--nrc-muted);
  }
  .masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 22px 28px;
    border-bottom: 1px solid var(--nrc-line);
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .brand-mark {
    display: grid;
    grid-template-columns: repeat(3, 5px);
    gap: 3px;
    transform: skew(-16deg);
    height: 29px;
  }
  .brand-mark i {
    background: var(--nrc-accent);
  }
  .brand-mark i:nth-child(2) {
    opacity: 0.65;
  }
  .brand-mark i:nth-child(3) {
    opacity: 0.3;
  }
  .brand-title {
    font-size: 17px;
    font-weight: 750;
    letter-spacing: -0.03em;
  }
  .tools {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .series-label {
    display: grid;
    gap: 3px;
  }
  .demo {
    background: #f1c66d18;
    color: var(--primary-text-color, #f3dba3);
    border: 1px solid #f1c66d55;
    padding: 9px 28px;
    font-size: 12px;
    letter-spacing: 0.02em;
  }
  .nav {
    display: flex;
    gap: 4px;
    overflow: auto;
    padding: 10px 24px;
    border-bottom: 1px solid var(--nrc-line);
    scrollbar-width: thin;
  }
  .nav button {
    border: 0;
    background: transparent;
    white-space: nowrap;
    color: var(--nrc-muted);
    font-size: 13px;
    padding: 10px 14px;
  }
  .nav button[aria-current="page"] {
    color: color-mix(
      in srgb,
      var(--nrc-accent) 35%,
      var(--primary-text-color, #e8edf2)
    );
    background: color-mix(in srgb, var(--nrc-accent), transparent 92%);
  }
  main {
    padding: 28px;
    min-height: 420px;
  }
  .stack > *,
  .two-col > *,
  .hero > * {
    min-width: 0;
  }
  .stack {
    display: grid;
    gap: 20px;
  }
  .section-head,
  .row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: center;
  }
  .section-head {
    margin-bottom: 20px;
  }
  .section-head p {
    margin-top: 6px;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    border: 1px solid var(--nrc-line);
    border-radius: 100px;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 10px;
    color: var(--nrc-muted);
    white-space: normal;
  }
  .badge::before {
    content: "";
    width: 6px;
    height: 6px;
    background: currentColor;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .green {
    color: color-mix(in srgb, #a8ef75 35%, var(--primary-text-color, #e8edf2));
  }
  .yellow {
    color: color-mix(in srgb, #f1cc72 35%, var(--primary-text-color, #e8edf2));
  }
  .red {
    color: color-mix(in srgb, #ff8d90 35%, var(--primary-text-color, #e8edf2));
  }
  .white,
  .checkered {
    color: var(--primary-text-color, #e8edf2);
  }
  .checkered::before {
    border-radius: 0;
    background: conic-gradient(#eee 25%, #444 0 50%, #eee 0 75%, #444 0);
    width: 12px;
    height: 12px;
    background-size: 8px 8px;
  }
  .panel {
    background: var(--nrc-panel);
    border: 1px solid var(--nrc-line);
    border-radius: 12px;
    padding: 22px;
  }
  .hero {
    position: relative;
    overflow: hidden;
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 40px;
    padding: 38px;
    background:
      radial-gradient(
        ellipse at 90% 0%,
        color-mix(in srgb, var(--nrc-accent), transparent 92%),
        transparent 70%
      ),
      var(--nrc-panel);
  }
  .hero::after {
    content: "";
    position: absolute;
    width: 180px;
    height: 280px;
    right: -55px;
    top: -80px;
    border: 28px solid var(--nrc-line);
    transform: rotate(30deg);
    border-radius: 45%;
    pointer-events: none;
    opacity: 0.3;
  }
  .hero-content {
    display: grid;
    gap: 18px;
    position: relative;
    z-index: 1;
  }
  .hero-track {
    font-size: 15px;
    color: var(--nrc-muted);
  }
  .hero-side {
    display: grid;
    align-content: center;
    gap: 22px;
    z-index: 1;
  }
  .lap-count {
    font-size: 60px;
    font-weight: 750;
    letter-spacing: -0.06em;
    line-height: 1;
  }
  .lap-count span {
    font-size: 22px;
    color: var(--nrc-muted);
    letter-spacing: -0.02em;
  }
  .stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--nrc-line);
    border: 1px solid var(--nrc-line);
    border-radius: 10px;
    overflow: hidden;
  }
  .stat {
    background: var(--nrc-panel);
    padding: 18px;
  }
  .stat strong {
    font-size: 24px;
    display: block;
    letter-spacing: -0.04em;
  }
  .stat span {
    font-size: 11px;
    color: var(--nrc-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .two-col {
    display: grid;
    grid-template-columns: 1.45fr 1fr;
    gap: 20px;
  }
  .favorite-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 12px;
  }
  .favorite {
    border-top: 2px solid var(--nrc-accent);
    display: grid;
    gap: 10px;
  }
  .favorite .position {
    font-size: 28px;
    letter-spacing: -0.04em;
  }
  .car {
    display: inline-grid;
    place-items: center;
    font-weight: 750;
    min-width: 34px;
    height: 32px;
    background: var(--nrc-line);
    border-radius: 6px;
    font-style: italic;
  }
  .progress {
    height: 5px;
    overflow: hidden;
    border-radius: 5px;
    background: var(--nrc-line);
  }
  .progress div {
    height: 100%;
    background: var(--nrc-accent);
    max-width: 100%;
  }
  .actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .state {
    border: 1px dashed var(--nrc-line);
    border-radius: 12px;
    padding: 30px;
    display: grid;
    gap: 12px;
  }
  .state h3 {
    font-size: 20px;
  }
  .error {
    border-color: #ff8d9060;
    background: #ff8d9008;
  }
  .loading {
    animation: breathe 1.6s ease-in-out infinite;
  }
  .source {
    font-size: 12px;
    color: var(--nrc-muted);
    border-top: 1px solid var(--nrc-line);
    padding: 14px 28px;
    display: flex;
    gap: 10px;
    justify-content: space-between;
    flex-wrap: wrap;
  }
  .field {
    display: grid;
    gap: 6px;
    font-size: 12px;
    color: var(--nrc-muted);
  }
  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: end;
    gap: 12px;
  }
  .filters input[type="number"] {
    width: 112px;
  }
  .filters .wide {
    min-width: 190px;
    flex: 1;
  }
  .filters fieldset {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    border: 1px solid var(--nrc-line);
    border-radius: 8px;
    margin: 0;
    padding: 10px;
  }
  .filters legend {
    font-size: 12px;
    color: var(--nrc-muted);
  }
  label.check {
    display: flex;
    align-items: center;
    gap: 6px;
    min-height: 32px;
  }
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    min-height: 0;
    accent-color: var(--nrc-accent);
  }
  .filters .check {
    font-size: 12px;
  }
  .notice {
    padding: 12px 16px;
    border-left: 2px solid var(--nrc-accent);
    background: color-mix(in srgb, var(--nrc-accent), transparent 96%);
    font-size: 12px;
    color: var(--nrc-muted);
  }
  .schedule {
    display: grid;
    gap: 14px;
  }
  .event-card {
    display: grid;
    grid-template-columns: 75px 1fr auto;
    align-items: start;
    gap: 20px;
  }
  .event-number {
    font-size: 30px;
    letter-spacing: -0.04em;
    color: var(--nrc-muted);
  }
  .sessions {
    display: grid;
    margin-top: 16px;
    border-top: 1px solid var(--nrc-line);
  }
  .session-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--nrc-line);
  }
  .session-row:last-child {
    border-bottom: 0;
  }
  .pager {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 18px;
  }
  .table-scroll {
    overflow: auto;
    border: 1px solid var(--nrc-line);
    border-radius: 10px;
    scrollbar-width: thin;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    text-align: left;
    white-space: nowrap;
  }
  th {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--nrc-muted);
    background: var(--nrc-panel);
    font-weight: 600;
  }
  th,
  td {
    padding: 13px 16px;
    border-bottom: 1px solid var(--nrc-line);
  }
  tr:last-child td {
    border: 0;
  }
  td:first-child {
    font-weight: 700;
  }
  .record-list {
    display: grid;
    gap: 8px;
  }
  .record-list details {
    border: 1px solid var(--nrc-line);
    border-radius: 8px;
    padding: 12px 16px;
  }
  summary {
    cursor: pointer;
    min-height: 28px;
  }
  summary:focus-visible {
    outline: 3px solid var(--primary-text-color, #e8edf2);
  }
  dl {
    display: grid;
    grid-template-columns: minmax(90px, 0.7fr) minmax(0, 1.3fr);
    gap: 6px 16px;
    font-size: 12px;
    margin: 12px 0;
  }
  dt {
    color: var(--nrc-muted);
    overflow-wrap: anywhere;
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  dd dl {
    margin-top: 0;
  }
  .detail-panel {
    border: 1px solid var(--nrc-accent);
    scroll-margin: 20px;
  }
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 12px;
  }
  .metric strong {
    font-size: 24px;
  }
  .metric p {
    font-size: 11px;
    color: var(--nrc-muted);
  }
  .metric h3 {
    font-size: 12px;
    font-weight: 500;
    color: var(--nrc-muted);
  }
  .evidence {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .chart-layout {
    display: grid;
    gap: 16px;
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
  }
  @keyframes breathe {
    50% {
      opacity: 0.6;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation: none !important;
      transition: none !important;
      scroll-behavior: auto !important;
    }
  }
  @container (max-width:740px) {
    .masthead {
      padding: 18px 20px;
    }
    .hero {
      padding: 24px;
      grid-template-columns: 1fr;
      gap: 24px;
    }
    .hero-side {
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .hero-side .actions {
      grid-column: 1/-1;
    }
    .two-col {
      grid-template-columns: 1fr;
    }
    main {
      padding: 20px;
    }
    .section-head {
      align-items: start;
    }
    .event-card {
      grid-template-columns: 45px 1fr;
      gap: 12px;
    }
    .event-card > .actions {
      grid-column: 2;
    }
    .nav {
      padding: 8px 12px;
    }
    .source {
      padding: 14px 20px;
    }
    .demo {
      padding: 9px 20px;
    }
  }
  @container (max-width:450px) {
    .masthead {
      padding: 16px;
      align-items: start;
      gap: 8px;
    }
    .brand-title {
      font-size: 14px;
    }
    .brand .eyebrow {
      font-size: 9px;
    }
    .tools {
      max-width: 135px;
    }
    .tools select {
      font-size: 11px;
      padding: 8px 6px;
      width: 100%;
    }
    .brand-mark {
      height: 25px;
      grid-template-columns: repeat(3, 4px);
      gap: 2px;
    }
    .brand {
      gap: 9px;
    }
    .hero {
      padding: 20px;
    }
    .hero-side {
      grid-template-columns: 1fr;
    }
    .lap-count {
      font-size: 48px;
    }
    .stat {
      padding: 12px;
    }
    .stat strong {
      font-size: 20px;
    }
    main {
      padding: 16px;
    }
    .panel {
      padding: 16px;
    }
    .section-head {
      flex-wrap: wrap;
    }
    .section-head h2 {
      font-size: 20px;
    }
    .session-row {
      display: grid;
      gap: 4px;
    }
    .favorite-grid {
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .source {
      padding: 12px 16px;
    }
    .demo {
      padding: 9px 16px;
    }
    .filters {
      gap: 10px;
    }
    .filters .field {
      flex: 1;
      min-width: 100px;
    }
    .filters .wide {
      flex-basis: 100%;
    }
    .notice {
      padding: 12px;
    }
    .event-number {
      font-size: 24px;
    }
  }
`;
function z(r, e = 0) {
  return r == null ? "Unknown / not reported" : typeof r == "boolean" ? r ? "Yes" : "No" : typeof r == "number" ? b(r, void 0, 6) : typeof r == "string" ? r : e > 6 ? "Nested observation" : Array.isArray(r) ? r.length ? l`${r.map(
    (t, s) => l`<div>
              ${r.length > 1 ? l`<small>Observation ${s + 1}</small>` : h}${z(t, e + 1)}
            </div>`
  )}` : "No reported records" : l`<dl>
    ${Object.entries(r).map(
    ([t, s]) => l`<dt>${m(t)}</dt>
          <dd>${z(s, e + 1)}</dd>`
  )}
  </dl>`;
}
function G(r) {
  return l`<div class="record-list">
    ${r.map(
    (e, t) => l`<details>
          <summary>
            ${m(e.kind)}${e.driver_id ? ` · driver ${e.driver_id}` : ""}${e.number != null ? ` · stage ${e.number}` : ""}${e.size ? ` · ${e.size} laps` : ""}${e.source_index != null ? ` · source index ${e.source_index}` : ` · record ${t + 1}`}
          </summary>
          ${z(e.value ?? e.best_mean ?? e)}
        </details>`
  )}
  </div>`;
}
function De(r, e) {
  const t = r.evidence ?? r.datasets ?? [];
  return l`<div class="evidence">
    ${t.map(
    (s) => l`<details>
          <summary class="badge">
            ${"dataset" in s ? s.dataset : s.provenance?.dataset ?? "Dataset"}
            · ${m(s.status)}
          </summary>
          <dl>
            <dt>Reason</dt>
            <dd>${m(s.reason)}</dd>
            <dt>Identity validation</dt>
            <dd>${m(s.provenance?.validation)}</dd>
            <dt>Coverage</dt>
            <dd>${m(s.provenance?.coverage)}</dd>
            <dt>Retrieved</dt>
            <dd>${E(s.provenance?.retrieved_at, e)}</dd>
            <dt>Reported content time</dt>
            <dd>${E(s.provenance?.response_at, e)}</dd>
            <dt>Delivery</dt>
            <dd>${m(s.provenance?.delivery)}</dd>
            <dt>Retry after</dt>
            <dd>${s.provenance?.retry_after ?? "Unknown"}</dd>
          </dl>
        </details>`
  )}
  </div>`;
}
function Ne(r, e) {
  return l`<div class="panel metric">
    <h3>${m(r.name)}</h3>
    <strong>${b(r.value, e, 3)}</strong>
    <p>${m(r.classification)} · ${yt(r)}</p>
    <details>
      <summary>Method & availability</summary>
      <p>${m(r.method)}${r.reason ? ` · ${m(r.reason)}` : ""}</p>
    </details>
  </div>`;
}
function _t(r, e) {
  const t = r.filter((s) => s.kind === "result");
  return t.length ? l`<div
        class="table-scroll"
        role="region"
        aria-label="Historical reported results"
        tabindex="0"
      >
        <table>
          <caption class="sr-only">
            Reported historical results; no assertion of official finality.
          </caption>
          <thead>
            <tr>
              <th>Finish</th>
              <th>Driver</th>
              <th>Start</th>
              <th>Laps</th>
              <th>Led</th>
              <th>Points</th>
              <th>Playoff</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${t.map((s) => {
    const i = s.value;
    return l`<tr>
                <td>${b(i.finishing_position, e?.locale?.language)}</td>
                <td>
                  <span class="car">${i.driver.car_number ?? "—"}</span> ${i.driver.name ?? i.driver.nascar_driver_id}
                </td>
                <td>${b(i.starting_position)}</td>
                <td>${b(i.laps_completed)}</td>
                <td>${b(i.laps_led)}</td>
                <td>${b(i.points_earned)}</td>
                <td>${b(i.playoff_points_earned)}</td>
                <td>${i.finishing_status ?? "Unknown"}</td>
              </tr>`;
  })}
          </tbody>
        </table>
      </div>` : h;
}
const xt = { CHILD: 2 }, wt = (r) => (...e) => ({ _$litDirective$: r, values: e });
let At = class {
  constructor(e) {
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AT(e, t, s) {
    this._$Ct = e, this._$AM = t, this._$Ci = s;
  }
  _$AS(e, t) {
    return this.update(e, t);
  }
  update(e, t) {
    return this.render(...t);
  }
};
const { I: kt } = dt, Pe = (r) => r, Ue = () => document.createComment(""), O = (r, e, t) => {
  const s = r._$AA.parentNode, i = e === void 0 ? r._$AB : e._$AA;
  if (t === void 0) {
    const a = s.insertBefore(Ue(), i), n = s.insertBefore(Ue(), i);
    t = new kt(a, n, r, r.options);
  } else {
    const a = t._$AB.nextSibling, n = t._$AM, c = n !== r;
    if (c) {
      let o;
      t._$AQ?.(r), t._$AM = r, t._$AP !== void 0 && (o = r._$AU) !== n._$AU && t._$AP(o);
    }
    if (a !== i || c) {
      let o = t._$AA;
      for (; o !== a; ) {
        const u = Pe(o).nextSibling;
        Pe(s).insertBefore(o, i), o = u;
      }
    }
  }
  return t;
}, C = (r, e, t = r) => (r._$AI(e, t), r), St = {}, Ct = (r, e = St) => r._$AH = e, Et = (r) => r._$AH, re = (r) => {
  r._$AR(), r._$AA.remove();
};
const Me = (r, e, t) => {
  const s = /* @__PURE__ */ new Map();
  for (let i = e; i <= t; i++) s.set(r[i], i);
  return s;
}, Rt = wt(class extends At {
  constructor(r) {
    if (super(r), r.type !== xt.CHILD) throw Error("repeat() can only be used in text expressions");
  }
  dt(r, e, t) {
    let s;
    t === void 0 ? t = e : e !== void 0 && (s = e);
    const i = [], a = [];
    let n = 0;
    for (const c of r) i[n] = s ? s(c, n) : n, a[n] = t(c, n), n++;
    return { values: a, keys: i };
  }
  render(r, e, t) {
    return this.dt(r, e, t).values;
  }
  update(r, [e, t, s]) {
    const i = Et(r), { values: a, keys: n } = this.dt(e, t, s);
    if (!Array.isArray(i)) return this.ut = n, a;
    const c = this.ut ??= [], o = [];
    let u, $, p = 0, d = i.length - 1, v = 0, g = a.length - 1;
    for (; p <= d && v <= g; ) if (i[p] === null) p++;
    else if (i[d] === null) d--;
    else if (c[p] === n[v]) o[v] = C(i[p], a[v]), p++, v++;
    else if (c[d] === n[g]) o[g] = C(i[d], a[g]), d--, g--;
    else if (c[p] === n[g]) o[g] = C(i[p], a[g]), O(r, o[g + 1], i[p]), p++, g--;
    else if (c[d] === n[v]) o[v] = C(i[d], a[v]), O(r, i[p], i[d]), d--, v++;
    else if (u === void 0 && (u = Me(n, v, g), $ = Me(c, p, d)), u.has(c[p])) if (u.has(c[d])) {
      const _ = $.get(n[v]), f = _ !== void 0 ? i[_] : null;
      if (f === null) {
        const x = O(r, i[p]);
        C(x, a[v]), o[v] = x;
      } else o[v] = C(f, a[v]), O(r, i[p], f), i[_] = null;
      v++;
    } else re(i[d]), d--;
    else re(i[p]), p++;
    for (; v <= g; ) {
      const _ = O(r, o[g + 1]);
      C(_, a[v]), o[v++] = _;
    }
    for (; p <= d; ) {
      const _ = i[p++];
      _ !== null && re(_);
    }
    return this.ut = n, Ct(r, o), N;
  }
});
class Dt extends w {
  constructor() {
    super(...arguments), this.rows = [], this.sort = "position", this.descending = !1;
  }
  static {
    this.properties = {
      rows: { attribute: !1 },
      hass: { attribute: !1 },
      sort: { state: !0 },
      descending: { state: !0 }
    };
  }
  static {
    this.styles = [
      V,
      X`
      :host {
        container-type: inline-size;
      }
      .tower {
        min-width: 960px;
      }
      th button {
        min-height: 32px;
        padding: 0;
        border: 0;
        background: none;
        font-size: inherit;
        text-transform: inherit;
        letter-spacing: inherit;
        color: inherit;
      }
      th button:hover {
        color: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      td {
        font-size: 13px;
      }
      .driver-cell {
        min-width: 190px;
      }
      .driver-button {
        border: 0;
        background: none;
        padding: 0;
        text-align: left;
        min-height: 36px;
        font-weight: 650;
      }
      .favorite-row {
        background: color-mix(in srgb, var(--nrc-accent), transparent 96%);
      }
      .star {
        color: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
        margin-right: 6px;
      }
      .rank {
        font-size: 19px;
        letter-spacing: -0.04em;
      }
      td.sticky,
      th.sticky {
        position: sticky;
        left: 0;
        background: var(--nrc-base);
        z-index: 1;
      }
      .mobile-metrics {
        display: none;
      }
      .positive {
        color: color-mix(
          in srgb,
          #a8ef75 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .negative {
        color: color-mix(
          in srgb,
          #ff8d90 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .table-note {
        font-size: 11px;
        color: var(--nrc-muted);
        padding: 10px 0;
      }
      @container (max-width:600px) {
        .tower {
          min-width: 700px;
        }
        .driver-cell {
          min-width: 160px;
        }
        .mobile-metrics {
          display: block;
          font-size: 11px;
          font-weight: 400;
          color: var(--nrc-muted);
        }
        td,
        th {
          padding: 10px;
        }
        .desktop-extra {
          display: none;
        }
        .rank {
          font-size: 17px;
        }
        .driver-button {
          white-space: normal;
          max-width: 145px;
        }
        .table-note {
          font-size: 11px;
        }
      }
    `
    ];
  }
  order(e) {
    e === this.sort ? this.descending = !this.descending : (this.sort = e, this.descending = !1);
  }
  heading(e, t, s = "") {
    return l`<th
      scope="col"
      class=${s}
      aria-sort=${this.sort === t ? this.descending ? "descending" : "ascending" : "none"}
    >
      <button @click=${() => this.order(t)}>
        ${e}${this.sort === t ? this.descending ? " ↓" : " ↑" : h}
      </button>
    </th>`;
  }
  render() {
    const e = Z(this.hass);
    return l`<div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Timing tower. Scroll horizontally for additional reported measurements."
      >
        <table class="tower">
          <caption class="sr-only">
            Full reported leaderboard. Activate a column to sort or a driver to
            open details. Timing and speed units are unverified.
          </caption>
          <thead>
            <tr>
              ${this.heading("Pos", "position", "sticky")}${this.heading(
      "Car",
      "car_number"
    )}${this.heading("Driver", "name")}${this.heading(
      "Fav",
      "favorite"
    )}${this.heading(
      "Start",
      "starting_position",
      "desktop-extra"
    )}${this.heading("Change", "position_change")}${this.heading(
      "Gap*",
      "gap"
    )}${this.heading("Last*", "last_lap_time")}${this.heading(
      "Best*",
      "best_lap_time"
    )}${this.heading("Laps", "laps_completed")}
              <th scope="col">Speed*</th>
              <th scope="col">Status / pits</th>
            </tr>
          </thead>
          <tbody>
            ${Rt(
      bt(this.rows, this.sort, this.descending),
      (t) => t.driver_id,
      (t) => l`<tr class=${t.favorite ? "favorite-row" : ""}>
                  <td class="rank sticky">${b(t.position, e)}</td>
                  <td><span class="car">${t.car_number ?? "—"}</span></td>
                  <td class="driver-cell">
                    <button
                      class="driver-button"
                      @click=${() => this.dispatchEvent(
        new CustomEvent("driver-open", {
          detail: t,
          bubbles: !0,
          composed: !0
        })
      )}
                    >
                      ${t.favorite ? l`<span class="star" aria-label="Favorite"
                            >★</span
                          >` : h}${t.name ?? `Driver ${t.driver_id}`}<span
                        class="mobile-metrics"
                        >Start ${b(t.starting_position, e)} ·
                        ${t.running_status ?? "Status unknown"}</span
                      >
                    </button>
                  </td>
                  <td>
                    ${t.favorite ? l`<span class="star" aria-label="Favorite">★</span>` : "—"}
                  </td>
                  <td class="desktop-extra">
                    ${b(t.starting_position, e)}
                  </td>
                  <td
                    class=${(t.position_change.value ?? 0) > 0 ? "positive" : (t.position_change.value ?? 0) < 0 ? "negative" : ""}
                  >
                    ${t.position_change.value != null && t.position_change.value > 0 ? "+" : ""}${b(t.position_change.value, e)}
                  </td>
                  <td>${b(t.gap, e, 3)}</td>
                  <td>${b(t.last_lap_time, e, 3)}</td>
                  <td>${b(t.best_lap_time, e, 3)}</td>
                  <td>${b(t.laps_completed, e)}</td>
                  <td>
                    <span title="Reported last / best / average speed"
                      >${b(t.last_lap_speed, e, 3)} /
                      ${b(t.best_lap_speed, e, 3)} /
                      ${b(t.average_speed, e, 3)}</span
                    >
                  </td>
                  <td>
                    ${t.running_status ?? "Unknown"} ·
                    ${t.pit_stops.total ?? "—"} pit observations
                  </td>
                </tr>`
    )}
          </tbody>
        </table>
      </div>
      <p class="table-note">
        * Reported gap, lap-time and speed scales; units unverified. Change =
        starting position − current position (derived). On mobile, scroll for
        additional columns or open a driver.
      </p>`;
  }
}
customElements.define("nrc-leaderboard", Dt);
function Nt(r, e) {
  const t = /* @__PURE__ */ new Map();
  for (const s of r) {
    if (!s.driver_id) continue;
    let i;
    if (s.kind === "samples" && s.value && e !== "window") {
      const a = s.value;
      i = {
        lap: a.lap,
        value: e === "position" ? a.usable_position : e === "delta" ? a.consecutive_time_delta : a.valid_time && a.included_in_time_basis ? a.reported_time : null
      };
    } else s.kind === "window" && s.value && e === "window" && (i = { lap: s.value.last_lap, value: s.value.mean });
    if (i) {
      const a = t.get(s.driver_id) ?? [];
      a.push(i), t.set(s.driver_id, a);
    }
  }
  return [...t].map(([s, i]) => ({
    id: s,
    points: i.sort((a, n) => a.lap - n.lap)
  }));
}
function Pt(r) {
  const e = [];
  let t = [];
  for (const s of r) {
    if (s.value === null) {
      t.length && e.push(t), t = [];
      continue;
    }
    t.length && s.lap !== t.at(-1).lap + 1 && (e.push(t), t = []), t.push(s);
  }
  return t.length && e.push(t), e;
}
class Ut extends w {
  constructor() {
    super(...arguments), this.rows = [], this.mode = "time";
  }
  static {
    this.properties = {
      rows: { attribute: !1 },
      mode: { type: String },
      locale: { type: String }
    };
  }
  static {
    this.styles = [
      V,
      X`
      :host {
        display: block;
      }
      .graph {
        width: 100%;
        height: auto;
        display: block;
        min-height: 190px;
      }
      .grid {
        stroke: var(--nrc-line);
        stroke-width: 1;
      }
      .axis {
        fill: var(--nrc-muted);
        font-size: 11px;
        font-family: inherit;
      }
      .legend {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 12px;
      }
      .swatch {
        width: 12px;
        height: 3px;
        display: inline-block;
        vertical-align: middle;
        margin-right: 6px;
      }
      .graph-wrap {
        border: 1px solid var(--nrc-line);
        border-radius: 10px;
        padding: 10px;
        background: var(--nrc-panel);
      }
      details {
        margin-top: 12px;
      }
      table {
        white-space: normal;
      }
    `
    ];
  }
  render() {
    const e = Nt(this.rows, this.mode), t = e.flatMap((f) => f.points).filter((f) => f.value !== null), s = {
      time: "Lap-time progression",
      position: "Position progression",
      delta: "Consecutive-lap change",
      window: "Consecutive-window mean"
    };
    if (!t.length)
      return l`<div class="state">
        <h3>${s[this.mode]}</h3>
        <p class="muted">
          No supported measurements on the loaded pages. Load the next page or
          change the selection.
        </p>
      </div>`;
    const i = t.map((f) => f.lap), a = t.map((f) => f.value), n = Math.min(...i), c = Math.max(...i), o = Math.min(...a), u = Math.max(...a), $ = Math.max((u - o) * 0.12, 0.25), p = this.mode === "position" ? o : o - $, d = this.mode === "position" ? u : u + $, v = (f) => 55 + (f - n) / (c - n || 1) * 650, g = (f) => this.mode === "position" ? 30 + (f - p) / (d - p || 1) * 210 : 240 - (f - p) / (d - p || 1) * 210, _ = [
      "#a8ef75",
      "#84c5ff",
      "#f3c574",
      "#d8a2ed",
      "#fe9b97",
      "#80d6cf",
      "#ebc1ac",
      "#d8e1eb"
    ].map(
      (f) => `color-mix(in srgb, ${f} 35%, var(--primary-text-color,#e8edf2))`
    );
    return l`<div class="graph-wrap">
        <h3>${s[this.mode]}</h3>
        <p class="muted">
          <small
            >${this.mode === "position" ? "Reported running positions" : this.mode === "time" ? "Reported measurements in selected basis · source unit unverified" : "Derived from selected observations · source unit unverified"}.
            Loaded pages only; gaps remain disconnected.</small
          >
        </p>
        <svg
          class="graph"
          viewBox="0 0 740 280"
          role="img"
          aria-label=${s[this.mode] + "; exact values available in the data table below."}
        >
          ${[0, 1, 2, 3, 4].map((f) => {
      const x = p + (d - p) * f / 4;
      return T`<line class="grid" x1="55" x2="705" y1=${g(x)} y2=${g(x)}></line><text class="axis" x="48" y=${g(x) + 4} text-anchor="end">${b(x, this.locale, 2)}</text>`;
    })}
          <text class="axis" x="55" y="267">
            Lap ${b(n, this.locale)}
          </text>
          <text class="axis" x="705" y="267" text-anchor="end">
            Lap ${b(c, this.locale)}
          </text>
          ${e.map(
      (f, x) => Pt(f.points).map(
        (ue) => T`<path d=${ue.map((k, je) => `${je ? "L" : "M"}${v(k.lap)},${g(k.value)}`).join(" ")} fill="none" stroke=${_[x % 8]} stroke-width="2.5" stroke-linejoin="round"></path>${ue.map((k) => T`<circle cx=${v(k.lap)} cy=${g(k.value)} r="2.5" fill=${_[x % 8]}><title>Driver ${f.id} · lap ${k.lap} · ${k.value}</title></circle>`)}`
      )
    )}
        </svg>
        <div class="legend">
          ${e.map(
      (f, x) => l`<span
                ><i class="swatch" style=${`background:${_[x % 8]}`}></i
                >Driver ${f.id}</span
              >`
    )}
        </div>
      </div>
      <details>
        <summary>Exact chart data · accessible table</summary>
        <div
          class="table-scroll"
          tabindex="0"
          role="region"
          aria-label="Chart data"
        >
          <table>
            <thead>
              <tr>
                <th>Driver</th>
                <th>Lap</th>
                <th>Value (source unit / position)</th>
              </tr>
            </thead>
            <tbody>
              ${e.flatMap(
      (f) => f.points.map(
        (x) => l`<tr>
                      <td>${f.id}</td>
                      <td>${x.lap}</td>
                      <td>${b(x.value, this.locale, 3)}</td>
                    </tr>`
      )
    )}
            </tbody>
          </table>
        </div>
      </details>`;
  }
}
customElements.define("nrc-chart", Ut);
function Mt(r) {
  const e = /* @__PURE__ */ new Map(), t = (s, i, a) => {
    const n = JSON.stringify([
      i,
      a.name,
      a.classification,
      a.unit,
      a.method
    ]), c = e.get(n) ?? {
      key: n,
      name: `${i} · ${m(a.name)}`,
      classification: a.classification,
      unit: a.unit,
      method: a.method,
      observations: []
    };
    c.observations.push({
      driver: s,
      value: a.value,
      reason: a.reason
    }), e.set(n, c);
  };
  for (const s of r)
    if (!(!s.driver_id || !s.value)) {
      if (s.kind === "driver")
        for (const i of s.value.metrics)
          t(s.driver_id, "Lap summary", i);
      if (s.kind === "performance" && s.value.result) {
        const i = s.value.result;
        for (const a of [
          "starting_position",
          "finishing_position",
          "laps_completed",
          "laps_led",
          "points_earned",
          "playoff_points_earned"
        ])
          t(s.driver_id, "Race result", {
            name: a,
            value: i[a],
            classification: "recorded",
            unit: a.includes("position") ? "position" : a.includes("laps") ? "lap_count" : "reported_points",
            method: "reported_result",
            reason: i[a] === null ? "not_reported" : null
          });
      }
      if (s.kind === "performance_stages") {
        const i = s.value;
        for (const a of ["position", "points"])
          t(
            s.driver_id,
            `${m(i.dataset)} stage ${i.number}${i.run_id ? ` · ${i.run_namespace} ${i.run_id}` : ""}`,
            {
              name: a,
              value: i.conflict ? null : i[a],
              classification: "recorded",
              unit: a === "position" ? "position" : "reported_points",
              method: "reported_stage_observation",
              reason: i.conflict ? "conflicting_source_observations" : i[a] === null ? "not_reported" : null
            }
          );
      }
      if (s.kind === "performance_reported_metrics") {
        const i = s.value;
        for (const a of i.metrics)
          t(
            s.driver_id,
            `${m(i.dataset)} · group ${i.source_index}${i.title ? ` · ${i.title}` : ""}`,
            {
              name: a.field,
              value: a.interpretation === "reported" ? a.value : null,
              classification: "recorded",
              unit: "source_unit_unverified",
              method: "reported_source_field",
              reason: a.interpretation === "reported" ? null : a.interpretation
            }
          );
      }
    }
  return [...e.values()];
}
class Tt extends w {
  constructor() {
    super(...arguments), this.rows = [], this.selected = "";
  }
  static {
    this.properties = {
      rows: { attribute: !1 },
      selected: { state: !0 },
      locale: { type: String }
    };
  }
  static {
    this.styles = [
      V,
      X`
      :host {
        display: block;
      }
      .bars {
        width: 100%;
        display: block;
      }
      .axis {
        fill: var(--nrc-muted);
        font: 11px system-ui;
      }
      .bar {
        fill: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .baseline {
        stroke: var(--nrc-line);
      }
      table {
        white-space: normal;
      }
    `
    ];
  }
  render() {
    const e = Mt(this.rows), t = e.find((o) => o.key === this.selected) ?? e[0];
    if (!t)
      return l`<div class="notice">
        Load pages containing driver summaries or supported
        race/stage/loop/average records to compare their metrics.
      </div>`;
    const s = t.observations.flatMap(
      (o) => o.value === null ? [] : [o.value]
    ), i = Math.min(0, ...s), a = Math.max(0, ...s), n = (o) => 165 + (o - i) / (a - i || 1) * 440, c = t.unit.includes("unverified") ? "Source unit · unverified" : m(t.unit);
    return l`<section class="panel stack">
      <h3>Compare loaded summary metrics</h3>
      <label class="field"
        >Metric and measurement basis<select
          .value=${t.key}
          @change=${(o) => {
      this.selected = o.target.value;
    }}
        >
          ${e.map(
      (o) => l`<option value=${o.key}>
                ${o.name} · ${m(o.classification)}
              </option>`
    )}
        </select></label
      >
      <p class="muted">
        <small
          >${m(t.classification)} · ${c} ·
          ${m(t.method)}. Loaded observations only.</small
        >
      </p>
      <svg
        class="bars"
        viewBox=${`0 0 700 ${t.observations.length * 44 + 20}`}
        role="img"
        aria-label=${`${t.name} comparison; exact values in the table below.`}
      >
        <line
          class="baseline"
          x1=${n(0)}
          x2=${n(0)}
          y1="0"
          y2=${t.observations.length * 44}
        ></line>
        ${t.observations.map(
      (o, u) => T`<text class="axis" x="8" y=${u * 44 + 24}>Driver ${o.driver}</text>${o.value !== null ? T`<rect class="bar" x=${Math.min(n(0), n(o.value))} y=${u * 44 + 7} width=${Math.max(1, Math.abs(n(o.value) - n(0)))} height="25" rx="3"></rect>` : T`<text class="axis" x="165" y=${u * 44 + 24}>Unavailable</text>`}<text class="axis" x="620" y=${u * 44 + 24}>${b(o.value, this.locale, 3)}</text>`
    )}
      </svg>
      <div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Summary comparison values"
      >
        <table>
          <thead>
            <tr>
              <th>Driver</th>
              <th>Value · ${c}</th>
              <th>Availability</th>
            </tr>
          </thead>
          <tbody>
            ${t.observations.map(
      (o) => l`<tr>
                  <td>${o.driver}</td>
                  <td>${b(o.value, this.locale, 6)}</td>
                  <td>
                    ${o.reason ? m(o.reason) : "Reported by analytics API"}
                  </td>
                </tr>`
    )}
          </tbody>
        </table>
      </div>
    </section>`;
  }
}
customElements.define("nrc-metric-chart", Tt);
class zt extends w {
  constructor() {
    super(...arguments), this.config = { type: "custom:nascar-race-center-card" }, this.entries = [], this.generation = 0;
  }
  static {
    this.properties = {
      config: { state: !0 },
      entries: { state: !0 },
      error: { state: !0 }
    };
  }
  static {
    this.styles = V;
  }
  set hass(e) {
    if (!e) return;
    const t = this.hostHass?.connection !== e.connection;
    this.hostHass = e, t && this.isConnected && this.discover();
  }
  get hass() {
    return this.hostHass;
  }
  setConfig(e) {
    this.config = { ...e };
  }
  connectedCallback() {
    super.connectedCallback(), this.hostHass && this.discover();
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this.generation++;
  }
  async discover() {
    const e = ++this.generation;
    try {
      const t = await We(this.hostHass);
      e === this.generation && (this.entries = t, this.error = void 0);
    } catch (t) {
      e === this.generation && (this.error = t);
    }
  }
  change(e, t) {
    const s = { ...this.config, [e]: t || void 0 };
    this.config = s, this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: s },
        bubbles: !0,
        composed: !0
      })
    );
  }
  render() {
    return l`<div class="stack">
      <p>
        Dashboard API v1 requires a Home Assistant administrator. Select the
        integration entry explicitly; favorites and series are managed by the
        integration.
      </p>
      ${this.error ? l`<p role="alert">${Be(this.error)}</p>` : ""}<label class="field"
        >Integration entry<select
          .value=${this.config.entry_id ?? ""}
          @change=${(e) => this.change("entry_id", e.target.value)}
        >
          <option value="">Select a NASCAR Race Center entry</option>
          ${this.entries.map(
      (e) => l`<option value=${e.entry_id}>
                ${e.title} · ${e.state}
              </option>`
    )}
        </select></label
      ><label class="field"
        >Entry ID (manual alternative)<input
          .value=${this.config.entry_id ?? ""}
          @change=${(e) => this.change(
      "entry_id",
      e.target.value.trim()
    )} /></label
      ><label class="field"
        >Initial series<select
          .value=${String(this.config.series_id ?? "")}
          @change=${(e) => this.change(
      "series_id",
      Number(e.target.value)
    )}
        >
          <option value="">First monitored series</option>
          ${[1, 2, 3].map(
      (e) => l`<option value=${e}>${U[e]}</option>`
    )}
        </select></label
      ><label class="field"
        >Initial view<select
          .value=${this.config.section ?? "Race Center"}
          @change=${(e) => this.change("section", e.target.value)}
        >
          ${ne.map((e) => l`<option>${e}</option>`)}
        </select></label
      ><label class="field"
        >Title<input
          .value=${this.config.title ?? ""}
          placeholder="NASCAR Race Center"
          @change=${(e) => this.change("title", e.target.value.trim())}
      /></label>
    </div>`;
  }
}
customElements.define("nascar-race-center-card-editor", zt);
const It = "0.5.0";
class Lt extends w {
  constructor() {
    super(...arguments), this.config = { type: "custom:nascar-race-center-card" }, this.signature = "", this.epoch = 0, this.liveEpoch = 0, this.bootPending = !1, this.liveChain = Promise.resolve(), this.entries = [], this.loading = !1, this.section = "Race Center", this.series = 1, this.schedules = /* @__PURE__ */ new Map(), this.snapshots = /* @__PURE__ */ new Map(), this.chartMode = "time", this.chartWindow = 5, this.season = (/* @__PURE__ */ new Date()).getFullYear(), this.raceId = "", this.ready = () => {
      this.scheduleStart();
    }, this.disconnected = () => {
      this.clearRuntime(), this.error = new y("connection_error"), this.requestUpdate();
    };
  }
  static {
    this.styles = V;
  }
  static getConfigElement() {
    return document.createElement("nascar-race-center-card-editor");
  }
  static getStubConfig() {
    return { type: "custom:nascar-race-center-card", section: "Race Center" };
  }
  static getDefaultConfig() {
    return this.getStubConfig();
  }
  getCardSize() {
    return 10;
  }
  getGridOptions() {
    return { columns: "full", rows: "auto", min_columns: 6, min_rows: 6 };
  }
  setConfig(e) {
    if (!e || e.entry_id !== void 0 && (typeof e.entry_id != "string" || !e.entry_id.trim() || e.entry_id.length > 128))
      throw new Error("entry_id must be a nonempty integration entry ID.");
    if (e.series_id !== void 0 && ![1, 2, 3].includes(e.series_id))
      throw new Error("series_id must be 1, 2, or 3.");
    if (e.section !== void 0 && !ne.includes(e.section))
      throw new Error("Unknown Race Center section.");
    this.config = { ...e }, this.section = e.section ?? "Race Center", this.clearRuntime(), this.scheduleStart(), this.requestUpdate();
  }
  set hass(e) {
    if (!e) return;
    const t = this.hostHass?.connection !== e.connection, s = JSON.stringify([
      e.user?.is_admin,
      e.locale,
      e.config?.time_zone
    ]), i = s !== this.signature;
    this.signature = s, this.hostHass = e, t ? (this.unlisten(), this.clearRuntime(), this.isConnected && (this.listen(), this.scheduleStart())) : i && this.isConnected && this.scheduleStart(), i && this.requestUpdate();
  }
  get hass() {
    return this.hostHass;
  }
  connectedCallback() {
    super.connectedCallback(), this.listen(), this.scheduleStart(), this.clock = setInterval(() => {
      this.section === "Race Center" && this.requestUpdate();
    }, 6e4);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this.unlisten(), this.clearRuntime(), this.clock && clearInterval(this.clock), this.clock = void 0;
  }
  listen() {
    !this.hostHass || this.listening || (this.listening = this.hostHass.connection, this.listening.addEventListener("ready", this.ready), this.listening.addEventListener("disconnected", this.disconnected));
  }
  unlisten() {
    this.listening?.removeEventListener("ready", this.ready), this.listening?.removeEventListener("disconnected", this.disconnected), this.listening = void 0;
  }
  clearRuntime() {
    this.epoch++, this.stopLive(), this.client?.dispose(), this.client = void 0, this.currentRace = void 0, this.detail?.invalidate(), this.bootstrapData = void 0, this.liveData = void 0, this.loading = !1, this.error = void 0, this.formError = void 0, this.detail = void 0, this.detailDriver = void 0, this.detailError = void 0, this.detailFocus = void 0;
    for (const e of [...this.schedules.values(), ...this.snapshots.values()])
      e.invalidate();
    this.schedules.clear(), this.snapshots.clear(), this.history = void 0, this.analytics = void 0;
  }
  stopLive() {
    this.liveEpoch++, this.liveData = void 0, this.currentRace = void 0;
    const e = this.unsubscribe;
    this.unsubscribe = void 0, e && (this.liveChain = this.liveChain.then(async () => {
      try {
        await e();
      } catch {
      }
    }));
  }
  scheduleStart() {
    this.bootPending || !this.isConnected || !this.hostHass || (this.bootPending = !0, queueMicrotask(() => {
      this.bootPending = !1, this.isConnected && this.start();
    }));
  }
  async start() {
    this.clearRuntime();
    const e = this.epoch, t = this.hostHass;
    if (t.user?.is_admin === !1) {
      this.error = new y("unauthorized"), this.requestUpdate();
      return;
    }
    this.loading = !0, this.requestUpdate();
    try {
      if (!this.config.entry_id) {
        const a = await We(t);
        if (e !== this.epoch) return;
        this.entries = a;
        return;
      }
      const s = new ft(
        t,
        this.config.entry_id,
        () => e === this.epoch && this.isConnected
      );
      this.client = s;
      const i = await s.bootstrap();
      if (e !== this.epoch) return;
      this.bootstrapData = i, this.series = this.config.series_id && i.series_ids.includes(this.config.series_id) ? this.config.series_id : i.series_ids[0], this.setDefaultRace(), this.syncLive(), this.section === "Race Weekend" && this.loadSchedule();
    } catch (s) {
      e === this.epoch && (this.error = s);
    } finally {
      e === this.epoch && (this.loading = !1, this.requestUpdate());
    }
  }
  setDefaultRace() {
    const e = this.bootstrapData, t = e?.navigation.find((i) => i.series_id === this.series), s = e?.upcoming.find((i) => i.series_id === this.series);
    this.season = s?.season ?? t?.seasons.at(-1) ?? (/* @__PURE__ */ new Date()).getFullYear(), this.raceId = s?.race_id ?? "";
  }
  syncLive() {
    this.stopLive();
    const e = this.liveEpoch, t = this.client;
    !t || !["Race Center", "Live Timing"].includes(this.section) || (this.liveChain = this.liveChain.then(async () => {
      if (!(e !== this.liveEpoch || !this.isConnected))
        try {
          const s = await t.subscribe(
            this.series,
            (i) => {
              if (e !== this.liveEpoch) return;
              const a = this.liveData?.identity, n = i.identity;
              (a && (a.race_id !== n.race_id || a.run_id !== n.run_id) || i.availability !== "ok") && this.closeDetail(!1), i.session && (!a || a.race_id !== n.race_id) && this.resolveCurrentRace(i, e), this.liveData = i, this.error = void 0, this.requestUpdate();
            },
            (i) => {
              e === this.liveEpoch && (this.error = i, this.liveData = void 0, this.requestUpdate());
            }
          );
          e !== this.liveEpoch || !this.isConnected ? await s() : this.unsubscribe = s;
        } catch (s) {
          e === this.liveEpoch && (this.error = s, this.requestUpdate());
        }
    }));
  }
  async resolveCurrentRace(e, t) {
    this.currentRace = void 0;
    const s = e.identity.race_id;
    if (!s || !this.client) return;
    const i = this.bootstrapData?.upcoming.find(
      (a) => a.series_id === this.series && a.race_id === s
    );
    if (i) {
      this.currentRace = i;
      return;
    }
    try {
      const a = await this.client.schedule({
        series_id: this.series,
        race_id: J(s),
        ...e.identity.season ? { season: e.identity.season } : {}
      });
      if (t !== this.liveEpoch) return;
      const n = a.records.find(
        (c) => c.kind === "race" && c.value?.race_id === s
      );
      if (n?.kind === "race" && n.value) {
        const c = a.records.filter((o) => o.kind === "session" && o.race_id === s).flatMap(
          (o) => o.kind === "session" && o.value && "session_id" in o.value ? [o.value] : []
        );
        this.currentRace = { ...n.value, sessions: c }, this.requestUpdate();
      }
    } catch {
    }
  }
  formatNumber(e, t, s = 0) {
    return b(e, Z(this.hass), s);
  }
  navigate(e) {
    if (e === this.section) return;
    const t = ["Race Center", "Live Timing"].includes(this.section);
    this.section = e, this.closeDetail(!1), t !== ["Race Center", "Live Timing"].includes(e) && this.syncLive(), e === "Race Weekend" && this.loadSchedule(), this.requestUpdate();
  }
  selectSeries(e) {
    e !== this.series && (this.series = e, this.liveData = void 0, this.currentRace = void 0, this.error = void 0, this.closeDetail(!1), this.setDefaultRace(), this.history = void 0, this.analytics = void 0, this.formError = void 0, this.syncLive(), this.section === "Race Weekend" && this.loadSchedule(), this.requestUpdate());
  }
  chooseEntry(e) {
    this.setConfig({ ...this.config, entry_id: e }), this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this.config },
        bubbles: !0,
        composed: !0
      })
    );
  }
  async loadSchedule() {
    if (!this.client) return;
    let e = this.schedules.get(this.series);
    if (e || (e = new ie("schedule", { series_id: this.series }), this.schedules.set(this.series, e)), !e.current && !e.loading) {
      const t = e.load(this.client);
      this.requestUpdate(), await t, this.requestUpdate();
    }
  }
  async page(e, t) {
    if (!this.client) return;
    const s = t === "next" ? e.next(this.client) : t === "previous" ? e.previous(this.client) : e.load(
      this.client,
      t === "restart" ? 0 : e.current?.pagination.offset ?? 0,
      t === "restart"
    );
    this.requestUpdate(), await s, this.requestUpdate();
  }
  async openDriver(e, t) {
    this.closeDetail(!1), this.detailDriver = e, this.detailFocus = t?.composedPath().find((s) => s instanceof HTMLButtonElement), this.requestUpdate(), await this.updateComplete, this.renderRoot.querySelector(".detail-close")?.focus();
  }
  closeDetail(e = !0) {
    this.detail?.invalidate(), this.detail = void 0, this.detailDriver = void 0, this.detailError = void 0, e && this.detailFocus?.focus(), this.detailFocus = void 0, this.requestUpdate();
  }
  async loadDetail(e, t = !1) {
    if (!this.client) return;
    const s = this.epoch;
    try {
      this.detailError = void 0;
      const i = { series_id: this.series, collection: e };
      t || (i.driver_id = J(
        this.detailDriver.driver_id,
        Number.MAX_SAFE_INTEGER
      ));
      const a = new ie(
        t ? "live_scoring" : "live_driver",
        i,
        this.liveData?.identity
      );
      this.detail?.invalidate(), this.detail = a;
      const n = a.load(this.client);
      this.requestUpdate(), await n, s === this.epoch && this.requestUpdate();
    } catch (i) {
      s === this.epoch && (this.detailError = i, this.requestUpdate());
    }
  }
  async submit(e, t = !1) {
    if (e.preventDefault(), !this.client) return;
    const s = e.target, i = new FormData(s);
    try {
      this.formError = void 0;
      const a = Number(i.get("season"));
      if (!Number.isInteger(a) || a < 1948 || a > 9999)
        throw new y("invalid_selection");
      const n = String(i.get("race")), c = J(n), o = i.getAll("dataset").map(String).filter(
        (v) => ke.includes(v)
      );
      if (!o.length) throw new y("invalid_selection");
      const u = {
        series_id: this.series,
        season: a,
        race_id: c,
        datasets: o
      };
      if (t) {
        const v = String(i.get("drivers")).split(",").map((x) => x.trim()).filter(Boolean);
        if (!v.length || v.length > 8 || new Set(v).size !== v.length)
          throw new y("invalid_selection");
        const g = Number(i.get("first")), _ = Number(i.get("last")), f = i.getAll("window").map(Number);
        if (!Number.isInteger(g) || !Number.isInteger(_) || g < 0 || _ > 1e10 || _ < g || _ - g + 1 > 5e3 || v.length * (_ - g + 1) * f.length > 6e4)
          throw new y("invalid_selection");
        Object.assign(u, {
          driver_ids: v.map((x) => J(x)),
          first_lap: g,
          last_lap: _,
          windows: f,
          time_basis: String(i.get("basis"))
        });
      }
      const $ = t ? "analytics" : "history", p = $ + JSON.stringify(u);
      let d = this.snapshots.get(p);
      if (!d) {
        for (const [v, g] of this.snapshots)
          (g.expired || !g.loading && !g.current) && this.snapshots.delete(v);
        if (this.snapshots.size >= 2)
          throw new y("snapshot_limit");
        d = new ie($, u), this.snapshots.set(p, d);
      }
      if (t ? this.analytics = d : this.history = d, this.season = a, this.raceId = n, !d.current) {
        const v = d.load(this.client);
        this.requestUpdate(), await v;
      }
      this.requestUpdate();
    } catch (a) {
      this.formError = a, this.requestUpdate();
    }
  }
  state(e, t, s = !1) {
    return l`<div class=${`state${s ? " loading" : ""}`} role="status">
      <h3>${e}</h3>
      <p class="muted">${t}</p>
    </div>`;
  }
  errorView(e, t) {
    return l`<div class="state error" role="alert">
      <h3>Unable to load this view</h3>
      <p>${Be(e)}</p>
      ${t ? l`<div><button @click=${t}>Retry / reconnect</button></div>` : h}
    </div>`;
  }
  badge(e, t = "neutral") {
    return l`<span class=${`badge ${t}`}>${e}</span>`;
  }
  pager(e) {
    const t = e.current?.pagination;
    return l`${e.expired ? l`<p class="notice">
            Snapshot expired; these are cached historical observations. Restart
            to request a fresh selection.
          </p>` : h}${e.error ? this.errorView(e.error, () => void this.page(e, "retry")) : h}
      <div class="pager">
        <small
          >${t ? `Records ${t.returned ? t.offset + 1 : 0}–${t.offset + t.returned} of ${this.formatNumber(t.total)} · ${e.records.length} retained in this view` : "No records loaded"}${e.loading ? " · Loading…" : ""}</small
        >
        <div class="actions">
          <button
            ?disabled=${e.loading || !e.canPrevious}
            @click=${() => void this.page(e, "previous")}
          >
            Previous</button
          ><button
            ?disabled=${e.loading || t?.next_offset == null}
            @click=${() => void this.page(e, "next")}
          >
            Next page</button
          >${e.error || e.expired ? l`<button
                ?disabled=${e.loading}
                @click=${() => void this.page(e, "restart")}
              >
                Restart selection
              </button>` : h}
        </div>
      </div>`;
  }
  renderOverview() {
    const e = this.bootstrapData, t = this.liveData, s = t?.session, i = s ? this.currentRace : e.upcoming.find((d) => d.series_id === this.series), a = e.upcoming.find((d) => d.series_id === this.series), n = [
      i?.start_time,
      ...(i?.sessions ?? []).map((d) => d.start_time)
    ].filter(
      (d) => !!d && M(d) !== null && M(d) > Date.now()
    ).sort((d, v) => M(d) - M(v))[0], c = se(t), o = Re(t), u = t?.leaderboard?.find(
      (d) => d.driver_id === t.leader_driver_id
    ), $ = $t(n), p = t?.leaderboard?.filter((d) => d.favorite) ?? [];
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">Your race day, in focus</p>
          <h2>Race Center</h2>
        </div>
        ${this.badge(c.text, c.tone)}
      </div>
      <section class="panel hero">
        <div class="hero-content">
          <p class="eyebrow">
            ${U[this.series]} ·
            ${s ? "Reported session" : i ? "Next known event" : "Schedule & live coverage"}
          </p>
          <h1>
            ${s?.run_name ?? i?.name ?? "Waiting for the next green flag."}
          </h1>
          <p class="hero-track">
            ${i?.track ?? "Track not reported"}${i?.season ? ` · ${i.season}` : ""}
          </p>
          <div class="actions">
            ${s ? this.badge(o.text, o.tone) : this.badge(i?.status ?? "No active session")}${s ? this.badge(
      `${m(s.status)} · ${m(s.progress)}`
    ) : h}
          </div>
          <div class="actions">
            <button
              class="primary"
              @click=${() => this.navigate("Live Timing")}
            >
              Open live timing ↗</button
            ><button @click=${() => this.navigate("Race Weekend")}>
              Race weekend
            </button>
          </div>
        </div>
        <div class="hero-side">
          ${s ? l`<div>
                  <p class="eyebrow">Reported lap</p>
                  <p class="lap-count">
                    ${this.formatNumber(s.lap)}
                    <span>/ ${this.formatNumber(s.total_laps)}</span>
                  </p>
                </div>
                ${s.lap !== null && s.total_laps !== null && s.total_laps > 0 ? l`<div
                      class="progress"
                      role="meter"
                      aria-label="Reported session laps"
                      aria-valuemin="0"
                      aria-valuemax=${s.total_laps}
                      aria-valuenow=${Math.min(s.lap, s.total_laps)}
                    >
                      <div
                        style=${`width:${Math.max(0, Math.min(100, s.lap / s.total_laps * 100))}%`}
                      ></div>
                    </div>` : h}
                <p>
                  <small>Leading the reported field</small><br /><strong
                    >${u?.name ?? "Leader unavailable"}</strong
                  >
                </p>` : l`<div>
                  <p class="eyebrow">
                    ${$ ? "Starts in" : "Event time"}
                  </p>
                  <p class="lap-count">${$ ?? "—"}</p>
                </div>
                <p>
                  ${E(n, this.hass)}<br /><small
                    >${$ ? "Known future instant" : "No reliable future instant available"}</small
                  >
                </p>`}
        </div>
      </section>
      <div class="stat-grid">
        <div class="stat">
          <span>Reported entries</span
          ><strong>${this.formatNumber(t?.reported_count)}</strong>
        </div>
        <div class="stat">
          <span>Laps remaining</span
          ><strong>${this.formatNumber(s?.laps_remaining)}</strong>
        </div>
        <div class="stat">
          <span>Stage observation</span
          ><strong>${this.formatNumber(s?.stage?.number)}</strong>
        </div>
      </div>
      <div class="two-col">
        <section class="stack">
          <div class="row">
            <h3>Following the field</h3>
            <small>Integration favorites</small>
          </div>
          ${p.length ? l`<div class="favorite-grid">
                ${p.map(
      (d) => l`<button
                      class="panel favorite"
                      @click=${(v) => void this.openDriver(d, v)}
                    >
                      <span class="row"
                        ><span class="car">${d.car_number ?? "—"}</span
                        ><span class="position"
                          >P${this.formatNumber(d.position)}</span
                        ></span
                      ><strong>${d.name ?? `Driver ${d.driver_id}`}</strong
                      ><small
                        >★ Favorite ·
                        ${d.running_status ?? "Status unknown"}</small
                      >
                    </button>`
    )}
              </div>` : l`<div class="panel">
                <p>
                  ${e.favorite_driver_ids.length ? "Favorite timing is unavailable for this series." : "Choose favorite drivers in the integration options."}
                </p>
                ${e.references.drivers.map(
      (d) => l`<p class="muted">★ ${d.name} · ${d.driver_id}</p>`
    )}
              </div>`}
        </section>
        <section class="panel stack">
          <h3>${s ? "Next known weekend" : "Weekend notebook"}</h3>
          ${a?.sessions?.length ? a.sessions.map(
      (d) => l`<div>
                    <p>${d.name} <small>· ${m(d.kind)}</small></p>
                    <small>${E(d.start_time, this.hass)}</small>
                  </div>`
    ) : l`<p class="muted">
                ${a ? "Session times are not confirmed." : "No scheduled future event in the retained catalog. Open Race Weekend for retained events or use an explicit historical race key."}
              </p>`}<button
            class="quiet"
            @click=${() => this.navigate("History")}
          >
            Explore race history →
          </button>
        </section>
      </div>
      ${s ? h : this.state(
      "Session coverage",
      t ? `${m(t.availability)}. Timing appears only when the source supplies fresh matching observations.` : "Waiting for the first live source snapshot.",
      !t
    )}${this.renderDetail()}
    </div>`;
  }
  renderTiming() {
    const e = this.liveData, t = e?.session, s = se(e), i = Re(e);
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${U[this.series]} · Timing tower</p>
          <h2>${t?.run_name ?? "Live Timing"}</h2>
          <p class="muted">
            ${m(t?.status)}${t ? ` · Reported lap ${this.formatNumber(t.lap)} / ${this.formatNumber(t.total_laps)}` : ""}
          </p>
        </div>
        <div class="actions">
          ${this.badge(s.text, s.tone)}${t ? this.badge(i.text, i.tone) : h}
        </div>
      </div>
      ${e?.leaderboard?.length ? l`<nrc-leaderboard
            .rows=${e.leaderboard}
            .hass=${this.hass}
            @driver-open=${(a) => void this.openDriver(a.detail, a)}
          ></nrc-leaderboard>` : this.state(
      e ? "No current timing" : "Connecting to the timing feed",
      e ? `${m(e.availability)}. Fresh matching observations are required; stale results are withheld.` : "Waiting for an authenticated live snapshot.",
      !e
    )}${t?.stage ? l`<div class="notice">
            Reported stage ${this.formatNumber(t.stage.number)} · finish
            at lap ${this.formatNumber(t.stage.finish_at_lap)} · stage
            laps ${this.formatNumber(t.stage.laps_in_stage)}. Provisional
            observations.
          </div>` : h}${e ? l`<section class="panel stack">
            <h3>Associated scoring observations</h3>
            <div class="actions">
              ${["pits", "stages", "points"].map(
      (a) => l`<button @click=${() => void this.loadDetail(a, !0)}>
                    ${m(a)} · ${m(e.scoring[a]?.status)}
                  </button>`
    )}
            </div>
            <p class="muted">
              <small
                >Only supported associations are shown. No championship or
                strategy conclusions.</small
              >
            </p>
          </section>` : h}${e?.omitted_count ? l`<p class="notice">
            Source normalizer omitted ${e.omitted_count} entries. This is not
            a complete official entry list.
          </p>` : h}${this.renderDetail()}
    </div>`;
  }
  renderDetail() {
    const e = this.detailDriver, t = this.detail;
    return !e && !t && !this.detailError ? h : l`<section
      class="panel stack detail-panel"
      aria-label="Driver and scoring details"
      @keydown=${(s) => {
      s.key === "Escape" && this.closeDetail();
    }}
    >
      <div class="row">
        <h3>
          ${e ? `${e.name ?? e.driver_id} · #${e.car_number ?? "—"}` : `${m(t?.selection.collection)} observations`}
        </h3>
        <button class="detail-close" @click=${() => this.closeDetail()}>
          Close
        </button>
      </div>
      ${e ? l`<div class="stat-grid">
              <div class="stat">
                <span>Position</span
                ><strong>${this.formatNumber(e.position)}</strong>
              </div>
              <div class="stat">
                <span>Best lap*</span
                ><strong
                  >${this.formatNumber(e.best_lap_time, void 0, 3)}</strong
                >
              </div>
              <div class="stat">
                <span>Laps</span
                ><strong>${this.formatNumber(e.laps_completed)}</strong>
              </div>
            </div>
            <p class="muted">
              <small
                >* Source unit unverified. Pit stops and laps-led intervals
                retain reported boundaries.</small
              >
            </p>
            <div class="actions">
              <button @click=${() => void this.loadDetail("pit_stops")}>
                Load pit observations</button
              ><button @click=${() => void this.loadDetail("laps_led")}>
                Load laps-led intervals
              </button>
            </div>
            <details>
              <summary>Reported driver measurements</summary>
              ${z(e)}
            </details>` : h}${this.detailError ? this.errorView(this.detailError) : h}${t ? l`${t.current ? l`<p class="muted">
                  ${m(t.current.availability)} · ${m(t.current.reason)}
                  · Race ${t.current.identity?.race_id ?? "Unknown"} / timing
                  run ${t.current.identity?.run_id ?? "Unknown"}
                </p>
                ${t.current.provenance ? l`<details>
                      <summary>Source provenance</summary>
                      ${z(t.current.provenance)}
                    </details>` : h}
                <p class="notice">
                  Provisional reported observations. Source timing units remain
                  unverified.
                </p>
                ${t.current.records.length ? G(t.current.records) : this.state(
      "No detail records",
      "This source has no supported records for the selected collection."
    )}` : t.loading ? this.state(
      "Loading observations",
      "Requesting only the selected detail collection.",
      !0
    ) : h}${this.pager(t)}` : h}
    </section>`;
  }
  renderWeekend() {
    const e = this.schedules.get(this.series), t = e?.current?.records ?? [], s = t.filter((a) => a.kind === "race"), i = t.filter((a) => a.kind === "session");
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${U[this.series]} · Retained schedule</p>
          <h2>Race Weekend</h2>
          <p class="muted">
            Known events and sessions ·
            ${this.hass?.config?.time_zone ?? "browser local time"}
          </p>
        </div>
        ${this.badge(
      this.bootstrapData?.source_state.find(
        (a) => a.series_id === this.series
      )?.schedule ?? "unknown"
    )}
      </div>
      ${this.bootstrapData?.navigation.find((a) => a.series_id === this.series)?.failed_seasons.length ? l`<p class="notice">
            Some retained seasons are unavailable. Available peers do not
            establish full schedule coverage.
          </p>` : h}
      <div class="schedule">
        ${s.map((a) => {
      const n = a.value, c = this.bootstrapData?.references.tracks.find(
        (o) => o.track_id === n.track_id
      );
      return l`<article class="panel event-card">
            <div class="event-number">${n.season ?? "—"}</div>
            <div>
              <p class="eyebrow">${n.track ?? "Track unknown"}</p>
              <h3>${n.name}</h3>
              <p class="muted">
                ${E(n.start_time, this.hass)} · ${m(n.status)}
              </p>
              ${c ? l`<small
                    >${c.city ?? ""}${c.state ? `, ${c.state}` : ""}
                    · ${m(c.track_type)} ·
                    ${this.formatNumber(c.length_miles, void 0, 2)}
                    reported miles</small
                  >` : h}
              <div class="sessions">
                ${i.filter(
        (o) => o.race_id === n.race_id && o.season === n.season
      ).map((o) => {
        const u = o.value;
        return "session_id" in u ? l`<div class="session-row">
                          <span
                            >${u.name} <small>· ${m(u.kind)}</small></span
                          ><span
                            >${E(u.start_time, this.hass)}<small>
                              · ${m(u.status)}</small
                            ></span
                          >
                        </div>` : h;
      })}
              </div>
              ${n.sessions_failed ? l`<p class="notice">
                    Session enrichment unavailable; race schedule retained.
                  </p>` : h}
            </div>
            <div class="actions">
              <button
                ?disabled=${n.season === null}
                @click=${() => {
        n.season && (this.season = n.season, this.raceId = n.race_id, this.history = void 0, this.navigate("History"));
      }}
              >
                Select race →
              </button>
            </div>
          </article>`;
    })}${i.filter(
      (a) => !s.some(
        (n) => n.value?.race_id === a.race_id && n.value?.season === a.season
      )
    ).length ? l`<p class="notice">
                This page continues the preceding race's sessions. Parent race
                IDs are retained below.
              </p>
              ${G(
      i.filter(
        (a) => !s.some(
          (n) => n.value?.race_id === a.race_id && n.value?.season === a.season
        )
      )
    )}` : h}${t.length ? h : this.state(
      e?.loading ? "Loading retained events" : "No scheduled events",
      e?.loading ? "Reading the integration’s retained schedule catalog." : "The retained catalog contains no events for this series. Historical lookup remains available.",
      e?.loading
    )}
      </div>
      ${e ? this.pager(e) : h}
    </div>`;
  }
  renderForm(e) {
    const t = this.bootstrapData?.navigation.find(
      (n) => n.series_id === this.series
    ), s = e ? this.analytics?.selection : this.history?.selection, i = s?.datasets ?? (e ? ["laps", "weekend"] : ["weekend"]), a = [...this.schedules.get(this.series)?.records ?? []].filter((n) => n.kind === "race").map((n) => n.value).concat(
      this.bootstrapData?.upcoming.filter(
        (n) => n.series_id === this.series
      ) ?? []
    ).filter(
      (n, c, o) => o.findIndex(
        (u) => u.race_id === n.race_id && u.season === n.season
      ) === c
    );
    return l`<form
      class="panel stack"
      @submit=${(n) => void this.submit(n, e)}
    >
      <div class="filters">
        <label class="field"
          >Series<select
            aria-label="Historical series"
            .value=${String(this.series)}
            @change=${(n) => this.selectSeries(Number(n.target.value))}
          >
            ${this.bootstrapData.series_ids.map(
      (n) => l`<option value=${n}>${U[n]}</option>`
    )}
          </select></label
        ><label class="field"
          >Season<input
            name="season"
            type="number"
            required
            min="1948"
            max="9999"
            .value=${String(s?.season ?? this.season)}
            list="retained-seasons" /></label
        ><datalist id="retained-seasons">
          ${t?.seasons.map((n) => l`<option value=${n}></option>`)}</datalist
        ><label class="field wide"
          >Known retained race<select
            @change=${(n) => {
      const [c, o] = n.target.value.split(":");
      if (o) {
        this.season = Number(c), this.raceId = o;
        const u = n.target.closest("form");
        u.elements.namedItem("season").value = c, u.elements.namedItem("race").value = o;
      }
    }}
          >
            <option value="">
              Choose a retained race or enter a key below
            </option>
            ${a.map(
      (n) => l`<option value=${`${n.season}:${n.race_id}`}>
                  ${n.season ?? "?"} · ${n.name} · ${n.race_id}
                </option>`
    )}
          </select></label
        ><label class="field"
          >Race ID · manual key<input
            name="race"
            required
            inputmode="numeric"
            pattern="[0-9]+"
            .value=${String(s?.race_id ?? this.raceId)}
            placeholder="e.g. 88001"
        /></label>
      </div>
      <div class="filters">
        <fieldset>
          <legend>Explicit datasets</legend>
          ${ke.map(
      (n) => l`<label class="check"
                ><input
                  type="checkbox"
                  name="dataset"
                  value=${n}
                  .checked=${i.includes(n)}
                />
                ${m(n)}</label
              >`
    )}
        </fieldset>
      </div>
      ${e ? l`<div class="filters">
              <label class="field wide"
                >NASCAR driver IDs · comma separated, 1–8<input
                  name="drivers"
                  required
                  .value=${s?.driver_ids?.join(", ") ?? this.bootstrapData.favorite_driver_ids.slice(0, 2).join(
      ", "
    )}
                  placeholder="99002, 99003" /></label
              ><label class="field"
                >First lap<input
                  type="number"
                  name="first"
                  min="0"
                  max="10000000000"
                  required
                  .value=${String(s?.first_lap ?? 1)} /></label
              ><label class="field"
                >Last lap<input
                  type="number"
                  name="last"
                  min="0"
                  max="10000000000"
                  required
                  .value=${String(s?.last_lap ?? 100)} /></label
              ><label class="field wide"
                >Comparison time basis<select
                  name="basis"
                  .value=${s?.time_basis ?? "all_available"}
                >
                  <option value="all_available">
                    All available valid laps per driver
                  </option>
                  <option value="overlapping_valid_laps">
                    Overlapping valid laps across selected drivers
                  </option>
                </select></label
              >
              <fieldset>
                <legend>Consecutive lap windows</legend>
                ${[5, 10, 15, 20, 25, 30].map(
      (n) => l`<label class="check"
                      ><input
                        name="window"
                        type="checkbox"
                        value=${n}
                        .checked=${(s?.windows ?? [5]).includes(n)}
                      />${n}</label
                    >`
    )}
              </fieldset>
            </div>
            <p class="muted">
              <small
                >Up to 5,000 lap numbers; drivers × lap span × window count ≤
                60,000. Missing data is preserved. Select loop, averages or
                stages to include supported reported statistics.</small
              >
            </p>` : h}
      <p class="muted">
        <small
          >Manual keys permit valid selections outside the retained schedule;
          endpoint coverage is unverified across seasons. Datasets are requested
          only on submission. At most two five-minute snapshots per user, four
          globally.</small
        >
      </p>
      <div>
        <button
          class="primary"
          type="submit"
          ?disabled=${(e ? this.analytics : this.history)?.loading}
        >
          ${e ? "Analyze selection" : "Load race records"}
        </button>
      </div>
      ${this.formError ? this.errorView(this.formError) : h}
    </form>`;
  }
  renderHistory() {
    const e = this.history, t = e?.current;
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">The race archive</p>
          <h2>History</h2>
          <p class="muted">
            Reported results, session records and source observations.
          </p>
        </div>
      </div>
      ${this.renderForm(!1)}${t ? l`<div class="section-head">
              <h3>
                ${t.records.find((s) => s.kind === "weekend")?.value?.name ?? `Race ${t.race?.race_id ?? this.raceId}`}
              </h3>
              ${this.badge(m(t.status))}
            </div>
            ${De(t, this.hass)}${_t(
      t.records,
      this.hass
    )}${t.records.length ? l`<details>
                  <summary>
                    Explore ${t.records.length} records on this page ·
                    metadata, stages, laps, notes & pits
                  </summary>
                  ${G(t.records)}
                </details>` : this.state(
      "No historical records",
      "This selection returned no records. Review dataset availability above."
    )}` : e?.loading ? this.state(
      "Loading historical selection",
      "Building one immutable snapshot for the explicitly selected datasets.",
      !0
    ) : this.state(
      "Choose a race to begin",
      "Select a season and retained race, or enter a valid manual race key."
    )}${e ? this.pager(e) : h}
    </div>`;
  }
  renderAnalytics() {
    const e = this.analytics, t = e?.current, s = e?.records ?? [], i = this.chartMode === "window" ? s.filter((a) => a.kind !== "window" || a.size === this.chartWindow) : s;
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">Understand the observations</p>
          <h2>Analytics</h2>
          <p class="muted">
            Interactive comparisons from Phase 4B analytics · no inferred
            strategy.
          </p>
        </div>
      </div>
      ${this.renderForm(!0)}${t ? l`<div class="row">
              <h3>
                Selected race ${t.query?.key.race_id ?? "—"} · laps
                ${t.query?.first_lap ?? "—"}–${t.query?.last_lap ?? "—"}
              </h3>
              ${this.badge(m(t.status))}
            </div>
            <p class="notice">
              ${m(t.query?.time_basis)} · ${m(t.reason)}. Charts
              and summaries contain loaded pages only. Continue paging for later
              drivers, comparisons and reported performance; retention is
              bounded to 1,600 records.
            </p>
            ${De(t, this.hass)}
            <div class="filters">
              <label class="field"
                >Chart<select
                  .value=${this.chartMode}
                  @change=${(a) => {
      this.chartMode = a.target.value, this.requestUpdate();
    }}
                >
                  <option value="time">Lap-time progression</option>
                  <option value="position">Position progression</option>
                  <option value="delta">Consecutive-lap change</option>
                  <option value="window">Consecutive-window mean</option>
                </select></label
              >${this.chartMode === "window" ? l`<label class="field"
                    >Window<select
                      .value=${String(this.chartWindow)}
                      @change=${(a) => {
      this.chartWindow = Number(
        a.target.value
      ), this.requestUpdate();
    }}
                    >
                      ${t.query?.windows.map(
      (a) => l`<option value=${a}>${a} laps</option>`
    )}
                    </select></label
                  >` : h}
            </div>
            <nrc-chart
              .rows=${i}
              .mode=${this.chartMode}
              .locale=${Z(this.hass)}
            ></nrc-chart>
            <nrc-metric-chart
              .rows=${s}
              .locale=${Z(this.hass)}
            ></nrc-metric-chart>
            ${s.filter((a) => a.kind === "driver").map(
      (a) => l`<section class="stack">
                    <h3>
                      Driver ${a.driver_id} · ${m(a.value?.status)} ·
                      fastest recorded lap
                      ${this.formatNumber(a.value?.fastest_lap)}
                    </h3>
                    <div class="metric-grid">
                      ${a.value?.metrics.map(
        (n) => Ne(n, this.hass?.locale?.language)
      )}
                    </div>
                    <details>
                      <summary>Coverage and exclusions</summary>
                      ${z(a.value?.coverage)}
                      <p>${m(a.value?.reason)}</p>
                    </details>
                  </section>`
    )}${t.race_metrics?.length ? l`<div class="metric-grid">
                  ${t.race_metrics.map(
      (a) => Ne(a, this.hass?.locale?.language)
    )}
                </div>` : h}
            <details>
              <summary>
                Comparisons, consecutive windows & reported performance ·
                current page
              </summary>
              ${G(t.records.filter((a) => a.kind !== "samples"))}
            </details>
            <details>
              <summary>Analytics caveats</summary>
              ${t.caveats?.map((a) => l`<p>${m(a)}</p>`)}
            </details>` : e?.loading ? this.state(
      "Calculating selected observations",
      "The backend applies the existing analytics contract and computation limits.",
      !0
    ) : this.state(
      "Build a comparison",
      "Choose drivers, lap range, datasets and a supported window."
    )}${e ? this.pager(e) : h}
    </div>`;
  }
  render() {
    const e = this.bootstrapData, t = se(this.liveData);
    return l`<ha-card
      ><header class="masthead">
        <div class="brand">
          <span class="brand-mark" aria-hidden="true"
            ><i></i><i></i><i></i
          ></span>
          <div>
            <p class="brand-title">
              ${this.config.title ?? "NASCAR Race Center"}
            </p>
            <p class="eyebrow">Race intelligence · Home Assistant</p>
          </div>
        </div>
        ${e ? l`<div class="tools">
              <label class="series-label"
                ><span class="eyebrow">Series</span
                ><select
                  aria-label="Selected series"
                  .value=${String(this.series)}
                  @change=${(s) => this.selectSeries(
      Number(s.target.value)
    )}
                >
                  ${e.series_ids.map(
      (s) => l`<option value=${s}>${U[s]}</option>`
    )}
                </select></label
              >
            </div>` : h}
      </header>
      ${e?.provider === "demo" ? l`<div class="demo" role="note">
            DEMONSTRATION · Simulated races & drivers · not genuine NASCAR
            results · offline provider
          </div>` : h}${e ? l`<nav class="nav" aria-label="Race Center sections">
            ${ne.map(
      (s) => l`<button
                  aria-current=${s === this.section ? "page" : h}
                  @click=${() => this.navigate(s)}
                >
                  ${s}
                </button>`
    )}
          </nav>` : h}
      <main aria-busy=${this.loading ? "true" : "false"}>
        ${this.loading ? this.state(
      "Preparing your Race Center",
      "Connecting through Home Assistant’s authenticated WebSocket API.",
      !0
    ) : h}${this.error ? this.errorView(this.error, () => this.scheduleStart()) : h}${!this.config.entry_id && !this.loading && !this.error ? l`<div class="state">
              <h2>Select an integration entry</h2>
              <p>
                Dashboard API v1 requires administrator access. Choose a loaded
                entry or set <code>entry_id</code> in the card editor. The card
                never infers entries from entity names.
              </p>
              <label class="field"
                >NASCAR Race Center entry<select
                  @change=${(s) => {
      const i = s.target.value;
      i && this.chooseEntry(i);
    }}
                >
                  <option value="">Select an entry</option>
                  ${this.entries.map(
      (s) => l`<option
                        ?disabled=${s.state !== "loaded"}
                        value=${s.entry_id}
                      >
                        ${s.title} · ${s.state}
                      </option>`
    )}
                </select></label
              >${this.entries.length ? h : l`<p class="muted">
                    No entries found. Add the NASCAR Race Center integration,
                    then reconnect.
                  </p>`}
            </div>` : h}${e ? this.section === "Race Center" ? this.renderOverview() : this.section === "Live Timing" ? this.renderTiming() : this.section === "Race Weekend" ? this.renderWeekend() : this.section === "History" ? this.renderHistory() : this.renderAnalytics() : h}
      </main>
      <footer class="source">
        <span
          >${e ? `${e.provider === "demo" ? "Simulated" : "Experimental"} source · ${m(this.section === "History" || this.section === "Analytics" ? "on_demand_snapshot" : t.text)}` : "Authenticated dashboard API v1"}</span
        ><span
          >Content updated:
          ${E(this.liveData?.source_updated_at, this.hass)}</span
        ><span>Card ${It} · API v1</span>
      </footer></ha-card
    >`;
  }
}
customElements.define("nascar-race-center-card", Lt);
const oe = window;
oe.customCards ??= [];
oe.customCards.some((r) => r.type === "nascar-race-center-card") || oe.customCards.push({
  type: "nascar-race-center-card",
  name: "NASCAR Race Center",
  description: "Five racing views with authenticated dashboard API v1. Administrator access required.",
  preview: !0
});
export {
  Lt as NascarRaceCenterCard,
  It as VERSION
};
