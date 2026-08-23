/**
 * The 아이디콘's smoke check — one case, no framework.
 *
 * A browser pass sees one account's mark and cannot tell a faithful algorithm
 * from a plausible one. What the record actually pins is arithmetic: the same
 * seed always draws the same mark (case- and whitespace-insensitive), every row
 * is mirrored about column 2, and the hue is the hash's own index into the four
 * data hues — never `--alert`, never `--brand`.
 */

import assert from "node:assert/strict";
import test from "node:test";
import { IDENTICON_HUES, identicon } from "./identicon.ts";

test("deterministic, mirrored, and one of the four data hues", () => {
  const mark = identicon("leetusik@gmail.com");

  // Same key → same mark; `seed.trim().toLowerCase()` is the key, not the seed.
  assert.deepEqual(identicon("  LeeTusik@Gmail.com  "), mark);
  // A different account is a different mark (both halves of it here).
  const other = identicon("reader@example.co.kr");
  assert.notDeepEqual(other, mark);

  assert.equal(mark.cells.length, 5);
  for (const row of mark.cells) {
    assert.equal(row.length, 5);
    assert.equal(row[0], row[4]);
    assert.equal(row[1], row[3]);
  }

  // The hue is `hues[fnv1a32(key) % 4]` — 2269685826 % 4 = 2 and 1895017235 % 4
  // = 3 for these two keys, so the index is asserted rather than a colour, and
  // `--alert`/`--brand` are not in the list at all.
  assert.ok(IDENTICON_HUES.includes(mark.hue));
  assert.equal(mark.hue, "--r3");
  assert.equal(other.hue, "--live");
});
