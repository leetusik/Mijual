"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import { useAuthState } from "./useAuthState";
import { CONVERT_BODY_KO, CONVERT_CTA_KO, CONVERT_SESSION_KO, DISMISS_KO } from "./copy";
import styles from "./Auth.module.css";

/**
 * 전환 제안 ① — the offer **band** under 조회's results (R5-2, re-cut by R12 §4).
 *
 * > ① 조회 결과 아래(값 계산 직후, 별도 패널, 닫기 가능, 세션당 1회) …
 * > nav 로그인은 R2 서명대로 조용히 유지 — 강조 없음. 어떤 지점에서도 익명 경로
 * > 비차단.
 * >
 * > 조회 결과 아래 offer 패널: 세션스토리지 플래그로 세션당 1회, 닫기 가능,
 * > 결과를 가리지 않음.
 *
 * ## The four conditions, and why each is a condition
 *
 * **값 계산 직후** — `ready` is the caller's answer to "has a per-holding value
 * rendered on this page", computed with the product's one multiplication site
 * (`lib/holding.ts`). Before a holding exists the panel's first line ("이 보유량은
 * 탭을 닫으면 사라집니다") would be about nothing.
 *
 * **세션당 1회** — one `sessionStorage` flag, written the moment the panel first
 * becomes eligible, so a second stock in the same session does not ask again. The
 * flag is this tab's, like R4's holdings; nothing is sent anywhere and there is
 * no anonymous write endpoint to send it to (`P5.S8` note 13).
 *
 * **닫기 가능** — dismissing hides it for the rest of the page, and the flag has
 * already made it a once-per-session offer either way.
 *
 * **Anonymous only** — the offer's own body is "계정에 저장하면 …", and showing
 * that to a reader who has an account would be the product asserting a state its
 * reader is not in (R5's own hard rule: 가짜 사용자 정체성 금지). The session is
 * probed **only** when the panel would otherwise render, so a 조회 page with no
 * holding typed into it makes no request at all. R5-2 writes no logged-in variant
 * of *this* panel — the logged-in swap it does sign is the detail one-liner —
 * which is recorded as this slice's reading for `P5.S19`.
 *
 * ## R12: the surface is the rank (finding 11)
 *
 * The offer used to be a `CraftPanel` — brackets, glow, the same treatment as the
 * panels holding the numbers it is talking about. It is an **inset band** now:
 * `--surface-inset` + a soft hairline, no brackets, one tier *below* the data. An
 * offer that looks bigger than the figure it answers is not an offer, it is a
 * gate. Three things render — the session line with 닫기, one body line, one 44px
 * CTA — and R5-2's closing reassurance 「지금처럼 로그인 없이 계속 쓸 수 있습니다」
 * is **deleted** (operator instruction, R12 session): what keeps the offer an
 * offer is what it does, not a sentence saying so.
 *
 * Its **place** moved with it (R12 §4): it renders after the last data section
 * and **before** 집계 범위 and the provenance line, which `StockView` decides.
 * Between the data sections it would break their rhythm and push 놓친 돈 under an
 * offer; at the very end of the page it would take the provenance's own place and
 * read as a footer banner.
 *
 * ## R13: one surface where the lead line would be false (Q-E)
 *
 * 보유 종목's **anonymous 샘플 mode** renders this same band after 지나간 마감 —
 * the round decided the sample surface should carry the product's one conversion
 * offer, under R12's own ladder rules (inset, one tier below the data, never
 * above the numbers, dismissible, once per session). It renders it **without the
 * lead line**: 「이 보유량은 탭을 닫으면 사라집니다」 is true of 조회's
 * `sessionStorage` holding and *false* of a sample, whose edits persist in
 * `localStorage` (R5-4, and Q-D accepted that permanence). So `lead` is a prop
 * rather than a second component: with it, `/stocks` renders exactly what R12
 * signed; without it, the body takes the head row beside 닫기 and the band is
 * body + CTA + 닫기. **No new copy either way.**
 *
 * ## What it never does
 *
 * It never covers the results: it is a block in normal flow, with nothing
 * `position: fixed` and no overlay ("게이트 화면·강제 모달 금지"). It gates nothing
 * — every anonymous surface behaves identically whether the band is there,
 * dismissed or never shown — and the nav's 로그인 slot stays exactly as R8 signed
 * it, unhighlighted (`AccountSlot.tsx` is untouched).
 */
export function ConversionOffer({
  ready,
  lead = true,
}: {
  ready: boolean;
  /** R13 Q-E — `false` on 보유 종목's 샘플 surface, where R12's session line is
   * not true. Defaults to R12's signed band. */
  lead?: boolean;
}) {
  const [eligible, setEligible] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const auth = useAuthState(ready && !dismissed);

  useEffect(() => {
    if (!ready || eligible || dismissed) return;
    if (auth === null || auth.authenticated) return;
    if (markSeen()) setEligible(true);
  }, [ready, eligible, dismissed, auth]);

  if (!eligible || !ready || dismissed) return null;

  const dismiss = (
    <button className={styles.dismiss} type="button" onClick={() => setDismissed(true)}>
      {DISMISS_KO}
    </button>
  );

  return (
    <div className={styles.offer}>
      {lead ? (
        <>
          <div className={styles.offerHead}>
            <p className={styles.offerLead}>{CONVERT_SESSION_KO}</p>
            {dismiss}
          </div>

          <p className={styles.offerBody}>{CONVERT_BODY_KO}</p>
        </>
      ) : (
        // Without the lead, the body stands in the head row beside 닫기 — the
        // band keeps its three-part shape rather than growing a blank first row.
        <div className={styles.offerHead}>
          <p className={styles.offerBody}>{CONVERT_BODY_KO}</p>
          {dismiss}
        </div>
      )}

      {/* Every login lands on 보유 종목; the origin is not carried and the copy
          names no destination (R12 Q-B). */}
      <Link className={styles.offerCta} href={ROUTES.login}>
        {CONVERT_CTA_KO}
      </Link>
    </div>
  );
}

/** The 세션당 1회 flag. Returns `true` when this call is the one that claims the
 * session's single showing. A browser with storage denied shows the offer once
 * per page rather than never — the panel is an offer, not a fact, so failing open
 * costs nothing. */
const SEEN_KEY = "mijual.convert.offer";

function markSeen(): boolean {
  try {
    if (window.sessionStorage.getItem(SEEN_KEY) !== null) return false;
    window.sessionStorage.setItem(SEEN_KEY, "1");
    return true;
  } catch {
    return true;
  }
}
