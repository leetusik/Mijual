/**
 * R5's auth surfaces and its two conversion touchpoints (`P5.S15`).
 *
 * The panels are the `/auth/*` pages'; `ConversionOffer` and `DeadlineOffer` are
 * mounted **on other slices' surfaces** — 내 종목 조회 (`P5.S14`) and the event
 * detail page (`P5.S13`) — because R5-2 places them there. They are exported here
 * so those surfaces import one R5 element rather than re-render R5's copy.
 *
 * 내 포트폴리오 itself, the logged-in account menu and the sample *mode* are
 * `P5.S16`'s; this folder deliberately builds none of them.
 *
 * **R12 removed one export**: `PiiInset` — the two-line PII panel R5-1 made a
 * 상시 요소 of the auth screen — is deleted with its component and its two
 * constants (operator instruction, 2026-08-24). `AuthRail` is internal to the two
 * panels and is not exported: it is this surface's own row, not an element other
 * surfaces compose.
 */
export { AuthPanel } from "./AuthPanel";
export { ResetConfirmPanel } from "./ResetConfirmPanel";
export { SampleEntry } from "./SampleEntry";
export { ConversionOffer } from "./ConversionOffer";
export { DeadlineOffer } from "./DeadlineOffer";
