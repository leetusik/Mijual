/**
 * The landing 관제 현황판 (R2/R2.1 + R3's 추후결정 board strip).
 *
 * These components are this surface's, not the system's: the trust primitives
 * live in `@/components` and the global chrome in `@/components/chrome`, and both
 * are composed here rather than re-implemented. Every Korean string the surface
 * renders is transcribed with a citation in `./copy.ts`.
 */
export { Board } from "./Board";
export { Cosmos } from "./Cosmos";
export { Countdown } from "./Countdown";
export { Hero } from "./Hero";
export { LapseNotice } from "./LapseNotice";
export { RetrospectiveAnchor } from "./Anchor";
