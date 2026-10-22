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
    "Reusing a retained selection creates no snapshot. Older selections are released as you explore; each card retains at most two recent selections.",
  front: "Front of the reported field",
  records: "Record types on this page",
} as const;
