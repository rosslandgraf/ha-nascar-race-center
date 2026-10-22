/*! NASCAR Race Center card 0.5.1
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
const ie = globalThis, ge = ie.ShadowRoot && (ie.ShadyCSS === void 0 || ie.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, ve = Symbol(), ye = /* @__PURE__ */ new WeakMap();
let Oe = class {
  constructor(e, t, i) {
    if (this._$cssResult$ = !0, i !== ve) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = t;
  }
  get styleSheet() {
    let e = this.o;
    const t = this.t;
    if (ge && e === void 0) {
      const i = t !== void 0 && t.length === 1;
      i && (e = ye.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), i && ye.set(t, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Xe = (r) => new Oe(typeof r == "string" ? r : r + "", void 0, ve), re = (r, ...e) => {
  const t = r.length === 1 ? r[0] : e.reduce((i, s, a) => i + ((n) => {
    if (n._$cssResult$ === !0) return n.cssText;
    if (typeof n == "number") return n;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + n + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(s) + r[a + 1], r[0]);
  return new Oe(t, r, ve);
}, Qe = (r, e) => {
  if (ge) r.adoptedStyleSheets = e.map((t) => t instanceof CSSStyleSheet ? t : t.styleSheet);
  else for (const t of e) {
    const i = document.createElement("style"), s = ie.litNonce;
    s !== void 0 && i.setAttribute("nonce", s), i.textContent = t.cssText, r.appendChild(i);
  }
}, xe = ge ? (r) => r : (r) => r instanceof CSSStyleSheet ? ((e) => {
  let t = "";
  for (const i of e.cssRules) t += i.cssText;
  return Xe(t);
})(r) : r;
const { is: et, defineProperty: tt, getOwnPropertyDescriptor: it, getOwnPropertyNames: st, getOwnPropertySymbols: rt, getPrototypeOf: at } = Object, ae = globalThis, _e = ae.trustedTypes, nt = _e ? _e.emptyScript : "", ot = ae.reactiveElementPolyfillSupport, G = (r, e) => r, pe = { toAttribute(r, e) {
  switch (e) {
    case Boolean:
      r = r ? nt : null;
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
} }, Fe = (r, e) => !et(r, e), we = { attribute: !0, type: String, converter: pe, reflect: !1, useDefault: !1, hasChanged: Fe };
Symbol.metadata ??= Symbol("metadata"), ae.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
let H = class extends HTMLElement {
  static addInitializer(e) {
    this._$Ei(), (this.l ??= []).push(e);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(e, t = we) {
    if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
      const i = Symbol(), s = this.getPropertyDescriptor(e, i, t);
      s !== void 0 && tt(this.prototype, e, s);
    }
  }
  static getPropertyDescriptor(e, t, i) {
    const { get: s, set: a } = it(this.prototype, e) ?? { get() {
      return this[t];
    }, set(n) {
      this[t] = n;
    } };
    return { get: s, set(n) {
      const d = s?.call(this);
      a?.call(this, n), this.requestUpdate(e, d, i);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) ?? we;
  }
  static _$Ei() {
    if (this.hasOwnProperty(G("elementProperties"))) return;
    const e = at(this);
    e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(G("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(G("properties"))) {
      const t = this.properties, i = [...st(t), ...rt(t)];
      for (const s of i) this.createProperty(s, t[s]);
    }
    const e = this[Symbol.metadata];
    if (e !== null) {
      const t = litPropertyMetadata.get(e);
      if (t !== void 0) for (const [i, s] of t) this.elementProperties.set(i, s);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t, i] of this.elementProperties) {
      const s = this._$Eu(t, i);
      s !== void 0 && this._$Eh.set(s, t);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(e) {
    const t = [];
    if (Array.isArray(e)) {
      const i = new Set(e.flat(1 / 0).reverse());
      for (const s of i) t.unshift(xe(s));
    } else e !== void 0 && t.push(xe(e));
    return t;
  }
  static _$Eu(e, t) {
    const i = t.attribute;
    return i === !1 ? void 0 : typeof i == "string" ? i : typeof e == "string" ? e.toLowerCase() : void 0;
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
    for (const i of t.keys()) this.hasOwnProperty(i) && (e.set(i, this[i]), delete this[i]);
    e.size > 0 && (this._$Ep = e);
  }
  createRenderRoot() {
    const e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return Qe(e, this.constructor.elementStyles), e;
  }
  connectedCallback() {
    this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(!0), this._$EO?.forEach((e) => e.hostConnected?.());
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((e) => e.hostDisconnected?.());
  }
  attributeChangedCallback(e, t, i) {
    this._$AK(e, i);
  }
  _$ET(e, t) {
    const i = this.constructor.elementProperties.get(e), s = this.constructor._$Eu(e, i);
    if (s !== void 0 && i.reflect === !0) {
      const a = (i.converter?.toAttribute !== void 0 ? i.converter : pe).toAttribute(t, i.type);
      this._$Em = e, a == null ? this.removeAttribute(s) : this.setAttribute(s, a), this._$Em = null;
    }
  }
  _$AK(e, t) {
    const i = this.constructor, s = i._$Eh.get(e);
    if (s !== void 0 && this._$Em !== s) {
      const a = i.getPropertyOptions(s), n = typeof a.converter == "function" ? { fromAttribute: a.converter } : a.converter?.fromAttribute !== void 0 ? a.converter : pe;
      this._$Em = s;
      const d = n.fromAttribute(t, a.type);
      this[s] = d ?? this._$Ej?.get(s) ?? d, this._$Em = null;
    }
  }
  requestUpdate(e, t, i, s = !1, a) {
    if (e !== void 0) {
      const n = this.constructor;
      if (s === !1 && (a = this[e]), i ??= n.getPropertyOptions(e), !((i.hasChanged ?? Fe)(a, t) || i.useDefault && i.reflect && a === this._$Ej?.get(e) && !this.hasAttribute(n._$Eu(e, i)))) return;
      this.C(e, t, i);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(e, t, { useDefault: i, reflect: s, wrapped: a }, n) {
    i && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(e) && (this._$Ej.set(e, n ?? t ?? this[e]), a !== !0 || n !== void 0) || (this._$AL.has(e) || (this.hasUpdated || i || (t = void 0), this._$AL.set(e, t)), s === !0 && this._$Em !== e && (this._$Eq ??= /* @__PURE__ */ new Set()).add(e));
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
        for (const [s, a] of this._$Ep) this[s] = a;
        this._$Ep = void 0;
      }
      const i = this.constructor.elementProperties;
      if (i.size > 0) for (const [s, a] of i) {
        const { wrapped: n } = a, d = this[s];
        n !== !0 || this._$AL.has(s) || d === void 0 || this.C(s, void 0, a, d);
      }
    }
    let e = !1;
    const t = this._$AL;
    try {
      e = this.shouldUpdate(t), e ? (this.willUpdate(t), this._$EO?.forEach((i) => i.hostUpdate?.()), this.update(t)) : this._$EM();
    } catch (i) {
      throw e = !1, this._$EM(), i;
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
H.elementStyles = [], H.shadowRootOptions = { mode: "open" }, H[G("elementProperties")] = /* @__PURE__ */ new Map(), H[G("finalized")] = /* @__PURE__ */ new Map(), ot?.({ ReactiveElement: H }), (ae.reactiveElementVersions ??= []).push("2.1.2");
const fe = globalThis, ke = (r) => r, se = fe.trustedTypes, Ae = se ? se.createPolicy("lit-html", { createHTML: (r) => r }) : void 0, je = "$lit$", R = `lit$${Math.random().toFixed(9).slice(2)}$`, We = "?" + R, lt = `<${We}>`, T = document, Z = () => T.createComment(""), Y = (r) => r === null || typeof r != "object" && typeof r != "function", $e = Array.isArray, dt = (r) => $e(r) || typeof r?.[Symbol.iterator] == "function", le = `[ 	
\f\r]`, B = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, Se = /-->/g, Ce = />/g, D = RegExp(`>|${le}(?:([^\\s"'>=/]+)(${le}*=${le}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), Ee = /'/g, Re = /"/g, Be = /^(?:script|style|textarea|title)$/i, Ve = (r) => (e, ...t) => ({ _$litType$: r, strings: e, values: t }), l = Ve(1), M = Ve(2), I = Symbol.for("lit-noChange"), h = Symbol.for("lit-nothing"), De = /* @__PURE__ */ new WeakMap(), z = T.createTreeWalker(T, 129);
function Ke(r, e) {
  if (!$e(r) || !r.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return Ae !== void 0 ? Ae.createHTML(e) : e;
}
const ct = (r, e) => {
  const t = r.length - 1, i = [];
  let s, a = e === 2 ? "<svg>" : e === 3 ? "<math>" : "", n = B;
  for (let d = 0; d < t; d++) {
    const o = r[d];
    let u, b, p = -1, c = 0;
    for (; c < o.length && (n.lastIndex = c, b = n.exec(o), b !== null); ) c = n.lastIndex, n === B ? b[1] === "!--" ? n = Se : b[1] !== void 0 ? n = Ce : b[2] !== void 0 ? (Be.test(b[2]) && (s = RegExp("</" + b[2], "g")), n = D) : b[3] !== void 0 && (n = D) : n === D ? b[0] === ">" ? (n = s ?? B, p = -1) : b[1] === void 0 ? p = -2 : (p = n.lastIndex - b[2].length, u = b[1], n = b[3] === void 0 ? D : b[3] === '"' ? Re : Ee) : n === Re || n === Ee ? n = D : n === Se || n === Ce ? n = B : (n = D, s = void 0);
    const m = n === D && r[d + 1].startsWith("/>") ? " " : "";
    a += n === B ? o + lt : p >= 0 ? (i.push(u), o.slice(0, p) + je + o.slice(p) + R + m) : o + R + (p === -2 ? d : m);
  }
  return [Ke(r, a + (r[t] || "<?>") + (e === 2 ? "</svg>" : e === 3 ? "</math>" : "")), i];
};
class X {
  constructor({ strings: e, _$litType$: t }, i) {
    let s;
    this.parts = [];
    let a = 0, n = 0;
    const d = e.length - 1, o = this.parts, [u, b] = ct(e, t);
    if (this.el = X.createElement(u, i), z.currentNode = this.el.content, t === 2 || t === 3) {
      const p = this.el.content.firstChild;
      p.replaceWith(...p.childNodes);
    }
    for (; (s = z.nextNode()) !== null && o.length < d; ) {
      if (s.nodeType === 1) {
        if (s.hasAttributes()) for (const p of s.getAttributeNames()) if (p.endsWith(je)) {
          const c = b[n++], m = s.getAttribute(p).split(R), $ = /([.?@])?(.*)/.exec(c);
          o.push({ type: 1, index: a, name: $[2], strings: m, ctor: $[1] === "." ? pt : $[1] === "?" ? ut : $[1] === "@" ? mt : ne }), s.removeAttribute(p);
        } else p.startsWith(R) && (o.push({ type: 6, index: a }), s.removeAttribute(p));
        if (Be.test(s.tagName)) {
          const p = s.textContent.split(R), c = p.length - 1;
          if (c > 0) {
            s.textContent = se ? se.emptyScript : "";
            for (let m = 0; m < c; m++) s.append(p[m], Z()), z.nextNode(), o.push({ type: 2, index: ++a });
            s.append(p[c], Z());
          }
        }
      } else if (s.nodeType === 8) if (s.data === We) o.push({ type: 2, index: a });
      else {
        let p = -1;
        for (; (p = s.data.indexOf(R, p + 1)) !== -1; ) o.push({ type: 7, index: a }), p += R.length - 1;
      }
      a++;
    }
  }
  static createElement(e, t) {
    const i = T.createElement("template");
    return i.innerHTML = e, i;
  }
}
function F(r, e, t = r, i) {
  if (e === I) return e;
  let s = i !== void 0 ? t._$Co?.[i] : t._$Cl;
  const a = Y(e) ? void 0 : e._$litDirective$;
  return s?.constructor !== a && (s?._$AO?.(!1), a === void 0 ? s = void 0 : (s = new a(r), s._$AT(r, t, i)), i !== void 0 ? (t._$Co ??= [])[i] = s : t._$Cl = s), s !== void 0 && (e = F(r, s._$AS(r, e.values), s, i)), e;
}
class ht {
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
    const { el: { content: t }, parts: i } = this._$AD, s = (e?.creationScope ?? T).importNode(t, !0);
    z.currentNode = s;
    let a = z.nextNode(), n = 0, d = 0, o = i[0];
    for (; o !== void 0; ) {
      if (n === o.index) {
        let u;
        o.type === 2 ? u = new j(a, a.nextSibling, this, e) : o.type === 1 ? u = new o.ctor(a, o.name, o.strings, this, e) : o.type === 6 && (u = new gt(a, this, e)), this._$AV.push(u), o = i[++d];
      }
      n !== o?.index && (a = z.nextNode(), n++);
    }
    return z.currentNode = T, s;
  }
  p(e) {
    let t = 0;
    for (const i of this._$AV) i !== void 0 && (i.strings !== void 0 ? (i._$AI(e, i, t), t += i.strings.length - 2) : i._$AI(e[t])), t++;
  }
}
class j {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(e, t, i, s) {
    this.type = 2, this._$AH = h, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = i, this.options = s, this._$Cv = s?.isConnected ?? !0;
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
    e = F(this, e, t), Y(e) ? e === h || e == null || e === "" ? (this._$AH !== h && this._$AR(), this._$AH = h) : e !== this._$AH && e !== I && this._(e) : e._$litType$ !== void 0 ? this.$(e) : e.nodeType !== void 0 ? this.T(e) : dt(e) ? this.k(e) : this._(e);
  }
  O(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  T(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
  }
  _(e) {
    this._$AH !== h && Y(this._$AH) ? this._$AA.nextSibling.data = e : this.T(T.createTextNode(e)), this._$AH = e;
  }
  $(e) {
    const { values: t, _$litType$: i } = e, s = typeof i == "number" ? this._$AC(e) : (i.el === void 0 && (i.el = X.createElement(Ke(i.h, i.h[0]), this.options)), i);
    if (this._$AH?._$AD === s) this._$AH.p(t);
    else {
      const a = new ht(s, this), n = a.u(this.options);
      a.p(t), this.T(n), this._$AH = a;
    }
  }
  _$AC(e) {
    let t = De.get(e.strings);
    return t === void 0 && De.set(e.strings, t = new X(e)), t;
  }
  k(e) {
    $e(this._$AH) || (this._$AH = [], this._$AR());
    const t = this._$AH;
    let i, s = 0;
    for (const a of e) s === t.length ? t.push(i = new j(this.O(Z()), this.O(Z()), this, this.options)) : i = t[s], i._$AI(a), s++;
    s < t.length && (this._$AR(i && i._$AB.nextSibling, s), t.length = s);
  }
  _$AR(e = this._$AA.nextSibling, t) {
    for (this._$AP?.(!1, !0, t); e !== this._$AB; ) {
      const i = ke(e).nextSibling;
      ke(e).remove(), e = i;
    }
  }
  setConnected(e) {
    this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
  }
}
class ne {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(e, t, i, s, a) {
    this.type = 1, this._$AH = h, this._$AN = void 0, this.element = e, this.name = t, this._$AM = s, this.options = a, i.length > 2 || i[0] !== "" || i[1] !== "" ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = h;
  }
  _$AI(e, t = this, i, s) {
    const a = this.strings;
    let n = !1;
    if (a === void 0) e = F(this, e, t, 0), n = !Y(e) || e !== this._$AH && e !== I, n && (this._$AH = e);
    else {
      const d = e;
      let o, u;
      for (e = a[0], o = 0; o < a.length - 1; o++) u = F(this, d[i + o], t, o), u === I && (u = this._$AH[o]), n ||= !Y(u) || u !== this._$AH[o], u === h ? e = h : e !== h && (e += (u ?? "") + a[o + 1]), this._$AH[o] = u;
    }
    n && !s && this.j(e);
  }
  j(e) {
    e === h ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class pt extends ne {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === h ? void 0 : e;
  }
}
class ut extends ne {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    this.element.toggleAttribute(this.name, !!e && e !== h);
  }
}
class mt extends ne {
  constructor(e, t, i, s, a) {
    super(e, t, i, s, a), this.type = 5;
  }
  _$AI(e, t = this) {
    if ((e = F(this, e, t, 0) ?? h) === I) return;
    const i = this._$AH, s = e === h && i !== h || e.capture !== i.capture || e.once !== i.once || e.passive !== i.passive, a = e !== h && (i === h || s);
    s && this.element.removeEventListener(this.name, this, i), a && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
  }
}
class gt {
  constructor(e, t, i) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = i;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    F(this, e);
  }
}
const vt = { I: j }, ft = fe.litHtmlPolyfillSupport;
ft?.(X, j), (fe.litHtmlVersions ??= []).push("3.3.3");
const $t = (r, e, t) => {
  const i = t?.renderBefore ?? e;
  let s = i._$litPart$;
  if (s === void 0) {
    const a = t?.renderBefore ?? null;
    i._$litPart$ = s = new j(e.insertBefore(Z(), a), a, void 0, t ?? {});
  }
  return s._$AI(r), s;
};
const be = globalThis;
let E = class extends H {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    const e = super.createRenderRoot();
    return this.renderOptions.renderBefore ??= e.firstChild, e;
  }
  update(e) {
    const t = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = $t(t, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    super.connectedCallback(), this._$Do?.setConnected(!0);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._$Do?.setConnected(!1);
  }
  render() {
    return I;
  }
};
E._$litElement$ = !0, E.finalized = !0, be.litElementHydrateSupport?.({ LitElement: E });
const bt = be.litElementPolyfillSupport;
bt?.({ LitElement: E });
(be.litElementVersions ??= []).push("4.2.2");
const ue = [
  "Race Center",
  "Live Timing",
  "Race Weekend",
  "History",
  "Analytics"
], P = {
  1: "Cup Series",
  2: "National Series 2",
  3: "Truck Series"
}, Ne = [
  "weekend",
  "laps",
  "notes",
  "loop",
  "averages",
  "pits",
  "stages"
], yt = "nascar_race_center/dashboard/";
class x extends Error {
  constructor(e, t) {
    super(t || e), this.code = e, this.name = "DashboardError";
  }
}
function Je(r) {
  return typeof r == "object" && r !== null && "code" in r ? String(r.code) : "connection_error";
}
const xt = {
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
function Ge(r) {
  const e = Je(r);
  return xt[e] || `Data unavailable (${e.replaceAll("_", " ")}). Narrow the selection or retry.`;
}
function ee(r, e = 1e10) {
  if (!/^\d+$/.test(r) || BigInt(r) < 1n || BigInt(r) > BigInt(e) || BigInt(r) > BigInt(Number.MAX_SAFE_INTEGER))
    throw new x("unsafe_identifier");
  return Number(r);
}
function V(r) {
  return typeof r == "object" && r !== null && !Array.isArray(r);
}
function Pe(r, e) {
  if (V(r) && r.type === "result") {
    if (r.success === !1)
      throw new x(
        V(r.error) ? String(r.error.code) : "invalid_response"
      );
    r = r.result;
  } else V(r) && r.type === "event" && (r = r.event);
  if (!V(r) || r.api_version !== 1)
    throw new x("api_version");
  if (r.entry_id !== e || !V(r.data))
    throw new x("invalid_response");
  return r;
}
function Ue(r, e) {
  if (r.identity?.series_id !== e || typeof r.availability != "string" || r.leaderboard !== null && (!Array.isArray(r.leaderboard) || r.leaderboard.length > 100 || r.leaderboard.some((t) => typeof t.driver_id != "string")))
    throw new x("invalid_response");
  return r.availability === "ok" && r.stale === !1 ? r : { ...r, session: null, leaderboard: null, leader_driver_id: null };
}
const Me = /* @__PURE__ */ new WeakMap();
function _t(r, e) {
  let t = Me.get(r);
  t || (t = /* @__PURE__ */ new Map(), Me.set(r, t));
  let i = t.get(e);
  return i || (i = { tail: Promise.resolve(), last: 0 }, t.set(e, i)), i;
}
class wt {
  constructor(e, t, i = () => !0) {
    this.hass = e, this.entry = t, this.active = i, this.controller = new AbortController();
  }
  dispose() {
    this.controller.abort();
  }
  async paced(e) {
    const t = _t(this.hass.connection, this.entry), i = t.tail.then(async () => {
      const s = Math.max(0, 370 - (Date.now() - t.last));
      if (this.controller.signal.aborted)
        throw new x("connection_error");
      if (s && await new Promise((a, n) => {
        const d = () => {
          clearTimeout(o), n(new x("connection_error"));
        }, o = setTimeout(() => {
          this.controller.signal.removeEventListener("abort", d), a();
        }, s);
        this.controller.signal.addEventListener("abort", d, {
          once: !0
        });
      }), this.controller.signal.aborted || !this.active())
        throw new x("connection_error");
      return t.last = Date.now(), e();
    });
    return t.tail = i.then(
      () => {
      },
      () => {
      }
    ), i;
  }
  message(e, t = {}) {
    return {
      type: yt + e,
      entry_id: this.entry,
      api_version: 1,
      ...t
    };
  }
  async request(e, t = {}) {
    const i = await this.paced(
      () => this.hass.callWS(this.message(e, t))
    );
    return Pe(i, this.entry).data;
  }
  async bootstrap() {
    const e = await this.request("bootstrap");
    if (!Array.isArray(e.series_ids) || !e.series_ids.length || e.series_ids.some((t) => ![1, 2, 3].includes(t)) || !Array.isArray(e.favorite_driver_ids) || e.favorite_driver_ids.some((t) => typeof t != "string") || !e.references || !Array.isArray(e.references.drivers) || !Array.isArray(e.references.tracks) || !Array.isArray(e.navigation) || !Array.isArray(e.upcoming) || !Array.isArray(e.source_state))
      throw new x("invalid_response");
    return e;
  }
  async live(e) {
    return Ue(
      await this.request("live", { series_id: e }),
      e
    );
  }
  async subscribe(e, t, i) {
    let s = 0;
    return this.paced(
      () => this.hass.connection.subscribeMessage(
        (a) => {
          try {
            const n = Pe(a, this.entry), d = n.revision ?? n.data.revision;
            if (d !== void 0 && d <= s) return;
            if (n.data.availability === "entry_unavailable")
              throw new x("entry_unavailable");
            const o = Ue(n.data, e);
            s = d ?? s + 1, t(o);
          } catch (n) {
            i(n);
          }
        },
        this.message("subscribe_live", { series_id: e })
      )
    );
  }
  async page(e, t, i = 0, s) {
    const a = await this.request(e, {
      ...t,
      offset: i,
      limit: 200,
      ...s ? { snapshot: s } : {}
    });
    if (e === "analytics" && a.contract_version !== 1)
      throw new x("api_version");
    const n = e === "history" ? a.race : e === "analytics" ? a.query?.key : void 0;
    if ((e === "history" || e === "analytics") && (!n || n.series_id !== t.series_id || n.season !== t.season || n.race_id !== String(t.race_id)))
      throw new x("invalid_response");
    const d = a.pagination;
    if (!d || d.offset !== i || !Array.isArray(a.records) || a.records.length > 200 || d.returned !== a.records.length || !/^([a-f0-9]{64})$/.test(d.snapshot) || !Number.isInteger(d.total) || d.total < i + a.records.length || s && d.snapshot !== s || d.next_offset !== null && (d.next_offset !== i + a.records.length || d.next_offset <= i) || d.complete !== (d.next_offset === null))
      throw new x("invalid_response");
    return (e === "live_driver" || e === "live_scoring") && (a.records = a.records.map((o) => ({ ...o, kind: "detail" }))), a;
  }
  schedule(e, t = 0, i) {
    return this.page("schedule", e, t, i);
  }
  history(e, t = 0, i) {
    return this.page("history", e, t, i);
  }
  analytics(e, t = 0, i) {
    return this.page("analytics", e, t, i);
  }
  liveDriver(e, t = 0, i) {
    return this.page("live_driver", e, t, i);
  }
  liveScoring(e, t = 0, i) {
    return this.page("live_scoring", e, t, i);
  }
}
async function Ze(r) {
  const e = await r.callWS({
    type: "config_entries/get",
    domain: "nascar_race_center"
  });
  if (!Array.isArray(e)) throw new x("invalid_response");
  return e.filter((t) => t.domain === "nascar_race_center");
}
const v = (r) => r ? r.replaceAll("_", " ") : "Unknown", K = /* @__PURE__ */ new Map();
function f(r, e, t = 0) {
  if (typeof r != "number" || !Number.isFinite(r)) return "—";
  const i = JSON.stringify([e, t]);
  let s = K.get(i);
  return s || (s = new Intl.NumberFormat(e === "none" ? "en-US" : e, {
    useGrouping: e !== "none",
    maximumFractionDigits: t
  }), K.set(i, s), K.size > 32 && K.delete(K.keys().next().value)), s.format(r);
}
function q(r) {
  if (!r || !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)$/.test(
    r
  ))
    return null;
  const e = Date.parse(r);
  return Number.isFinite(e) ? e : null;
}
function U(r, e) {
  const t = q(r);
  return t === null ? "Time unconfirmed" : new Intl.DateTimeFormat(e?.locale?.language, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: e?.config?.time_zone,
    ...e?.locale?.time_format === "12" ? { hour12: !0 } : e?.locale?.time_format === "24" ? { hour12: !1 } : {}
  }).format(t);
}
function kt(r, e = Date.now()) {
  const t = q(r);
  if (t === null || t <= e) return null;
  const i = Math.ceil((t - e) / 6e4);
  return i >= 1440 ? `${Math.floor(i / 1440)}d ${Math.floor(i % 1440 / 60)}h` : `${Math.floor(i / 60)}h ${i % 60}m`;
}
function de(r) {
  const e = r?.availability;
  return e === "ok" && r?.stale === !1 ? { text: "Fresh source", tone: "green" } : e === "stale" || r?.stale === !0 ? { text: "Stale · timing withheld", tone: "yellow" } : e === "freshness_unknown" ? { text: "Freshness unknown", tone: "yellow" } : { text: e ? v(e) : "Awaiting source", tone: "neutral" };
}
function ze(r) {
  const e = {
    green: "green",
    yellow: "yellow",
    red: "red",
    white: "white",
    checkered: "checkered"
  }, t = r?.session?.flag;
  return t && e[t] ? { text: v(t), tone: e[t] } : {
    text: r?.session?.flag_state_code != null ? `Unknown flag (${r.session.flag_state_code})` : "Flag unreported",
    tone: "neutral"
  };
}
function At(r, e, t = !1) {
  return r.map((i, s) => ({ row: i, index: s })).sort((i, s) => {
    const a = e === "position_change" ? i.row.position_change.value : i.row[e], n = e === "position_change" ? s.row.position_change.value : s.row[e];
    if (a == null && n == null) return i.index - s.index;
    if (a == null) return 1;
    if (n == null) return -1;
    const d = typeof a == "number" && typeof n == "number" ? a - n : typeof a == "boolean" && typeof n == "boolean" ? Number(a) - Number(n) : String(a).localeCompare(String(n), void 0, { numeric: !0 });
    return (t ? -d : d) || i.index - s.index;
  }).map((i) => i.row);
}
function St(r) {
  return r.unit.includes("unverified") ? "source unit · unverified" : v(r.unit);
}
function S(r) {
  const e = r?.locale?.number_format;
  return e === "none" ? "none" : e === "comma_decimal" ? "en-US" : e === "decimal_comma" ? "de-DE" : e === "space_comma" ? "fr-FR" : e === "system" ? void 0 : r?.locale?.language;
}
class ce {
  constructor(e, t, i) {
    this.command = e, this.selection = t, this.expectedLive = i, this.pages = /* @__PURE__ */ new Map(), this.loading = !1, this.created = 0, this.generation = 0, this.previousOffsets = [];
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
  async load(e, t = 0, i = !1) {
    if (this.loading) return;
    i && this.invalidate();
    const s = this.generation;
    if (this.expired) {
      this.error = new x("snapshot_expired");
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
      if (s !== this.generation) return;
      if (this.expectedLive && (n.identity?.series_id !== this.selection.series_id || n.identity?.race_id !== this.expectedLive.race_id || n.identity?.run_id !== this.expectedLive.run_id))
        throw new x("snapshot_changed");
      for (this.created || (this.created = Date.now()), this.pages.set(t, n), this.current = n; this.pages.size > 8; )
        this.pages.delete(this.pages.keys().next().value);
    } catch (n) {
      s === this.generation && (Je(n) === "snapshot_changed" && (this.pages.clear(), this.current = void 0, this.previousOffsets = [], this.created = 0), this.error = n);
    } finally {
      s === this.generation && (this.loading = !1);
    }
  }
  async next(e) {
    const t = this.current?.pagination;
    if (!t || t.next_offset === null) return;
    const i = t.offset;
    await this.load(e, t.next_offset), this.current?.pagination.offset !== i && this.previousOffsets.push(i);
  }
  async previous(e) {
    const t = this.previousOffsets.at(-1);
    t !== void 0 && (await this.load(e, t), this.current?.pagination.offset === t && this.previousOffsets.pop());
  }
  async jump(e, t) {
    if (!this.pages.has(t) || this.loading) return;
    const i = this.current?.pagination.offset;
    await this.load(e, t), i !== void 0 && i !== t && this.current?.pagination.offset === t && this.previousOffsets.push(i);
  }
}
const w = {
  density: "Display density",
  comfortable: "Comfortable",
  compact: "Compact",
  measurements: "All measurements",
  essential: "Essential columns",
  towerHint: "Open a driver for details. Scroll within the table for more measurements.",
  sortHint: "Reported position is the default. Change is relative to the start, not an on-track pass.",
  inspect: "Inspect observation",
  previousPoint: "Previous observation",
  nextPoint: "Next observation",
  missing: "Missing / excluded observation",
  chartScope: "Loaded pages only; missing observations break lines.",
  retained: "Return to a retained selection",
  snapshotHint: "Reusing a selection creates no snapshot. Slots remain occupied until server expiry; clearing local data does not release them.",
  front: "Front of the reported field",
  records: "Record types on this page"
}, Q = re`
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
    /* Theme changes must not animate through unreadable intermediate colors. */
    transition: none;
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
    min-width: 0;
  }
  .field select {
    width: 100%;
    min-width: 0;
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
  h1,
  .race-title {
    font-size: clamp(28px, 3.5cqi, 44px);
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
    overflow-wrap: anywhere;
    font-size: 17px;
    font-weight: 750;
    letter-spacing: -0.03em;
  }
  .tools {
    flex-wrap: wrap;
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
    border-bottom: 2px solid transparent;
    border-radius: 6px 6px 0 0;
    font-size: 13px;
    padding: 10px 14px;
  }
  .nav button[aria-current="page"] {
    border-bottom-color: currentColor;
    color: var(--primary-text-color, #e8edf2);
    font-weight: 650;
    background: color-mix(in srgb, var(--nrc-accent), transparent 92%);
  }
  main {
    padding: 28px;
    min-height: 420px;
  }
  .brand > *,
  .tools > *,
  .row > *,
  .section-head > *,
  .filters > *,
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
  .race-flag::before {
    width: 20px;
    height: 14px;
    border-radius: 0;
    border-left: 2px solid currentColor;
    clip-path: polygon(0 0, 100% 10%, 90% 90%, 0 80%);
  }
  .race-flag.green::before {
    background: #81be55;
  }
  .race-flag.yellow::before {
    background: #e9bd4f;
  }
  .race-flag.red::before {
    background: #ea686c;
  }
  .race-flag.white::before {
    background: #eee;
    border: 1px solid #555;
  }
  .race-flag.checkered::before {
    background-size: 8px 8px;
  }
  .panel {
    background: var(--nrc-panel);
    border: 1px solid var(--nrc-line);
    border-radius: 12px;
    padding: var(--nrc-panel-space, 22px);
  }
  .hero {
    position: relative;
    overflow: hidden;
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 28px;
    padding: var(--nrc-hero-space, 28px);
    background: var(--nrc-panel);
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
    font-size: 52px;
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
    align-items: start;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(155px, 100%), 1fr));
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
    min-inline-size: 0;
    max-inline-size: 100%;
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
    min-height: 44px;
  }
  input[type="checkbox"] {
    padding: 0;
    flex-shrink: 0;
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
    min-height: 44px;
    align-content: center;
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
    grid-template-columns: repeat(auto-fit, minmax(min(155px, 100%), 1fr));
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
  .overview-field {
    display: none;
  }
  .front-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
    margin-top: 16px;
  }
  .front-grid button {
    display: grid;
    grid-template-columns: auto auto;
    justify-content: start;
    gap: 8px;
    text-align: left;
    align-items: center;
  }
  .front-grid strong {
    grid-column: 1 / -1;
    overflow-wrap: anywhere;
  }
  .selection-library > .actions {
    margin-block: 12px;
  }
  [data-compact] {
    --nrc-panel-space: 14px;
    --nrc-hero-space: 22px;
  }
  [data-compact] main {
    padding: 18px;
  }
  [data-compact] .stack {
    gap: 14px;
  }
  [data-compact] .section-head {
    margin-bottom: 10px;
  }
  [data-compact] .hero-content {
    gap: 12px;
  }
  [data-compact] .stat {
    padding: 12px;
  }
  [data-compact] .session-row {
    padding-block: 8px;
  }
  @container (min-width:1100px) {
    .overview-field {
      display: block;
    }
    .two-col {
      grid-template-columns: 1fr 1fr;
      align-items: start;
    }
    .two-col > .stack {
      align-content: start;
    }
    [data-compact] .hero {
      grid-template-columns: 1.4fr 1fr;
    }
    [data-compact] .two-col > .panel.stack {
      gap: 10px;
    }
  }
  @media (forced-colors: active) {
    :focus-visible {
      outline: 3px solid Highlight;
    }
    .nav button[aria-current="page"],
    button[aria-pressed="true"] {
      border: 2px solid Highlight;
    }
    .badge::before,
    .car,
    .progress {
      forced-color-adjust: auto;
      border: 1px solid CanvasText;
    }
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
      flex-wrap: wrap;
      padding: 16px;
      align-items: start;
      gap: 8px;
    }
    .brand-title {
      overflow-wrap: anywhere;
      font-size: 14px;
    }
    .brand .eyebrow {
      font-size: 9px;
    }
    .tools {
      width: 100%;
      justify-content: space-between;
      gap: 10px;
    }
    .tools > label {
      flex: 1;
      min-width: 0;
    }
    .tools select {
      font-size: 13px;
      padding: 8px 6px;
      width: 100%;
    }
    .nav {
      flex-wrap: wrap;
    }
    .nav button {
      flex: 1 1 29%;
      white-space: normal;
      padding: 8px;
      font-size: 12px;
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
      grid-template-columns: 1fr;
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
function O(r, e = 0, t) {
  return r == null ? "Unknown / not reported" : typeof r == "boolean" ? r ? "Yes" : "No" : typeof r == "number" ? f(r, t, 6) : typeof r == "string" ? r : e > 6 ? "Nested observation" : Array.isArray(r) ? r.length ? l`${r.map(
    (i, s) => l`<div>
              ${r.length > 1 ? l`<small>Observation ${s + 1}</small>` : h}${O(i, e + 1, t)}
            </div>`
  )}` : "No reported records" : l`<dl>
    ${Object.entries(r).map(
    ([i, s]) => l`<dt>${v(i)}</dt>
          <dd>${O(s, e + 1, t)}</dd>`
  )}
  </dl>`;
}
function Ct(r, e) {
  return r.kind === "notes" && r.value ? `Lap ${f(r.value.lap, e)} · ${r.value.text ?? "Note text unreported"}` : r.kind === "flags" && r.value ? `Lap ${f(r.value.laps_completed, e)} · reported flag code ${f(r.value.flag_code, e)}` : r.kind === "pits" && r.value ? `Archived pit · car ${r.value.activity.car_number ?? "—"} · ${r.value.nascar_driver_id ? `NASCAR driver ${r.value.nascar_driver_id}` : "NASCAR driver identity unreported"}` : (r.kind === "stage_result" || r.kind === "weekend_stage_result") && r.value ? `Stage ${f(r.number, e)} · P${f(r.value.position, e)} · car ${r.value.car_number ?? "—"} · driver ${r.value.driver_id}` : r.kind === "loop_driver" && r.value ? `Loop observations · NASCAR driver ${r.value.nascar_driver_id}` : r.kind === "average_driver" && r.value ? `Lap averages · ${r.value.driver.name ?? r.value.driver.nascar_driver_id} · car ${r.value.driver.car_number ?? "—"}` : v(r.kind);
}
function te(r, e) {
  const t = S(e);
  return l`<div class="record-list">
    ${r.map(
    (i, s) => l`<details>
          <summary>
            ${Ct(i, t)}${i.driver_id ? ` · driver ${i.driver_id}` : ""}${i.number != null ? ` · stage ${i.number}` : ""}${i.size ? ` · ${i.size} laps` : ""}${i.source_index != null ? ` · source index ${i.source_index}` : ` · record ${s + 1}`}
          </summary>
          ${i.kind === "loop_driver" || i.kind === "average_driver" ? l`<div
                class="table-scroll"
                tabindex="0"
                role="region"
                aria-label="Reported scoring metrics"
              >
                <table>
                  <thead>
                    <tr>
                      <th>Reported field</th>
                      <th>Source value</th>
                      <th>Interpretation</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${i.value?.metrics.map(
      (a) => l`<tr>
                          <th scope="row">${v(a.field)}</th>
                          <td>${f(a.value, t, 6)}</td>
                          <td>${v(a.interpretation)}</td>
                        </tr>`
    )}
                  </tbody>
                </table>
              </div>` : h}
          ${O(i, 0, t)}
        </details>`
  )}
  </div>`;
}
function Te(r, e) {
  const t = r.evidence ?? r.datasets ?? [];
  return l`<div class="evidence">
    ${t.map(
    (i) => l`<details>
          <summary class="badge">
            ${"dataset" in i ? i.dataset : i.provenance?.dataset ?? "Dataset"}
            · ${v(i.status)}
          </summary>
          <dl>
            <dt>Reason</dt>
            <dd>${v(i.reason)}</dd>
            <dt>Identity validation</dt>
            <dd>${v(i.provenance?.validation)}</dd>
            <dt>Coverage</dt>
            <dd>${v(i.provenance?.coverage)}</dd>
            <dt>Retrieved</dt>
            <dd>${U(i.provenance?.retrieved_at, e)}</dd>
            <dt>Reported content time</dt>
            <dd>${U(i.provenance?.response_at, e)}</dd>
            <dt>Delivery</dt>
            <dd>${v(i.provenance?.delivery)}</dd>
            <dt>Retry after</dt>
            <dd>${i.provenance?.retry_after ?? "Unknown"}</dd>
          </dl>
        </details>`
  )}
  </div>`;
}
function Ie(r, e) {
  return l`<div class="panel metric">
    <h3>${v(r.name)}</h3>
    <strong>${f(r.value, e, 3)}</strong>
    <p>${v(r.classification)} · ${St(r)}</p>
    <details>
      <summary>Method & availability</summary>
      <p>${v(r.method)}${r.reason ? ` · ${v(r.reason)}` : ""}</p>
    </details>
  </div>`;
}
function Et(r, e) {
  const t = r.filter((s) => s.kind === "result").sort(
    (s, a) => (s.value?.finishing_position ?? 1 / 0) - (a.value?.finishing_position ?? 1 / 0)
  ), i = S(e);
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
    const a = s.value;
    return l`<tr>
                <td>${f(a.finishing_position, i)}</td>
                <td>
                  <span class="car">${a.driver.car_number ?? "—"}</span> ${a.driver.name ?? a.driver.nascar_driver_id}
                </td>
                <td>${f(a.starting_position, i)}</td>
                <td>${f(a.laps_completed, i)}</td>
                <td>${f(a.laps_led, i)}</td>
                <td>${f(a.points_earned, i)}</td>
                <td>${f(a.playoff_points_earned, i)}</td>
                <td>${a.finishing_status ?? "Unknown"}</td>
              </tr>`;
  })}
          </tbody>
        </table>
      </div>` : h;
}
const Rt = { CHILD: 2 }, Dt = (r) => (...e) => ({ _$litDirective$: r, values: e });
let Nt = class {
  constructor(e) {
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AT(e, t, i) {
    this._$Ct = e, this._$AM = t, this._$Ci = i;
  }
  _$AS(e, t) {
    return this.update(e, t);
  }
  update(e, t) {
    return this.render(...t);
  }
};
const { I: Pt } = vt, Le = (r) => r, He = () => document.createComment(""), J = (r, e, t) => {
  const i = r._$AA.parentNode, s = e === void 0 ? r._$AB : e._$AA;
  if (t === void 0) {
    const a = i.insertBefore(He(), s), n = i.insertBefore(He(), s);
    t = new Pt(a, n, r, r.options);
  } else {
    const a = t._$AB.nextSibling, n = t._$AM, d = n !== r;
    if (d) {
      let o;
      t._$AQ?.(r), t._$AM = r, t._$AP !== void 0 && (o = r._$AU) !== n._$AU && t._$AP(o);
    }
    if (a !== s || d) {
      let o = t._$AA;
      for (; o !== a; ) {
        const u = Le(o).nextSibling;
        Le(i).insertBefore(o, s), o = u;
      }
    }
  }
  return t;
}, N = (r, e, t = r) => (r._$AI(e, t), r), Ut = {}, Mt = (r, e = Ut) => r._$AH = e, zt = (r) => r._$AH, he = (r) => {
  r._$AR(), r._$AA.remove();
};
const qe = (r, e, t) => {
  const i = /* @__PURE__ */ new Map();
  for (let s = e; s <= t; s++) i.set(r[s], s);
  return i;
}, Tt = Dt(class extends Nt {
  constructor(r) {
    if (super(r), r.type !== Rt.CHILD) throw Error("repeat() can only be used in text expressions");
  }
  dt(r, e, t) {
    let i;
    t === void 0 ? t = e : e !== void 0 && (i = e);
    const s = [], a = [];
    let n = 0;
    for (const d of r) s[n] = i ? i(d, n) : n, a[n] = t(d, n), n++;
    return { values: a, keys: s };
  }
  render(r, e, t) {
    return this.dt(r, e, t).values;
  }
  update(r, [e, t, i]) {
    const s = zt(r), { values: a, keys: n } = this.dt(e, t, i);
    if (!Array.isArray(s)) return this.ut = n, a;
    const d = this.ut ??= [], o = [];
    let u, b, p = 0, c = s.length - 1, m = 0, $ = a.length - 1;
    for (; p <= c && m <= $; ) if (s[p] === null) p++;
    else if (s[c] === null) c--;
    else if (d[p] === n[m]) o[m] = N(s[p], a[m]), p++, m++;
    else if (d[c] === n[$]) o[$] = N(s[c], a[$]), c--, $--;
    else if (d[p] === n[$]) o[$] = N(s[p], a[$]), J(r, o[$ + 1], s[p]), p++, $--;
    else if (d[c] === n[m]) o[m] = N(s[c], a[m]), J(r, s[p], s[c]), c--, m++;
    else if (u === void 0 && (u = qe(n, m, $), b = qe(d, p, c)), u.has(d[p])) if (u.has(d[c])) {
      const y = b.get(n[m]), k = y !== void 0 ? s[y] : null;
      if (k === null) {
        const A = J(r, s[p]);
        N(A, a[m]), o[m] = A;
      } else o[m] = N(k, a[m]), J(r, s[p], k), s[y] = null;
      m++;
    } else he(s[c]), c--;
    else he(s[p]), p++;
    for (; m <= $; ) {
      const y = J(r, o[$ + 1]);
      N(y, a[m]), o[m++] = y;
    }
    for (; p <= c; ) {
      const y = s[p++];
      y !== null && he(y);
    }
    return this.ut = n, Mt(r, o), I;
  }
});
class It extends E {
  constructor() {
    super(...arguments), this.rows = [], this.sort = "position", this.descending = !1, this.expanded = !1, this.compact = !1;
  }
  static {
    this.properties = {
      rows: { attribute: !1 },
      hass: { attribute: !1 },
      sort: { state: !0 },
      descending: { state: !0 },
      expanded: { state: !0 },
      compact: { type: Boolean }
    };
  }
  static {
    this.styles = [
      Q,
      re`
      :host {
        container-type: inline-size;
      }
      .tower {
        min-width: 960px;
        table-layout: fixed;
      }
      th button {
        min-height: 44px;
        min-width: 44px;
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
        width: 220px;
      }
      .driver-button {
        border: 0;
        background: none;
        padding: 0;
        text-align: left;
        min-height: 44px;
        width: 100%;
        overflow-wrap: anywhere;
        white-space: normal;
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
      .table-scroll {
        max-height: 70vh;
      }
      th {
        position: sticky;
        top: 0;
        z-index: 2;
      }
      th.sticky {
        z-index: 3;
      }
      th:first-child,
      td:first-child {
        width: 54px;
      }
      th:nth-child(2),
      td:nth-child(2) {
        width: 64px;
      }
      th:nth-child(3) {
        width: 220px;
      }
      th:nth-child(11) {
        width: 185px;
      }
      th:last-child {
        width: 200px;
      }
      td {
        padding-block: 8px;
      }
      [data-compact] td {
        padding-block: 2px;
      }
      .column-toggle {
        display: none;
      }
      .tower-tools {
        display: flex;
        gap: 12px;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-wrap: wrap;
      }
      @container (max-width:600px) {
        .column-toggle {
          display: block;
        }
        th:first-child,
        td:first-child {
          width: 40px;
          padding-inline: 6px;
        }
        th:nth-child(2),
        td:nth-child(2) {
          width: 48px;
          padding-inline: 5px;
        }
        th:nth-child(3) {
          width: 150px;
        }
        th:nth-child(4) {
          width: 60px;
        }
        th:nth-child(11) {
          width: 185px;
        }
        th:last-child {
          width: 200px;
        }
        .tower:not([data-expanded]) .measurement {
          display: none;
        }
        .tower[data-expanded] {
          min-width: 1040px;
        }
        td:nth-child(2),
        th:nth-child(2) {
          position: sticky;
          left: 40px;
          background: var(--nrc-base);
          z-index: 1;
        }
        td:nth-child(3),
        th:nth-child(3) {
          position: sticky;
          left: 88px;
          background: var(--nrc-base);
          z-index: 1;
        }
        th:nth-child(2),
        th:nth-child(3) {
          z-index: 3;
        }
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
          min-width: 340px;
        }
        .driver-cell {
          width: 150px;
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
          max-width: none;
        }
        .table-note {
          font-size: 11px;
        }
      }
    `
    ];
  }
  moveFocus(e) {
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) return;
    const t = [
      ...this.renderRoot.querySelectorAll(".driver-button")
    ], i = t.indexOf(e.currentTarget), s = e.key === "Home" ? 0 : e.key === "End" ? t.length - 1 : i + (e.key === "ArrowDown" ? 1 : -1);
    e.preventDefault(), t[Math.max(0, Math.min(t.length - 1, s))]?.focus();
  }
  order(e) {
    e === this.sort ? this.descending = !this.descending : (this.sort = e, this.descending = !1);
  }
  heading(e, t, i = "") {
    return l`<th
      scope="col"
      class=${i + (t === "name" ? " driver-cell" : "")}
      aria-sort=${this.sort === t ? this.descending ? "descending" : "ascending" : "none"}
    >
      <button @click=${() => this.order(t)}>
        ${e}${this.sort === t ? this.descending ? " ↓" : " ↑" : h}
      </button>
    </th>`;
  }
  render() {
    const e = S(this.hass);
    return l`<div class="tower-tools">
        <small>${w.sortHint}</small>
        <button
          class="column-toggle"
          aria-pressed=${this.expanded}
          @click=${() => {
      this.expanded = !this.expanded;
    }}
        >
          ${this.expanded ? w.essential : w.measurements}
        </button>
      </div>
      <p class="sr-only" role="status">
        Sorted by ${this.sort.replaceAll("_", " ")},
        ${this.descending ? "descending" : "ascending"}.
      </p>
      <div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Timing tower. Scroll horizontally for additional reported measurements."
      >
        <table
          class="tower"
          ?data-expanded=${this.expanded}
          ?data-compact=${this.compact}
        >
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
      "favorite",
      "desktop-extra"
    )}${this.heading(
      "Start",
      "starting_position",
      "desktop-extra"
    )}${this.heading(
      "Change",
      "position_change",
      "desktop-extra"
    )}${this.heading("Gap*", "gap")}${this.heading(
      "Last*",
      "last_lap_time",
      "measurement"
    )}${this.heading(
      "Best*",
      "best_lap_time",
      "measurement"
    )}${this.heading("Laps", "laps_completed", "measurement")}
              <th scope="col" class="measurement">Speed*</th>
              <th scope="col" class="measurement">Status / pits</th>
            </tr>
          </thead>
          <tbody>
            ${Tt(
      At(this.rows, this.sort, this.descending),
      (t) => t.driver_id,
      (t) => l`<tr class=${t.favorite ? "favorite-row" : ""}>
                  <td class="rank sticky">${f(t.position, e)}</td>
                  <td><span class="car">${t.car_number ?? "—"}</span></td>
                  <td class="driver-cell">
                    <button
                      class="driver-button"
                      @keydown=${(i) => this.moveFocus(i)}
                      @click=${(i) => i.currentTarget.dispatchEvent(
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
                        >Start ${f(t.starting_position, e)} · Δ
                        ${t.position_change.value != null && t.position_change.value > 0 ? "+" : ""}${f(t.position_change.value, e)}
                        · ${t.running_status ?? "Status unknown"}</span
                      >
                    </button>
                  </td>
                  <td class="desktop-extra">
                    ${t.favorite ? l`<span class="star" aria-label="Favorite">★</span>` : "—"}
                  </td>
                  <td class="desktop-extra">
                    ${f(t.starting_position, e)}
                  </td>
                  <td
                    class=${"desktop-extra " + ((t.position_change.value ?? 0) > 0 ? "positive" : (t.position_change.value ?? 0) < 0 ? "negative" : "")}
                  >
                    ${t.position_change.value != null && t.position_change.value > 0 ? "+" : ""}${f(t.position_change.value, e)}
                  </td>
                  <td>${f(t.gap, e, 3)}</td>
                  <td class="measurement">
                    ${f(t.last_lap_time, e, 3)}
                  </td>
                  <td class="measurement">
                    ${f(t.best_lap_time, e, 3)}
                  </td>
                  <td class="measurement">
                    ${f(t.laps_completed, e)}
                  </td>
                  <td class="measurement">
                    <span title="Reported last / best / average speed"
                      >${f(t.last_lap_speed, e, 3)} /
                      ${f(t.best_lap_speed, e, 3)} /
                      ${f(t.average_speed, e, 3)}</span
                    >
                  </td>
                  <td class="measurement">
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
        starting position − current position (derived). ${w.towerHint}
      </p>`;
  }
}
customElements.define("nrc-leaderboard", It);
function Lt(r, e) {
  const t = /* @__PURE__ */ new Map();
  for (const i of r) {
    if (!i.driver_id) continue;
    let s;
    if (i.kind === "samples" && i.value && e !== "window") {
      const a = i.value;
      s = {
        lap: a.lap,
        value: e === "position" ? a.usable_position : e === "delta" ? a.consecutive_time_delta : a.valid_time && a.included_in_time_basis ? a.reported_time : null
      };
    } else i.kind === "window" && i.value && e === "window" && (s = { lap: i.value.last_lap, value: i.value.mean });
    if (s) {
      const a = t.get(i.driver_id) ?? [];
      a.push(s), t.set(i.driver_id, a);
    }
  }
  return [...t].map(([i, s]) => ({
    id: i,
    points: s.sort((a, n) => a.lap - n.lap)
  }));
}
function Ht(r) {
  const e = [];
  let t = [];
  for (const i of r) {
    if (i.value === null) {
      t.length && e.push(t), t = [];
      continue;
    }
    t.length && i.lap !== t.at(-1).lap + 1 && (e.push(t), t = []), t.push(i);
  }
  return t.length && e.push(t), e;
}
class qt extends E {
  constructor() {
    super(...arguments), this.rows = [], this.mode = "time";
  }
  static {
    this.properties = {
      rows: { attribute: !1 },
      mode: { type: String },
      locale: { type: String },
      inspected: { state: !0 }
    };
  }
  static {
    this.styles = [
      Q,
      re`
      :host {
        display: block;
      }
      .chart-scroll {
        overflow-x: auto;
      }
      .graph {
        min-width: 560px;
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
      .inspector {
        display: flex;
        flex-wrap: wrap;
        align-items: end;
        gap: 12px;
        margin-top: 16px;
      }
      .inspection {
        min-height: 48px;
        padding-top: 12px;
        overflow-wrap: anywhere;
      }
      .legend button {
        min-height: 44px;
      }
      .legend [aria-pressed="true"] {
        border-color: currentColor;
        font-weight: 700;
      }
      circle {
        cursor: pointer;
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
    const e = Lt(this.rows, this.mode), t = e.flatMap((g) => g.points).filter((g) => g.value !== null), i = {
      time: "Lap-time progression",
      position: "Position progression",
      delta: "Consecutive-lap change",
      window: "Consecutive-window mean"
    };
    if (!e.length)
      return l`<div class="state">
        <h3>${i[this.mode]}</h3>
        <p class="muted">
          No supported measurements on the loaded pages. Load the next page or
          change the selection.
        </p>
      </div>`;
    const s = e.find((g) => g.id === this.inspected?.id) ?? e[0], a = s.points.find((g) => g.lap === this.inspected?.lap) ?? s.points[0], n = s.points.indexOf(a), d = (g, _) => {
      this.inspected = { id: g, lap: _ };
    }, o = e.flatMap((g) => g.points.map((_) => _.lap)), u = t.length ? t.map((g) => g.value) : [0], b = Math.min(...o), p = Math.max(...o), c = Math.min(...u), m = Math.max(...u), $ = Math.max((m - c) * 0.12, 0.25), y = this.mode === "position" ? c : c - $, k = this.mode === "position" ? m : m + $, A = (g) => b === p ? 380 : 55 + (g - b) / (p - b) * 650, W = (g) => this.mode === "position" ? k === y ? 135 : 30 + (g - y) / (k - y) * 210 : 240 - (g - y) / (k - y || 1) * 210, oe = [
      "#a8ef75",
      "#84c5ff",
      "#f3c574",
      "#d8a2ed",
      "#fe9b97",
      "#80d6cf",
      "#ebc1ac",
      "#d8e1eb"
    ].map(
      (g) => `color-mix(in srgb, ${g} 35%, var(--primary-text-color,#e8edf2))`
    );
    return l`<div class="graph-wrap">
        <h3>${i[this.mode]}</h3>
        <p class="muted">
          <small
            >${this.mode === "position" ? "Reported running positions" : this.mode === "time" ? "Reported measurements in selected basis · source unit unverified" : "Derived from selected observations · source unit unverified"}.
            ${w.chartScope}</small
          >
        </p>
        ${t.length ? l`<div
              class="chart-scroll"
              tabindex="0"
              role="region"
              aria-label="Chart plot. Scroll horizontally for readable axes."
            >
              <svg
                class="graph"
                viewBox="0 0 740 280"
                role="img"
                aria-label=${i[this.mode] + "; exact values available in the data table below."}
              >
                ${[0, 1, 2, 3, 4].map((g) => {
      const _ = y + (k - y) * g / 4;
      return M`<line class="grid" x1="55" x2="705" y1=${W(_)} y2=${W(_)}></line><text class="axis" x="48" y=${W(_) + 4} text-anchor="end">${f(_, this.locale, 2)}</text>`;
    })}
                <text class="axis" x="55" y="267">
                  Lap ${f(b, this.locale)}
                </text>
                <text class="axis" x="705" y="267" text-anchor="end">
                  Lap ${f(p, this.locale)}
                </text>
                ${e.map(
      (g, _) => Ht(g.points).map(
        (L) => M`<path d=${L.map((C, Ye) => `${Ye ? "L" : "M"}${A(C.lap)},${W(C.value)}`).join(" ")} fill="none" stroke=${oe[_ % 8]} stroke-width="2.5" stroke-linejoin="round"></path>${L.map((C) => M`<circle cx=${A(C.lap)} cy=${W(C.value)} r=${g.id === s.id && C.lap === a.lap ? "5" : "3"} fill=${oe[_ % 8]} @pointerenter=${() => d(g.id, C.lap)} @click=${() => d(g.id, C.lap)}><title>Driver ${g.id} · lap ${C.lap} · ${C.value}</title></circle>`)}`
      )
    )}
                ${a.value !== null ? M`<line x1=${A(a.lap)} x2=${A(a.lap)} y1="25" y2="245" stroke="currentColor" stroke-dasharray="3 5" opacity="0.4"></line>` : h}
              </svg>
            </div>` : l`<p class="notice">
              No valid values on these pages. Missing observations remain
              inspectable below.
            </p>`}
        <div class="legend" aria-label="Selected chart driver">
          ${e.map(
      (g, _) => l`<button
                aria-pressed=${g.id === s.id}
                @click=${() => d(g.id, g.points[0].lap)}
              >
                <i class="swatch" style=${`background:${oe[_ % 8]}`}></i
                >Driver ${g.id}
              </button>`
    )}
        </div>
        <div class="inspector" role="group" aria-label=${w.inspect}>
          <label class="field"
            >Driver<select
              .value=${s.id}
              @change=${(g) => {
      const _ = e.find(
        (L) => L.id === g.target.value
      );
      d(_.id, _.points[0].lap);
    }}
            >
              ${e.map(
      (g) => l`<option value=${g.id}>Driver ${g.id}</option>`
    )}
            </select></label
          >
          <label class="field"
            >Lap observation<select
              .value=${String(a.lap)}
              @change=${(g) => d(
      s.id,
      Number(g.target.value)
    )}
            >
              ${s.points.map(
      (g) => l`<option value=${g.lap}>
                    ${f(g.lap, this.locale)}${g.value === null ? " · missing" : ""}
                  </option>`
    )}
            </select></label
          >
          <button
            aria-label=${w.previousPoint}
            ?disabled=${n <= 0}
            @click=${() => d(s.id, s.points[n - 1].lap)}
          >
            ←
          </button>
          <button
            aria-label=${w.nextPoint}
            ?disabled=${n >= s.points.length - 1}
            @click=${() => d(s.id, s.points[n + 1].lap)}
          >
            →
          </button>
        </div>
        <p class="inspection" role="status">
          Driver ${s.id} · lap ${f(a.lap, this.locale)} ·
          <strong
            >${a.value === null ? w.missing : f(a.value, this.locale, 3)}</strong
          >
          ·
          ${this.mode === "position" ? "reported position" : this.mode === "time" ? "reported source measurement" : "derived source measurement"}
        </p>
        <p class="muted">
          <small
            >${e.reduce(
      (g, _) => g + _.points.filter((L) => L.value === null).length,
      0
    )}
            explicit missing observations on loaded pages. Unloaded or absent
            laps are not interpolated.</small
          >
        </p>
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
      (g) => g.points.map(
        (_) => l`<tr>
                      <td>${g.id}</td>
                      <td>${f(_.lap, this.locale)}</td>
                      <td>
                        ${_.value === null ? w.missing : f(_.value, this.locale, 3)}
                      </td>
                    </tr>`
      )
    )}
            </tbody>
          </table>
        </div>
      </details>`;
  }
}
customElements.define("nrc-chart", qt);
function Ot(r) {
  const e = /* @__PURE__ */ new Map(), t = (i, s, a) => {
    const n = JSON.stringify([
      s,
      a.name,
      a.classification,
      a.unit,
      a.method
    ]), d = e.get(n) ?? {
      key: n,
      name: `${s} · ${v(a.name)}`,
      classification: a.classification,
      unit: a.unit,
      method: a.method,
      observations: []
    };
    d.observations.push({
      driver: i,
      value: a.value,
      reason: a.reason
    }), e.set(n, d);
  };
  for (const i of r)
    if (!(!i.driver_id || !i.value)) {
      if (i.kind === "driver")
        for (const s of i.value.metrics)
          t(i.driver_id, "Lap summary", s);
      if (i.kind === "performance" && i.value.result) {
        const s = i.value.result;
        for (const a of [
          "starting_position",
          "finishing_position",
          "laps_completed",
          "laps_led",
          "points_earned",
          "playoff_points_earned"
        ])
          t(i.driver_id, "Race result", {
            name: a,
            value: s[a],
            classification: "recorded",
            unit: a.includes("position") ? "position" : a.includes("laps") ? "lap_count" : "reported_points",
            method: "reported_result",
            reason: s[a] === null ? "not_reported" : null
          });
      }
      if (i.kind === "performance_stages") {
        const s = i.value;
        for (const a of ["position", "points"])
          t(
            i.driver_id,
            `${v(s.dataset)} stage ${s.number}${s.run_id ? ` · ${s.run_namespace} ${s.run_id}` : ""}`,
            {
              name: a,
              value: s.conflict ? null : s[a],
              classification: "recorded",
              unit: a === "position" ? "position" : "reported_points",
              method: "reported_stage_observation",
              reason: s.conflict ? "conflicting_source_observations" : s[a] === null ? "not_reported" : null
            }
          );
      }
      if (i.kind === "performance_reported_metrics") {
        const s = i.value;
        for (const a of s.metrics)
          t(
            i.driver_id,
            `${v(s.dataset)} · group ${s.source_index}${s.title ? ` · ${s.title}` : ""}`,
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
class Ft extends E {
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
      Q,
      re`
      :host {
        display: block;
      }
      .comparison-scroll {
        overflow-x: auto;
      }
      .bars {
        min-width: 560px;
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
    const e = Ot(this.rows), t = e.find((o) => o.key === this.selected) ?? e[0];
    if (!t)
      return l`<div class="notice">
        Load pages containing driver summaries or supported
        race/stage/loop/average records to compare their metrics.
      </div>`;
    const i = t.observations.flatMap(
      (o) => o.value === null ? [] : [o.value]
    ), s = Math.min(0, ...i), a = Math.max(0, ...i), n = (o) => 165 + (o - s) / (a - s || 1) * 440, d = t.unit.includes("unverified") ? "Source unit · unverified" : v(t.unit);
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
                ${o.name} · ${v(o.classification)}
              </option>`
    )}
        </select></label
      >
      <p class="muted">
        <small
          >${v(t.classification)} · ${d} ·
          ${v(t.method)}. Loaded observations only.</small
        >
      </p>
      <div
        class="comparison-scroll"
        tabindex="0"
        role="region"
        aria-label="Summary comparison plot. Scroll for readable labels."
      >
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
      (o, u) => M`<text class="axis" x="8" y=${u * 44 + 24}>Driver ${o.driver}</text>${o.value !== null ? M`<rect class="bar" x=${Math.min(n(0), n(o.value))} y=${u * 44 + 7} width=${Math.max(1, Math.abs(n(o.value) - n(0)))} height="25" rx="3"></rect>` : M`<text class="axis" x="165" y=${u * 44 + 24}>Unavailable</text>`}<text class="axis" x="620" y=${u * 44 + 24}>${f(o.value, this.locale, 3)}</text>`
    )}
        </svg>
      </div>
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
              <th>Value · ${d}</th>
              <th>Availability</th>
            </tr>
          </thead>
          <tbody>
            ${t.observations.map(
      (o) => l`<tr>
                  <td>${o.driver}</td>
                  <td>${f(o.value, this.locale, 6)}</td>
                  <td>
                    ${o.reason ? v(o.reason) : "Reported by analytics API"}
                  </td>
                </tr>`
    )}
          </tbody>
        </table>
      </div>
    </section>`;
  }
}
customElements.define("nrc-metric-chart", Ft);
class jt extends E {
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
    this.styles = Q;
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
      const t = await Ze(this.hostHass);
      e === this.generation && (this.entries = t, this.error = void 0);
    } catch (t) {
      e === this.generation && (this.error = t);
    }
  }
  change(e, t) {
    const i = { ...this.config, [e]: t || void 0 };
    this.config = i, this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: i },
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
      ${this.error ? l`<p role="alert">${Ge(this.error)}</p>` : ""}<label class="field"
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
      (e) => l`<option value=${e}>${P[e]}</option>`
    )}
        </select></label
      ><label class="field"
        >Initial view<select
          .value=${this.config.section ?? "Race Center"}
          @change=${(e) => this.change("section", e.target.value)}
        >
          ${ue.map((e) => l`<option>${e}</option>`)}
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
customElements.define("nascar-race-center-card-editor", jt);
const Wt = "0.5.1";
class Bt extends E {
  constructor() {
    super(...arguments), this.config = { type: "custom:nascar-race-center-card" }, this.signature = "", this.epoch = 0, this.liveEpoch = 0, this.bootPending = !1, this.liveChain = Promise.resolve(), this.entries = [], this.loading = !1, this.section = "Race Center", this.series = 1, this.schedules = /* @__PURE__ */ new Map(), this.snapshots = /* @__PURE__ */ new Map(), this.compact = !1, this.historyKind = "all", this.chartMode = "time", this.chartWindow = 5, this.season = (/* @__PURE__ */ new Date()).getFullYear(), this.raceId = "", this.ready = () => {
      this.scheduleStart();
    }, this.disconnected = () => {
      this.clearRuntime(), this.error = new x("connection_error"), this.requestUpdate();
    };
  }
  static {
    this.styles = Q;
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
    if (e.section !== void 0 && !ue.includes(e.section))
      throw new Error("Unknown Race Center section.");
    this.config = { ...e }, this.section = e.section ?? "Race Center", this.clearRuntime(), this.scheduleStart(), this.requestUpdate();
  }
  set hass(e) {
    if (!e) return;
    const t = this.hostHass?.connection !== e.connection, i = JSON.stringify([
      e.user?.is_admin,
      e.locale,
      e.config?.time_zone
    ]), s = i !== this.signature;
    this.signature = i, this.hostHass = e, t ? (this.unlisten(), this.clearRuntime(), this.isConnected && (this.listen(), this.scheduleStart())) : s && this.isConnected && this.scheduleStart(), s && this.requestUpdate();
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
      this.error = new x("unauthorized"), this.requestUpdate();
      return;
    }
    this.loading = !0, this.requestUpdate();
    try {
      if (!this.config.entry_id) {
        const a = await Ze(t);
        if (e !== this.epoch) return;
        this.entries = a;
        return;
      }
      const i = new wt(
        t,
        this.config.entry_id,
        () => e === this.epoch && this.isConnected
      );
      this.client = i;
      const s = await i.bootstrap();
      if (e !== this.epoch) return;
      this.bootstrapData = s, this.series = this.config.series_id && s.series_ids.includes(this.config.series_id) ? this.config.series_id : s.series_ids[0], this.setDefaultRace(), this.syncLive(), this.section === "Race Weekend" && this.loadSchedule();
    } catch (i) {
      e === this.epoch && (this.error = i);
    } finally {
      e === this.epoch && (this.loading = !1, this.requestUpdate());
    }
  }
  setDefaultRace() {
    const e = this.bootstrapData, t = e?.navigation.find((s) => s.series_id === this.series), i = e?.upcoming.find((s) => s.series_id === this.series);
    this.season = i?.season ?? t?.seasons.at(-1) ?? (/* @__PURE__ */ new Date()).getFullYear(), this.raceId = i?.race_id ?? "";
  }
  syncLive() {
    this.stopLive();
    const e = this.liveEpoch, t = this.client;
    !t || !["Race Center", "Live Timing"].includes(this.section) || (this.liveChain = this.liveChain.then(async () => {
      if (!(e !== this.liveEpoch || !this.isConnected))
        try {
          const i = await t.subscribe(
            this.series,
            (s) => {
              if (e !== this.liveEpoch) return;
              const a = this.liveData?.identity, n = s.identity;
              (a && (a.race_id !== n.race_id || a.run_id !== n.run_id) || s.availability !== "ok") && this.closeDetail(!1), s.session && (!a || a.race_id !== n.race_id) && this.resolveCurrentRace(s, e), this.liveData = s, this.error = void 0, this.requestUpdate();
            },
            (s) => {
              e === this.liveEpoch && (this.error = s, this.liveData = void 0, this.requestUpdate());
            }
          );
          e !== this.liveEpoch || !this.isConnected ? await i() : this.unsubscribe = i;
        } catch (i) {
          e === this.liveEpoch && (this.error = i, this.requestUpdate());
        }
    }));
  }
  async resolveCurrentRace(e, t) {
    this.currentRace = void 0;
    const i = e.identity.race_id;
    if (!i || !this.client) return;
    const s = this.bootstrapData?.upcoming.find(
      (a) => a.series_id === this.series && a.race_id === i
    );
    if (s) {
      this.currentRace = s;
      return;
    }
    try {
      const a = await this.client.schedule({
        series_id: this.series,
        race_id: ee(i),
        ...e.identity.season ? { season: e.identity.season } : {}
      });
      if (t !== this.liveEpoch) return;
      const n = a.records.find(
        (d) => d.kind === "race" && d.value?.race_id === i
      );
      if (n?.kind === "race" && n.value) {
        const d = a.records.filter((o) => o.kind === "session" && o.race_id === i).flatMap(
          (o) => o.kind === "session" && o.value && "session_id" in o.value ? [o.value] : []
        );
        this.currentRace = { ...n.value, sessions: d }, this.requestUpdate();
      }
    } catch {
    }
  }
  formatNumber(e, t, i = 0) {
    return f(e, S(this.hass), i);
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
    if (e || (e = new ce("schedule", { series_id: this.series }), this.schedules.set(this.series, e)), !e.current && !e.loading) {
      const t = e.load(this.client);
      this.requestUpdate(), await t, this.requestUpdate();
    }
  }
  async page(e, t) {
    if (!this.client) return;
    const i = t === "next" ? e.next(this.client) : t === "previous" ? e.previous(this.client) : e.load(
      this.client,
      t === "restart" ? 0 : e.current?.pagination.offset ?? 0,
      t === "restart"
    );
    this.requestUpdate(), await i, this.requestUpdate();
  }
  async openDriver(e, t) {
    this.closeDetail(!1), this.detailDriver = e, this.detailFocus = t?.composedPath().find((i) => i instanceof HTMLButtonElement), this.requestUpdate(), await this.updateComplete, this.renderRoot.querySelector(".detail-close")?.focus();
  }
  closeDetail(e = !0) {
    this.detail?.invalidate(), this.detail = void 0, this.detailDriver = void 0, this.detailError = void 0, e ? this.detailFocus?.focus() : this.renderRoot.querySelector(".detail-panel")?.contains(this.shadowRoot?.activeElement ?? null) && this.renderRoot.querySelector(
      '.nav [aria-current="page"]'
    )?.focus(), this.detailFocus = void 0, this.requestUpdate();
  }
  async loadDetail(e, t = !1) {
    if (!this.client) return;
    const i = this.epoch;
    try {
      this.detailError = void 0;
      const s = { series_id: this.series, collection: e };
      t || (s.driver_id = ee(
        this.detailDriver.driver_id,
        Number.MAX_SAFE_INTEGER
      ));
      const a = new ce(
        t ? "live_scoring" : "live_driver",
        s,
        this.liveData?.identity
      );
      this.detail?.invalidate(), this.detail = a;
      const n = a.load(this.client);
      this.requestUpdate(), await n, i === this.epoch && this.requestUpdate();
    } catch (s) {
      i === this.epoch && (this.detailError = s, this.requestUpdate());
    }
  }
  async submit(e, t = !1) {
    if (e.preventDefault(), !this.client) return;
    const i = e.target, s = new FormData(i);
    try {
      this.formError = void 0;
      const a = Number(s.get("season"));
      if (!Number.isInteger(a) || a < 1948 || a > 9999)
        throw new x("invalid_selection");
      const n = String(s.get("race")), d = ee(n), o = s.getAll("dataset").map(String).filter(
        (m) => Ne.includes(m)
      );
      if (!o.length) throw new x("invalid_selection");
      const u = {
        series_id: this.series,
        season: a,
        race_id: d,
        datasets: o
      };
      if (t) {
        const m = String(s.get("drivers")).split(",").map((A) => A.trim()).filter(Boolean);
        if (!m.length || m.length > 8 || new Set(m).size !== m.length)
          throw new x("invalid_selection");
        const $ = Number(s.get("first")), y = Number(s.get("last")), k = s.getAll("window").map(Number);
        if (!Number.isInteger($) || !Number.isInteger(y) || $ < 0 || y > 1e10 || y < $ || y - $ + 1 > 5e3 || m.length * (y - $ + 1) * k.length > 6e4)
          throw new x("invalid_selection");
        Object.assign(u, {
          driver_ids: m.map((A) => ee(A)),
          first_lap: $,
          last_lap: y,
          windows: k,
          time_basis: String(s.get("basis"))
        });
      }
      const b = t ? "analytics" : "history", p = b + JSON.stringify(u);
      let c = this.snapshots.get(p);
      if (!c) {
        for (const [m, $] of this.snapshots)
          ($.expired || !$.loading && !$.current) && this.snapshots.delete(m);
        if (this.snapshots.size >= 2)
          throw new x("snapshot_limit");
        c = new ce(b, u), this.snapshots.set(p, c);
      }
      if (t ? (this.analytics = c, u.windows?.includes(this.chartWindow) || (this.chartWindow = u.windows?.[0] ?? 5)) : this.history = c, this.season = a, this.raceId = n, !c.current) {
        const m = c.load(this.client);
        this.requestUpdate(), await m;
      }
      this.requestUpdate();
    } catch (a) {
      this.formError = a, this.requestUpdate();
    }
  }
  state(e, t, i = !1) {
    return l`<div class=${`state${i ? " loading" : ""}`} role="status">
      <h3>${e}</h3>
      <p class="muted">${t}</p>
    </div>`;
  }
  errorView(e, t) {
    return l`<div class="state error" role="alert">
      <h3>Unable to load this view</h3>
      <p>${Ge(e)}</p>
      ${t ? l`<div><button @click=${t}>Retry / reconnect</button></div>` : h}
    </div>`;
  }
  badge(e, t = "neutral", i = !1) {
    return l`<span class=${`badge ${t}${i ? " race-flag" : ""}`}
      >${e}</span
    >`;
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
          ${e.pages.size > 1 ? l`<label class="field"
                >Loaded page<select
                  aria-label="Return to loaded page"
                  .value=${String(t?.offset ?? 0)}
                  ?disabled=${e.loading || e.expired}
                  @change=${async (i) => {
      this.client && (await e.jump(
        this.client,
        Number(i.target.value)
      ), this.requestUpdate());
    }}
                >
                  ${[...e.pages.values()].sort((i, s) => i.pagination.offset - s.pagination.offset).map(
      (i) => l`<option value=${i.pagination.offset}>
                          ${this.formatNumber(
        i.pagination.offset + 1
      )}–${this.formatNumber(
        i.pagination.offset + i.pagination.returned
      )}
                        </option>`
    )}
                </select></label
              >` : h}
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
    const e = this.bootstrapData, t = this.liveData, i = t?.session, s = i ? this.currentRace : e.upcoming.find((c) => c.series_id === this.series), a = e.upcoming.find((c) => c.series_id === this.series), n = [
      s?.start_time,
      ...(s?.sessions ?? []).map((c) => c.start_time)
    ].filter(
      (c) => !!c && q(c) !== null && q(c) > Date.now()
    ).sort((c, m) => q(c) - q(m))[0], d = de(t), o = ze(t), u = t?.leaderboard?.find(
      (c) => c.driver_id === t.leader_driver_id
    ), b = kt(n), p = t?.leaderboard?.filter((c) => c.favorite) ?? [];
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">Your race day, in focus</p>
          <h2>Race Center</h2>
        </div>
        ${this.badge(d.text, d.tone)}
      </div>
      <section class="panel hero">
        <div class="hero-content">
          <p class="eyebrow">
            ${P[this.series]} ·
            ${i ? "Reported session" : s ? "Next known event" : "Schedule & live coverage"}
          </p>
          <h3 class="race-title">
            ${i?.run_name ?? s?.name ?? "Waiting for the next green flag."}
          </h3>
          <p class="hero-track">
            ${s?.track ?? "Track not reported"}${s?.season ? ` · ${s.season}` : ""}
          </p>
          <div class="actions">
            ${i ? this.badge(o.text, o.tone, !0) : this.badge(s?.status ?? "No active session")}${i ? this.badge(
      `${v(i.status)} · ${v(i.progress)}`
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
          ${i ? l`<div>
                  <p class="eyebrow">Reported lap</p>
                  <p class="lap-count">
                    ${this.formatNumber(i.lap)}
                    <span>/ ${this.formatNumber(i.total_laps)}</span>
                  </p>
                </div>
                ${i.lap !== null && i.total_laps !== null && i.total_laps > 0 ? l`<div
                      class="progress"
                      role="meter"
                      aria-label="Reported session laps"
                      aria-valuemin="0"
                      aria-valuemax=${i.total_laps}
                      aria-valuenow=${Math.min(i.lap, i.total_laps)}
                    >
                      <div
                        style=${`width:${Math.max(0, Math.min(100, i.lap / i.total_laps * 100))}%`}
                      ></div>
                    </div>` : h}
                <p>
                  <small>Leading the reported field</small><br /><strong
                    >${u?.name ?? "Leader unavailable"}</strong
                  >
                </p>` : l`<div>
                  <p class="eyebrow">
                    ${b ? "Starts in" : "Event time"}
                  </p>
                  <p class="lap-count">${b ?? "—"}</p>
                </div>
                <p>
                  ${U(n, this.hass)}<br /><small
                    >${b ? "Known future instant" : "No reliable future instant available"}</small
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
          ><strong>${this.formatNumber(i?.laps_remaining)}</strong>
        </div>
        <div class="stat">
          <span>Stage observation</span
          ><strong>${this.formatNumber(i?.stage?.number)}</strong>
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
      (c) => l`<button
                      class="panel favorite"
                      @click=${(m) => void this.openDriver(c, m)}
                    >
                      <span class="row"
                        ><span class="car">${c.car_number ?? "—"}</span
                        ><span class="position"
                          >P${this.formatNumber(c.position)}</span
                        ></span
                      ><strong>${c.name ?? `Driver ${c.driver_id}`}</strong
                      ><small
                        >★ Favorite ·
                        ${c.running_status ?? "Status unknown"}</small
                      >
                    </button>`
    )}
              </div>` : l`<div class="panel">
                <p>
                  ${e.favorite_driver_ids.length ? "Favorite timing is unavailable for this series." : "Choose favorite drivers in the integration options."}
                </p>
                ${e.references.drivers.map(
      (c) => l`<p class="muted">★ ${c.name} · ${c.driver_id}</p>`
    )}
              </div>`}
        </section>
        <section class="panel stack">
          <h3>${i ? "Next known weekend" : "Weekend notebook"}</h3>
          ${a?.sessions?.length ? a.sessions.map(
      (c) => l`<div>
                    <p>${c.name} <small>· ${v(c.kind)}</small></p>
                    <small>${U(c.start_time, this.hass)}</small>
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
      ${t?.leaderboard?.length ? l`<section class="panel overview-field">
            <div class="row">
              <h3>${w.front}</h3>
              <button @click=${() => this.navigate("Live Timing")}>
                Full timing tower →
              </button>
            </div>
            <div class="front-grid">
              ${t.leaderboard.slice().sort(
      (c, m) => (c.position ?? 1 / 0) - (m.position ?? 1 / 0)
    ).slice(0, 5).map(
      (c) => l`<button
                      @click=${(m) => void this.openDriver(c, m)}
                    >
                      <span class="muted"
                        >P${this.formatNumber(c.position)}</span
                      ><span class="car">${c.car_number ?? "—"}</span
                      ><strong
                        >${c.favorite ? "★ " : ""}${c.name ?? `Driver ${c.driver_id}`}</strong
                      >
                    </button>`
    )}
            </div>
          </section>` : h}
      ${i ? h : this.state(
      "Session coverage",
      t ? `${v(t.availability)}. Timing appears only when the source supplies fresh matching observations.` : "Waiting for the first live source snapshot.",
      !t
    )}${this.renderDetail()}
    </div>`;
  }
  renderTiming() {
    const e = this.liveData, t = e?.session, i = de(e), s = ze(e);
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${P[this.series]} · Timing tower</p>
          <h2>${t?.run_name ?? "Live Timing"}</h2>
          <p class="muted">
            ${v(t?.status)}${t ? ` · Reported lap ${this.formatNumber(t.lap)} / ${this.formatNumber(t.total_laps)}` : ""}
          </p>
        </div>
        <div class="actions">
          ${this.badge(i.text, i.tone)}${t ? this.badge(s.text, s.tone, !0) : h}
        </div>
      </div>
      ${e?.leaderboard?.length ? l`<nrc-leaderboard
            .rows=${e.leaderboard}
            .hass=${this.hass}
            .compact=${this.compact}
            @driver-open=${(a) => void this.openDriver(a.detail, a)}
          ></nrc-leaderboard>` : this.state(
      e ? "No current timing" : "Connecting to the timing feed",
      e ? `${v(e.availability)}. Fresh matching observations are required; stale results are withheld.` : "Waiting for an authenticated live snapshot.",
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
                    ${v(a)} · ${v(e.scoring[a]?.status)}
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
      @keydown=${(i) => {
      i.key === "Escape" && this.closeDetail();
    }}
    >
      <div class="row">
        <h3>
          ${e ? `${e.name ?? e.driver_id} · #${e.car_number ?? "—"}` : `${v(t?.selection.collection)} observations`}
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
              ${O(e, 0, S(this.hass))}
            </details>` : h}${this.detailError ? this.errorView(this.detailError) : h}${t ? l`${t.current ? l`<p class="muted">
                  ${v(t.current.availability)} · ${v(t.current.reason)}
                  · Race ${t.current.identity?.race_id ?? "Unknown"} / timing
                  run ${t.current.identity?.run_id ?? "Unknown"}
                </p>
                ${t.current.provenance ? l`<details>
                      <summary>Source provenance</summary>
                      ${O(
      t.current.provenance,
      0,
      S(this.hass)
    )}
                    </details>` : h}
                <p class="notice">
                  Provisional reported observations. Source timing units remain
                  unverified.
                </p>
                ${t.current.records.length ? te(t.current.records, this.hass) : this.state(
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
    const e = this.schedules.get(this.series), t = e?.current?.records ?? [], i = t.filter((a) => a.kind === "race"), s = t.filter((a) => a.kind === "session");
    return l`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${P[this.series]} · Retained schedule</p>
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
        ${i.map((a) => {
      const n = a.value, d = this.bootstrapData?.references.tracks.find(
        (o) => o.track_id === n.track_id
      );
      return l`<article class="panel event-card">
            <div class="event-number">${n.season ?? "—"}</div>
            <div>
              <p class="eyebrow">${n.track ?? "Track unknown"}</p>
              <h3>${n.name}</h3>
              <p class="muted">
                ${U(n.start_time, this.hass)} · ${v(n.status)}
              </p>
              ${d ? l`<small
                    >${d.city ?? ""}${d.state ? `, ${d.state}` : ""}
                    · ${v(d.track_type)} ·
                    ${this.formatNumber(d.length_miles, void 0, 2)}
                    reported miles</small
                  >` : h}
              <div class="sessions">
                ${s.filter(
        (o) => o.race_id === n.race_id && o.season === n.season
      ).map((o) => {
        const u = o.value;
        return "session_id" in u ? l`<div class="session-row">
                          <span
                            >${u.name} <small>· ${v(u.kind)}</small></span
                          ><span
                            >${U(u.start_time, this.hass)}<small>
                              · ${v(u.status)}</small
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
    })}${s.filter(
      (a) => !i.some(
        (n) => n.value?.race_id === a.race_id && n.value?.season === a.season
      )
    ).length ? l`<p class="notice">
                This page continues the preceding race's sessions. Parent race
                IDs are retained below.
              </p>
              ${te(
      s.filter(
        (a) => !i.some(
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
    ), i = e ? this.analytics?.selection : this.history?.selection, s = i?.datasets ?? (e ? ["laps", "weekend"] : ["weekend"]), a = [...this.schedules.get(this.series)?.records ?? []].filter((n) => n.kind === "race").map((n) => n.value).concat(
      this.bootstrapData?.upcoming.filter(
        (n) => n.series_id === this.series
      ) ?? []
    ).filter(
      (n, d, o) => o.findIndex(
        (u) => u.race_id === n.race_id && u.season === n.season
      ) === d
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
      (n) => l`<option value=${n}>${P[n]}</option>`
    )}
          </select></label
        ><label class="field"
          >Season<input
            name="season"
            type="number"
            required
            min="1948"
            max="9999"
            .value=${String(i?.season ?? this.season)}
            list="retained-seasons" /></label
        ><datalist id="retained-seasons">
          ${t?.seasons.map((n) => l`<option value=${n}></option>`)}</datalist
        ><label class="field wide"
          >Known retained race<select
            @change=${(n) => {
      const [d, o] = n.target.value.split(":");
      if (o) {
        this.season = Number(d), this.raceId = o;
        const u = n.target.closest("form");
        u.elements.namedItem("season").value = d, u.elements.namedItem("race").value = o;
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
            .value=${String(i?.race_id ?? this.raceId)}
            placeholder="e.g. 88001"
        /></label>
      </div>
      <div class="filters">
        <fieldset>
          <legend>Explicit datasets</legend>
          ${Ne.map(
      (n) => l`<label class="check"
                ><input
                  type="checkbox"
                  name="dataset"
                  value=${n}
                  .checked=${s.includes(n)}
                />
                ${v(n)}</label
              >`
    )}
        </fieldset>
      </div>
      ${e ? l`<div class="filters">
              <label class="field wide"
                >NASCAR driver IDs · comma separated, 1–8<input
                  name="drivers"
                  required
                  .value=${i?.driver_ids?.join(", ") ?? this.bootstrapData.favorite_driver_ids.slice(0, 2).join(
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
                  .value=${String(i?.first_lap ?? 1)} /></label
              ><label class="field"
                >Last lap<input
                  type="number"
                  name="last"
                  min="0"
                  max="10000000000"
                  required
                  .value=${String(i?.last_lap ?? 100)} /></label
              ><label class="field wide"
                >Comparison time basis<select
                  name="basis"
                  .value=${i?.time_basis ?? "all_available"}
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
                        .checked=${(i?.windows ?? [5]).includes(n)}
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
  retainedSelections() {
    return this.snapshots.size ? l`<details class="selection-library">
          <summary>${w.retained}</summary>
          <div class="actions">
            ${[...this.snapshots.values()].map(
      (e) => l`<button
                  @click=${() => {
        this.formError = void 0, this.selectSeries(e.selection.series_id), this.season = e.selection.season, this.raceId = String(e.selection.race_id), e.command === "history" ? this.history = e : (this.analytics = e, e.selection.windows?.includes(this.chartWindow) || (this.chartWindow = e.selection.windows?.[0] ?? 5)), this.navigate(
          e.command === "history" ? "History" : "Analytics"
        ), this.requestUpdate();
      }}
                >
                  ${e.command === "history" ? "History" : "Analytics"} ·
                  ${P[e.selection.series_id]} · ${e.selection.season} /
                  ${e.selection.race_id}${e.expired ? " · expired" : ""}
                </button>`
    )}
          </div>
          <p class="muted"><small>${w.snapshotHint}</small></p>
        </details>` : h;
  }
  renderHistory() {
    const e = this.history, t = e?.current, i = t?.records.some((s) => s.kind === this.historyKind) ? this.historyKind : "all";
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
      ${this.retainedSelections()}${this.renderForm(!1)}${t ? l`<div class="section-head">
              <h3>
                ${t.records.find((s) => s.kind === "weekend")?.value?.name ?? `Race ${t.race?.race_id ?? this.raceId}`}
              </h3>
              ${this.badge(v(t.status))}
            </div>
            ${Te(t, this.hass)}${this.pager(e)}${Et(
      t.records,
      this.hass
    )}${t.records.length ? l`<label class="field"
                    >${w.records}<select
                      aria-label=${w.records}
                      .value=${i}
                      @change=${(s) => {
      this.historyKind = s.target.value, this.requestUpdate();
    }}
                    >
                      <option value="all">All supported record types</option>
                      ${[...new Set(t.records.map((s) => s.kind))].map(
      (s) => l`<option value=${s}>${v(s)}</option>`
    )}
                    </select></label
                  >
                  <details ?open=${i !== "all"}>
                    <summary>
                      Explore ${t.records.length} records on this page ·
                      metadata, stages, laps, notes & pits
                    </summary>
                    ${te(
      t.records.filter(
        (s) => i === "all" || s.kind === i
      ),
      this.hass
    )}
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
    )}${e && !t ? this.pager(e) : h}
    </div>`;
  }
  renderAnalytics() {
    const e = this.analytics, t = e?.current, i = e?.records ?? [], s = this.chartMode === "window" ? i.filter((a) => a.kind !== "window" || a.size === this.chartWindow) : i;
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
      ${this.retainedSelections()}${this.renderForm(!0)}${t ? l`<div class="row">
              <h3>
                Selected race ${t.query?.key.race_id ?? "—"} · laps
                ${t.query?.first_lap ?? "—"}–${t.query?.last_lap ?? "—"}
              </h3>
              ${this.badge(v(t.status))}
            </div>
            <p class="notice">
              ${v(t.query?.time_basis)} · ${v(t.reason)}. Charts
              and summaries contain loaded pages only. Continue paging for later
              drivers, comparisons and reported performance; retention is
              bounded to 1,600 records.
            </p>
            ${Te(t, this.hass)}${this.pager(e)}
            <p class="notice" role="status">
              Loaded record ranges:
              ${[...e.pages.values()].sort((a, n) => a.pagination.offset - n.pagination.offset).map(
      (a) => `${this.formatNumber(a.pagination.offset + 1)}–${this.formatNumber(a.pagination.offset + a.pagination.returned)}`
    ).join(", ")}
              of ${this.formatNumber(t.pagination.total)}. These ranges
              include headers and metrics, not only lap samples.
            </p>
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
                  <option
                    value="window"
                    ?disabled=${!t.query?.windows.length}
                  >
                    Consecutive-window mean
                  </option>
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
              .rows=${s}
              .mode=${this.chartMode}
              .locale=${S(this.hass)}
            ></nrc-chart>
            <nrc-metric-chart
              .rows=${i}
              .locale=${S(this.hass)}
            ></nrc-metric-chart>
            ${i.filter((a) => a.kind === "driver").map(
      (a) => l`<section class="stack">
                    <h3>
                      Driver ${a.driver_id} · ${v(a.value?.status)} ·
                      fastest recorded lap
                      ${this.formatNumber(a.value?.fastest_lap)}
                    </h3>
                    <div class="metric-grid">
                      ${a.value?.metrics.map(
        (n) => Ie(n, S(this.hass))
      )}
                    </div>
                    <details>
                      <summary>Coverage and exclusions</summary>
                      ${O(a.value?.coverage, 0, S(this.hass))}
                      <p>${v(a.value?.reason)}</p>
                    </details>
                  </section>`
    )}${t.race_metrics?.length ? l`<div class="metric-grid">
                  ${t.race_metrics.map(
      (a) => Ie(a, S(this.hass))
    )}
                </div>` : h}
            <details>
              <summary>
                Comparisons, consecutive windows & reported performance ·
                current page
              </summary>
              ${te(
      t.records.filter((a) => a.kind !== "samples"),
      this.hass
    )}
            </details>
            <details>
              <summary>Analytics caveats</summary>
              ${t.caveats?.map((a) => l`<p>${v(a)}</p>`)}
            </details>` : e?.loading ? this.state(
      "Calculating selected observations",
      "The backend applies the existing analytics contract and computation limits.",
      !0
    ) : this.state(
      "Build a comparison",
      "Choose drivers, lap range, datasets and a supported window."
    )}${e && !t ? this.pager(e) : h}
    </div>`;
  }
  render() {
    const e = this.bootstrapData, t = de(this.liveData);
    return l`<ha-card ?data-compact=${this.compact}
      ><header class="masthead">
        <div class="brand">
          <span class="brand-mark" aria-hidden="true"
            ><i></i><i></i><i></i
          ></span>
          <div>
            <h1 class="brand-title">
              ${this.config.title ?? "NASCAR Race Center"}
            </h1>
            <p class="eyebrow">Race intelligence · Home Assistant</p>
          </div>
        </div>
        ${e ? l`<div class="tools">
              <label class="series-label"
                ><span class="eyebrow">${w.density}</span
                ><select
                  aria-label=${w.density}
                  .value=${this.compact ? "compact" : "comfortable"}
                  @change=${(i) => {
      this.compact = i.target.value === "compact", this.requestUpdate();
    }}
                >
                  <option value="comfortable">${w.comfortable}</option>
                  <option value="compact">${w.compact}</option>
                </select></label
              >
              <label class="series-label"
                ><span class="eyebrow">Series</span
                ><select
                  aria-label="Selected series"
                  .value=${String(this.series)}
                  @change=${(i) => this.selectSeries(
      Number(i.target.value)
    )}
                >
                  ${e.series_ids.map(
      (i) => l`<option value=${i}>${P[i]}</option>`
    )}
                </select></label
              >
            </div>` : h}
      </header>
      ${e?.provider === "demo" ? l`<div class="demo" role="note">
            DEMONSTRATION · Simulated races & drivers · not genuine NASCAR
            results · offline provider
          </div>` : h}${e ? l`<nav class="nav" aria-label="Race Center sections">
            ${ue.map(
      (i) => l`<button
                  aria-current=${i === this.section ? "page" : h}
                  @click=${() => this.navigate(i)}
                >
                  ${i}
                </button>`
    )}
          </nav>` : h}
      <main
        @keydown=${(i) => {
      i.key === "Escape" && (this.detailDriver || this.detail) && this.closeDetail();
    }}
        aria-busy=${this.loading ? "true" : "false"}
      >
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
                  @change=${(i) => {
      const s = i.target.value;
      s && this.chooseEntry(s);
    }}
                >
                  <option value="">Select an entry</option>
                  ${this.entries.map(
      (i) => l`<option
                        ?disabled=${i.state !== "loaded"}
                        value=${i.entry_id}
                      >
                        ${i.title} · ${i.state}
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
          >${e ? `${e.provider === "demo" ? "Simulated" : "Experimental"} source · ${v(this.section === "History" || this.section === "Analytics" ? "on_demand_snapshot" : t.text)}` : "Authenticated dashboard API v1"}</span
        ><span
          >Content updated:
          ${U(this.liveData?.source_updated_at, this.hass)}</span
        ><span>Card ${Wt} · API v1</span>
      </footer></ha-card
    >`;
  }
}
customElements.define("nascar-race-center-card", Bt);
const me = window;
me.customCards ??= [];
me.customCards.some((r) => r.type === "nascar-race-center-card") || me.customCards.push({
  type: "nascar-race-center-card",
  name: "NASCAR Race Center",
  description: "Five racing views with authenticated dashboard API v1. Administrator access required.",
  preview: !0
});
export {
  Bt as NascarRaceCenterCard,
  Wt as VERSION
};
