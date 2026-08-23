/**
 * One body-scroll lock, counted — so two overlays cannot fight over it.
 *
 * R8 puts two of them on the same screen at ≤480: the menu sheet locks the page
 * while it is open, and the 의견 보내기 bottom sheet does the same. Each had its
 * own `document.body.style.overflow` save/restore at first, and the overlap is a
 * real bug that a browser pass caught: the feedback sheet mounts while the menu
 * sheet is still up, **captures `"hidden"` as the value to restore**, and then
 * the menu sheet's own cleanup writes `""` back — so the page was scrollable
 * behind the open sheet, and locked again after it closed. Measured, not
 * theoretical.
 *
 * A counter fixes both halves: the first lock records the page's own value and
 * sets `hidden`, the last release puts that value back, and a release is
 * idempotent so React's StrictMode double-invoked effects (the operator browses
 * `next dev`) cannot decrement twice.
 *
 * It touches `overflow` and nothing else — no `position: fixed` body, no scroll
 * offset restoration — because the page underneath must not move: R2's cosmos
 * backdrop is `position: fixed` behind everything, and moving the document would
 * shift the surface the overlay is drawn on.
 */

let locks = 0;
let previous = "";

export function lockBodyScroll(): () => void {
  if (typeof document === "undefined") return () => undefined;

  if (locks === 0) {
    previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
  }
  locks += 1;

  let released = false;
  return () => {
    if (released) return;
    released = true;
    locks -= 1;
    if (locks === 0) document.body.style.overflow = previous;
  };
}
