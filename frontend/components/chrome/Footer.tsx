import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import type { SiteContact } from "@/lib/types";
import { ASK_LABEL_KO, COPYRIGHT_KO, SOURCE_KO } from "./copy";
import { FeedbackEntry } from "./Feedback";
import { Wordmark } from "./Wordmark";
import styles from "./Footer.module.css";

/**
 * The global footer — R2 §Page shell, **re-cut by R8 §4** (SIGNOFF: R8
 * supersedes R2's footer content and type).
 *
 * ```
 * <footer>            border-top: 1px solid rgba(255,255,255,.14); padding-block: var(--space-6)
 *   <div class=in>    flex, space-between, gap var(--space-6), wrap
 *     <div class=id>  워드마크 h24 + "자료: 금융감독원 DART 전자공시 · © 미주알"
 *     <div class=acts> [의견 보내기 버튼] [AI 질문 링크 — 데스크톱 숨김, R17]
 * ```
 *
 * The operator's instruction was "remove the text and keep it simple and clean",
 * and the round executed it as a deletion of **four sentences** — the positioning
 * line, the provenance sentence, the gate-cost sentence (with its `EstimateMarker`)
 * and the disclaimer — plus the separate mono bottom row. What is left is one
 * hairline, one row, and no numerals at all, which is why the type is Pretendard:
 * "mono는 숫자 전용(R1)이고 남은 줄에는 숫자가 없다" (result.md §2-14).
 *
 * **The five deleted constants still exist** in `./copy.ts`, unrendered. R8's own
 * record asks the operator where the gate-cost and 면책 sentences should go
 * instead (result.md §6-1, open as P8 Operator Question Q5) and makes deleting
 * the strings conditional on that answer; deleting the markup is what the round
 * signs, and this file is that deletion.
 *
 * 의견 보내기 is no longer a `data-vocky-trigger` — it is the entry point for
 * 미주알's own surface (`Feedback.tsx`), which anchors its 380px panel to this
 * button on desktop and becomes a bottom sheet at ≤480.
 *
 * **R17 found that the AI 질문 launcher was sitting on this row** — a constant
 * 68px of overlap at every viewport ≤1120px, crossing to zero only at 1256px.
 * Because `Feedback.tsx` anchors its panel to the 의견 보내기 button, a covered
 * button is a **dead interaction**, not a cosmetic overlap. The round signs two
 * independent fixes and neither replaces the other:
 *
 * 1. a **corner reservation** on `.inner` (`Footer.module.css`), so whatever ends
 *    the row clears the launcher — `.actions` is the end of a `space-between`
 *    row, so hiding one item only hands the covered position to the next one;
 * 2. **hiding the duplicated 「AI 질문」 link on desktop** — R8 §1's "같은 목적지를
 *    바에서 두 번 말하지 않는다", applied to a destination that desktop said
 *    three times (nav, footer, launcher). **≤767px keeps the link**: the launcher
 *    does not render there, so this is that destination's only footer entry.
 *
 * Structure, content and order are unchanged — only spacing and one desktop-only
 * visibility rule. The link keeps its place in the DOM at every width.
 *
 * ## The 운영자 연락처 is an **operator override**, not something R8 signed
 *
 * `P11.F2`, from the operator's own report at P11's acceptance gate: 「the
 * 운영자에게 직접 연락하려면… part is I think good. but it answers like "현재 등록된
 * 운영자 연락처가 없습니다…" where to insert those values? and I want those values
 * to the footer as well. email: leetusik@gmail.com phone: 010-3772-9916」 — both
 * values, in the agent's answer **and** here, confirmed against an email-only
 * alternative they were offered.
 *
 * It is recorded as an override because it pushes against this exact round. R8
 * deleted four sentences from this footer at the operator's earlier instruction
 * (「remove the text and keep it simple and clean」), and the round justified the
 * row's Pretendard by the absence the deletion produced: 「mono는 숫자 전용(R1)이고
 * 남은 줄에는 숫자가 없다」. A phone number is numerals. So this puts text back
 * into a footer the operator asked to be minimal, and digits into a row whose
 * typeface was argued from having none. The later instruction supersedes the
 * round — the same way `intent.md` §2 superseded R16 D11's 「4장」 — and it is
 * written down here rather than smoothed over. Two consequences follow, and
 * neither is R8's:
 *
 * 1. **The phone renders mono and the email stays sans**, so R1's 「숫자는 mono」
 *    and R8's 「남은 줄은 Pretendard」 are both honoured rather than one of them
 *    broken silently (`Footer.module.css`).
 * 2. **The contact joins the existing 자료/© row.** R8's deletion was *of a second
 *    mono row*; re-adding one would undo the shape the operator asked for.
 *
 * The five constants R8 left unrendered in `./copy.ts` are **not** reopened, and
 * P8 Operator Question Q5 is untouched.
 *
 * ## Where the values come from
 *
 * One deploy setting, `MIJUAL_OPERATOR_CONTACT`, which the AI 질문 agent answers
 * with as well — served by `GET /site/contact` and read in the **root layout**,
 * because this component sits inside the client-side `SiteChrome`. The API
 * splits it: the email and the phone arrive as separate fields so this row can
 * type them apart without parsing anything.
 *
 * **Unset, or the API unreachable, renders no contact line at all** — never an
 * empty label, and never 「연락처 미설정」, which is the *agent's* honest-unset
 * voice and not the chrome's.
 */
export function SiteFooter({ contact = null }: { contact?: SiteContact | null }) {
  return (
    <footer className={styles.footer}>
      <div className={`content ${styles.inner}`}>
        <div className={styles.identity}>
          <Wordmark height={24} />
          <p className={styles.source}>
            {SOURCE_KO}
            <span aria-hidden="true" className={styles.dot}>
              ·
            </span>
            {COPYRIGHT_KO}
            {/* The operator's own values, and only the ones that exist. No label
                precedes them: an address and a phone number say what they are,
                and a Korean label here would be copy nobody signed. */}
            {contact?.email ? (
              <>
                <span aria-hidden="true" className={styles.dot}>
                  ·
                </span>
                <a href={`mailto:${contact.email}`} className={styles.contact}>
                  {contact.email}
                </a>
              </>
            ) : null}
            {contact?.phone ? (
              <>
                <span aria-hidden="true" className={styles.dot}>
                  ·
                </span>
                {/* `tel:` keeps the operator's own hyphens — RFC 3966 visual
                    separators, which every dialer strips — so what a reader taps
                    is what a reader reads. */}
                <a
                  href={`tel:${contact.phone.replace(/\s+/g, "")}`}
                  className={`${styles.contact} ${styles.phone}`}
                >
                  {contact.phone}
                </a>
              </>
            ) : null}
          </p>
        </div>

        <div className={styles.actions}>
          <FeedbackEntry className={styles.action} />
          <Link href={ROUTES.ask} className={`${styles.action} ${styles.actionAsk}`}>
            {ASK_LABEL_KO}
          </Link>
        </div>
      </div>
    </footer>
  );
}
