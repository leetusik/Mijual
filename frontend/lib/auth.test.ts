/**
 * The code→copy mapping's smoke check — two cases, no framework.
 *
 * Run by `npm run smoke` (`node --test lib/*.test.ts`, Node's own runner with its
 * native type stripping), which is why a test for `components/auth/copy.ts` lives
 * here: the glob is the qa contract `P5.S10` set, and the module under test is
 * pure strings with no React import, so it loads unchanged.
 *
 * What is worth pinning is exactly what a browser cannot show: that each of R5's
 * three signed failure lines is reachable from the structural code `P5.S7` emits
 * for it, **and that nothing else is** — the second case is the one that fails if
 * a later slice ever answers an unmapped code with an invented sentence.
 */

import assert from "node:assert/strict";
import test from "node:test";
import {
  ERR_EMAIL_TAKEN_KO,
  ERR_INVALID_CREDENTIALS_KO,
  ERR_PASSWORD_TOO_SHORT_KO,
  authErrorKo,
} from "../components/auth/copy.ts";

test("R5's three signed lines, each from the code the API actually sends", () => {
  // 불일치 — one code for a wrong password *and* for an address with no account
  // (`mijual.web.auth._invalid_credentials`), so the line names no field.
  assert.equal(authErrorKo("invalid_credentials"), ERR_INVALID_CREDENTIALS_KO);
  assert.equal(authErrorKo("email_taken"), ERR_EMAIL_TAKEN_KO);
  assert.equal(authErrorKo("password_too_short"), ERR_PASSWORD_TOO_SHORT_KO);
  assert.equal(ERR_INVALID_CREDENTIALS_KO, "이메일 또는 비밀번호가 일치하지 않습니다.");
});

test("every other code renders no line — an unsigned failure is never given words", () => {
  for (const code of [
    "invalid_email",
    "invalid_reset_token",
    "csrf_required",
    "unauthenticated",
    "http_error",
    "",
  ]) {
    assert.equal(authErrorKo(code), null, code);
  }
});
