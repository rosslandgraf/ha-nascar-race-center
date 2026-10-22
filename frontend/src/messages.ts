/** English source catalog. Formatting follows HA; translations are future work. */
export const messages = {
  density: "Display density",
  comfortable: "Comfortable",
  compact: "Compact",
  measurements: "All measurements",
  essential: "Essential columns",
  towerHint:
    "Open a driver for details. Scroll within the table for more measurements.",
  sortHint:
    "Reported position is the default. Change is relative to the start, not an on-track pass.",
  inspect: "Inspect observation",
  previousPoint: "Previous observation",
  nextPoint: "Next observation",
  missing: "Missing / excluded observation",
  chartScope: "Loaded pages only; missing observations break lines.",
  retained: "Return to a retained selection",
  snapshotHint:
    "Reusing a selection creates no snapshot. Slots remain occupied until server expiry; clearing local data does not release them.",
  front: "Front of the reported field",
  records: "Record types on this page",
} as const;
