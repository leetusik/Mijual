/**
 * The R1/R2 trust primitives. **Every surface composes these; none re-invents
 * one** (`docs/current/frontend.md` §Component conventions).
 *
 * `P5.S11`–`P5.S17` build pages out of this set. If a page needs a variation,
 * the variation belongs in the primitive with a named prop and a citation to the
 * round that specifies it — not in a local copy, and never as a restyle.
 */
export { CraftPanel, type CraftPanelProps } from "./CraftPanel";
export { EstimateMarker, type EstimateMarkerProps } from "./EstimateMarker";
export { Citation, type CitationProps } from "./Citation";
export { StateBadge, type StateBadgeProps } from "./StateBadge";
export { DDay, urgencyClass, type DDayProps } from "./DDay";
export { RightsChip, type RightsChipProps } from "./RightsChip";
export { LapseAlert, lapseNumeralClass, type LapseAlertProps } from "./LapseAlert";
/** R8's account mark — a chrome component by placement, a shared primitive by
 * shape (the account surface renders it at 40px too). */
export { Identicon, type IdenticonProps } from "./Identicon";
