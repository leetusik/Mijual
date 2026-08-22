/**
 * The 축약 이메일's smoke check — one case, no framework.
 *
 * The account menu is chrome, so a browser pass sees whatever address the test
 * account happens to have; what a render cannot show is the rule itself, and the
 * rule is the only part of R5's slot that is arithmetic rather than layout.
 */

import assert from "node:assert/strict";
import test from "node:test";
import { abbreviateEmail } from "./account.ts";

test("앞 4자 + … + 도메인 끝, and it never crosses the @", () => {
  assert.equal(abbreviateEmail("leetusik@gmail.com"), "leet…com");
  assert.equal(abbreviateEmail("reader@example.co.kr"), "read…kr");
  // A local part shorter than four characters clamps rather than printing part
  // of the domain, which would read as a different address.
  assert.equal(abbreviateEmail("ab@mijual.kr"), "ab…kr");
  // Not an address shape — rendered as served, never reshaped into one.
  assert.equal(abbreviateEmail("reader"), "reader");
});
