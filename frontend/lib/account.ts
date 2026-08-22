/**
 * The account slot's 축약 이메일 (R5 §Chrome).
 *
 * > Desktop: links 불변(R2 삼분할) · 로그인 링크 → **축약 이메일 메뉴(mono, 앞 4자
 * > + … + 도메인 끝)**: 내 포트폴리오 / 알림 설정 / 로그아웃.
 *
 * The chrome shows *that this browser has an account* without printing the
 * address across the top of every page: `GET /auth/me` serves the full email
 * (`P5.S7` note 13 — "the 축약 (앞 4자 + … + 도메인 끝) is `P5.S11`/`P5.S16`'s
 * rendering") and this is where the product's one abbreviation lives, so the
 * desktop menu and the mobile sheet cannot spell it two ways.
 *
 * Two readings the record leaves to the build, both recorded for `P5.S19` to
 * check against the `ChromeSession` card:
 *
 * 1. **앞 4자 never crosses the `@`.** On an address whose local part is shorter
 *    than four characters, four characters of *the address* would print part of
 *    the domain and read as a different address; the head is clamped to the local
 *    part instead.
 * 2. **도메인 끝 = the domain's last label** (`gmail.com` → `com`,
 *    `example.co.kr` → `kr`), which is the part of a domain that is still a fact
 *    about it once the rest is hidden.
 *
 * An address that is already no longer than its abbreviation is printed whole —
 * an "abbreviation" that is longer than the thing it shortens hides nothing and
 * would be a second spelling of the same address.
 */

/** 앞 4자 — the record's own number. */
const HEAD = 4;

/** The record's own ellipsis character. */
const ELLIPSIS = "…";

export function abbreviateEmail(email: string): string {
  const address = email.trim();
  const at = address.lastIndexOf("@");
  if (at <= 0) return address;

  const head = address.slice(0, Math.min(HEAD, at));
  const domain = address.slice(at + 1);
  if (domain === "") return address;

  const dot = domain.lastIndexOf(".");
  const tail = dot >= 0 ? domain.slice(dot + 1) : domain;
  if (tail === "") return address;

  const abbreviated = `${head}${ELLIPSIS}${tail}`;
  return abbreviated.length < address.length ? abbreviated : address;
}
