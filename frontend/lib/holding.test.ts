/**
 * The one multiplication site's smoke check — three cases, no framework.
 *
 * Run by `npm run smoke` (`node --test lib/*.test.ts`), Node's own runner with
 * its native TypeScript stripping. The repo rule is terse tests, so this covers
 * only what a render cannot show and what a wrong answer would publish: the
 * flooring rule, the no-money-before-확정발행가 branch, and that the arithmetic
 * is exact rather than floating.
 */

import assert from "node:assert/strict";
import test from "node:test";
import { won } from "./format.ts";
import { allottedShares, convert, excessLimit, sumValues } from "./holding.ts";

const fact = (value: string) => ({ value, estimated: false });
const estimate = (value: string) => ({ value, estimated: true });

test("⌊N × 배정비율⌋ floors on the exact digits (단수주 절사), all ten decimals", () => {
  // R4's own worked example, and the live 한화솔루션 factors: 500 ×
  // 0.2465120994 = 123.256… → 123주. `Number(500 * 0.2465120994)` happens to
  // agree here; the point is that the ratio is never parsed into a float, so a
  // ratio whose product lands microscopically below an integer cannot round up.
  assert.equal(allottedShares(500, "0.2465120994"), 123);
  assert.equal(allottedShares(500, "0.2314082845"), 115); // 계양전기
  assert.equal(excessLimit(123, "0.2"), 24);
  assert.equal(excessLimit(115, "0.2"), 23);
  // Exactly on the boundary: 0.9999999999 × 10 is 9.999999999, never 10.
  assert.equal(allottedShares(10, "0.9999999999"), 9);
});

test("한화솔루션 500주 reproduces R4's 679,575원 — and its floor — from factors only", () => {
  const conversion = convert(
    {
      price_confirmed: true,
      allotment_ratio: fact("0.2465120994"),
      excess_ratio: fact("0.2"),
      unit_value: estimate("5525"),
      unit_value_floor: estimate("4432.367726441982100185942246"),
    },
    500,
  );

  assert.equal(conversion.allotted, 123);
  assert.equal(conversion.excess, 24);
  assert.equal(conversion.value, "679575");
  assert.equal(won(conversion.value!), "679,575원");
  assert.equal(won(conversion.valueFloor!), "545,181원");
  // The tag is the payload's, never a literal (`P5.S10` note 9).
  assert.equal(conversion.valueEstimated, true);
  assert.equal(sumValues([conversion.value!, "1.5"]), "679576.5");
});

test("확정발행가 null ⇒ no money number at all; the share counts still convert", () => {
  // 계양전기's live ① today: `price_confirmed: false`, and the payload carries
  // no `unit_value` key at all. Money must be unreachable, not merely unrendered.
  const conversion = convert(
    {
      price_confirmed: false,
      allotment_ratio: fact("0.2314082845"),
      excess_ratio: fact("0.2"),
    },
    500,
  );

  assert.equal(conversion.value, null);
  assert.equal(conversion.valueFloor, null);
  assert.equal(conversion.allotted, 115);
  assert.equal(conversion.excess, 23);

  // No holding entered is not zero: nothing converts, so nothing is stated.
  const none = convert({ allotment_ratio: fact("0.2465120994") }, null);
  assert.deepEqual([none.allotted, none.excess, none.value], [null, null, null]);
});
