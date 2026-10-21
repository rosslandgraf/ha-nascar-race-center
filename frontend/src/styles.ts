import { css } from "lit";
export const styles = css`
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
