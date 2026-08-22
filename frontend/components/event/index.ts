/**
 * The event detail surface (R3 — ①②③ + the trust states + the CorrectionStory).
 *
 * These components are this surface's, not the system's: the trust primitives
 * live in `@/components`, the global chrome in `@/components/chrome`, and both
 * are composed here rather than re-implemented. Every Korean string the surface
 * renders is transcribed with a citation in `./copy.ts`; every label that names a
 * field comes off the wire as `korean_name`.
 */
export { EventDetail } from "./EventDetail";
