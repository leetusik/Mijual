/**
 * The code→copy mapping's smoke check — two cases, no framework.
 *
 * Run by `npm run smoke` (`node --test lib/*.test.ts`, Node's own runner with its
 * native type stripping), which is why a test for `components/auth/copy.ts` lives
 * here: the glob is the qa contract `P5.S10` set, and the module under test is
 * pure strings with no React import, so it loads unchanged.
 *
 * What is worth pinning is exactly what a browser cannot show: that each signed
 * failure line is reachable from the structural code `P5.S7` emits for it, **and
 * that nothing else is** — the second case is the one that fails if a later slice
 * ever answers an unmapped code with an invented sentence.
 *
 * **R12 (2026-08-24)** closed two of the three recorded gaps: `invalid_email` and
 * `invalid_reset_token` now have signed Korean, so they move from the second case
 * to the first. `csrf_required` and a transport failure stay unmapped by design.
 */

import assert from "node:assert/strict";
import test from "node:test";
import {
  ERR_EMAIL_TAKEN_KO,
  ERR_INVALID_CREDENTIALS_KO,
  ERR_INVALID_EMAIL_KO,
  ERR_PASSWORD_TOO_SHORT_KO,
  ERR_RESET_TOKEN_KO,
  authErrorKo,
} from "../components/auth/copy.ts";

test("the five signed lines, each from the code the API actually sends", () => {
  // 불일치 — one code for a wrong password *and* for an address with no account
  // (`mijual.web.auth._invalid_credentials`), so the line names no field.
  assert.equal(authErrorKo("invalid_credentials"), ERR_INVALID_CREDENTIALS_KO);
  assert.equal(authErrorKo("email_taken"), ERR_EMAIL_TAKEN_KO);
  assert.equal(authErrorKo("password_too_short"), ERR_PASSWORD_TOO_SHORT_KO);
  assert.equal(ERR_INVALID_CREDENTIALS_KO, "이메일 또는 비밀번호가 일치하지 않습니다.");
  // R12's two: a malformed address (the browser no longer refuses it in English)
  // and an expired or already-spent reset link (which used to answer nothing).
  assert.equal(authErrorKo("invalid_email"), ERR_INVALID_EMAIL_KO);
  assert.equal(authErrorKo("invalid_reset_token"), ERR_RESET_TOKEN_KO);
});

test("every other code renders no line — an unsigned failure is never given words", () => {
  for (const code of ["csrf_required", "unauthenticated", "http_error", ""]) {
    assert.equal(authErrorKo(code), null, code);
  }
});
