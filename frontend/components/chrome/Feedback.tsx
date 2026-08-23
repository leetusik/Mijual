"use client";

import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, FEEDBACK_NO_RETRY_CODES, sendFeedback } from "@/lib/api";
import { askStore } from "@/lib/ask";
import { lockBodyScroll } from "@/lib/scrollLock";
import {
  CLOSE_GLYPH,
  FEEDBACK_CLOSE_KO,
  FEEDBACK_EMPTY_HINT_KO,
  FEEDBACK_FAILED_KO,
  FEEDBACK_FINE_KO,
  FEEDBACK_GUIDE_KO,
  FEEDBACK_KEPT_KO,
  FEEDBACK_PLACEHOLDER_KO,
  FEEDBACK_RECEIPT_FINE_KO,
  FEEDBACK_RECEIPT_LABEL_KO,
  FEEDBACK_RETRY_KO,
  FEEDBACK_SEND_KO,
  FEEDBACK_SENDING_KO,
  FEEDBACK_SENT_KO,
  FEEDBACK_TITLE_KO,
  VOCKY_ROW_KO,
} from "./copy";
import styles from "./Feedback.module.css";

/**
 * 의견 보내기 — the surface **미주알 owns** (R8 build-prompt §6, `Feedback.html` /
 * `FeedbackStates.html`).
 *
 * > vocky는 임베드 위젯을 제공하지 않으므로 화면은 우리 것이다. 브라우저는
 * > **미주알 자체 API**에만 말하고 키는 서버 `.env`에만 있다.
 *
 * That replaces R2's whole vocky contract: there is no third-party script, no
 * `data-vocky-trigger` seam and no widget this app does not draw. The entry
 * points are the footer button, the mobile sheet row and — since R9's session
 * instruction (build-prompt §12, `chrome/AccountSlot.html`) — the desktop
 * account menu's 의견 보내기 row: 「R8이 만든 미주알 소유 의견 표면을 여는 세 번째
 * 진입점이며 … 새 표면도 새 카피도 없다」. **Never a floating corner button**,
 * because the bottom-right corner is the AI 질문 launcher's (R2 §6-4, restated
 * by R8: "우하단 모서리는 비운다").
 *
 * ## The two forms are one component
 *
 * > desktop: 진입점 기준 앵커 패널 … `bottom: calc(100% + 10px); width:380px`.
 * > ≤480: 전폭 하단 시트 … 백드롭 `rgba(10,19,16,.72)`.
 *
 * The desktop panel hangs off its entry point, so it is `position: absolute`
 * inside the entry's own wrapper; the mobile sheet is `position: fixed` and the
 * 480px media query switches between them. `variant="sheet"` is the nav's entry,
 * which exists only below that breakpoint and therefore only ever takes the
 * fixed form — and it renders *outside* the menu sheet, because opening the
 * feedback closes the menu ("열 때 메뉴 시트는 닫는다") and a dialog inside a
 * `display: none` container would close with it.
 *
 * ## The state machine is the record's, exactly
 *
 * idle (empty) → 보내기 disabled + the hint, **and no error colour**; typing (the
 * trimmed message decides); sending → the textarea locks and dims, the button
 * says 보내는 중입니다 and 닫기 disappears, **and there is no spinner** (R1 has no
 * rotation); sent → the body is replaced by 접수됨 + the 접수 번호 vocky returned;
 * failed → a notice, the message preserved in an inset, 입력한 내용은 그대로 남아
 * 있습니다 and 다시 시도 — **never `--alert`**, because red means 소멸/기한 in this
 * product and a failed POST is not a loss of money.
 */

/** R8: "`503`/네트워크/**타임아웃(8초)** → failed + 다시 시도". The server's own
 * forward gives up sooner (6 s), so this ceiling is the client's backstop for a
 * request that never comes back at all. */
const TIMEOUT_MS = 8000;

/** R1's mobile side of 480/768/1120 — the same boundary `Nav.module.css` uses
 * for the sheet. Server-rendered as `false` and corrected on mount, the shape
 * `lib/motion.ts` and `components/ask/useAsk.ts` both use: a media query is a
 * client fact. It decides only the **body scroll lock**, which belongs to the
 * bottom sheet and would be wrong under the anchored desktop panel; the geometry
 * itself is CSS. */
const MOBILE_QUERY = "(max-width: 480px)";

function useMobile(): boolean {
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(MOBILE_QUERY);
    const sync = () => setMobile(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);
  return mobile;
}

type Phase = "editing" | "sending" | "sent" | "failed";

export type FeedbackDialogProps = {
  /** vocky's own field: which entry point opened this (footer / mobile sheet /
   * the account menu, which is the desktop web chrome and therefore `web`). */
  channel: "web" | "mobile";
  /** `anchored` = the footer's 380px panel (a bottom sheet below 480px);
   * `sheet` = the nav's, which is the bottom sheet at every width it exists at. */
  variant: "anchored" | "sheet";
  /** Which side of its entry point the anchored panel hangs off. R8 drew one
   * entry point — the footer, at the bottom of the page — so the panel goes
   * **above** it, and that stays the default: the footer and the nav are
   * untouched by this prop existing. The account menu (R9 build-prompt §12) is
   * the third entry point and sits in the 52px top bar, where "above" is
   * off-screen, so it asks for `below`. Ignored by `variant="sheet"` and below
   * 480px, where the panel is the viewport's own bottom sheet. */
  placement?: "above" | "below";
  onClose: () => void;
  /** Where focus goes when the dialog closes — its entry point. */
  returnFocusTo?: React.RefObject<HTMLElement | null>;
};

export function FeedbackDialog({
  channel,
  variant,
  placement = "above",
  onClose,
  returnFocusTo,
}: FeedbackDialogProps) {
  const pathname = usePathname();
  const mobile = useMobile();
  const [message, setMessage] = useState("");
  const [phase, setPhase] = useState<Phase>("editing");
  const [receipt, setReceipt] = useState<string | null>(null);
  const [retryable, setRetryable] = useState(true);
  const field = useRef<HTMLTextAreaElement>(null);
  const inflight = useRef<AbortController | null>(null);

  const trimmed = message.trim();
  const sending = phase === "sending";

  // 열릴 때 textarea로 이동, 닫힐 때 진입점으로 복귀 — the return half runs on
  // unmount, so every close path (×, 닫기, Esc, backdrop, route change) gets it.
  useEffect(() => {
    field.current?.focus();
    const entry = returnFocusTo;
    return () => {
      inflight.current?.abort();
      entry?.current?.focus();
    };
  }, [returnFocusTo]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  // 경로 변경 닫힘. The first render's pathname is the one it opened on, so the
  // effect only fires when it actually changes.
  const opened = useRef(pathname);
  useEffect(() => {
    if (pathname !== opened.current) onClose();
  }, [pathname, onClose]);

  // The bottom sheet covers the page, so the page must not scroll underneath it
  // (the same counted lock the menu sheet takes — they overlap while the menu
  // fades out). The anchored desktop panel takes none.
  useEffect(() => {
    if (!mobile) return;
    return lockBodyScroll();
  }, [mobile]);

  const send = useCallback(
    (text: string) => {
      const controller = new AbortController();
      inflight.current = controller;
      const timer = window.setTimeout(() => controller.abort(), TIMEOUT_MS);
      setPhase("sending");
      // The AI 질문 tab handle if this browser already has one — never a new
      // identifier, and nothing at all for a reader who has not asked anything.
      const session = askStore.getSnapshot().sessionHash ?? undefined;

      void sendFeedback(text, channel, { session, signal: controller.signal })
        .then((answer) => {
          setReceipt(answer.request_id);
          setPhase("sent");
        })
        .catch((error: unknown) => {
          setRetryable(
            !(error instanceof ApiError && FEEDBACK_NO_RETRY_CODES.includes(error.code)),
          );
          setPhase("failed");
        })
        .finally(() => {
          window.clearTimeout(timer);
          if (inflight.current === controller) inflight.current = null;
        });
    },
    [channel],
  );

  const surface = [
    styles.surface,
    variant === "sheet" ? styles.asSheet : styles.asPanel,
    variant !== "sheet" && placement === "below" ? styles.asPanelBelow : null,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <>
      {/* ≤480 only (and always, for the nav's variant): 백드롭 rgba(10,19,16,.72),
          tap = close. It is a sibling of the surface rather than its parent, so a
          click on the panel never has to be stopped from bubbling. */}
      <div
        className={[styles.backdrop, variant === "sheet" ? styles.backdropShown : null]
          .filter(Boolean)
          .join(" ")}
        onClick={onClose}
        aria-hidden="true"
      />

      <div className={surface} role="dialog" aria-label={FEEDBACK_TITLE_KO}>
        <div className={styles.header}>
          <span className={styles.title}>{FEEDBACK_TITLE_KO}</span>
          <button
            type="button"
            className={styles.close}
            aria-label={FEEDBACK_CLOSE_KO}
            onClick={onClose}
          >
            {CLOSE_GLYPH}
          </button>
        </div>

        {phase === "sent" ? (
          <div className={styles.body}>
            <p className={styles.notice}>{FEEDBACK_SENT_KO}</p>
            {/* 접수 번호 <mono request_id> inset 박스 — vocky's own handle, the one
                number this surface shows, so it is mono like every other numeral. */}
            <p className={styles.inset}>
              <span className={styles.insetLabel}>{FEEDBACK_RECEIPT_LABEL_KO}</span>
              <span className={`mono ${styles.receipt}`}>{receipt}</span>
            </p>
            <p className={styles.fine}>{FEEDBACK_RECEIPT_FINE_KO}</p>
            <div className={styles.actions}>
              <button type="button" className={styles.quiet} onClick={onClose}>
                {FEEDBACK_CLOSE_KO}
              </button>
            </div>
          </div>
        ) : phase === "failed" ? (
          <div className={styles.body}>
            <p className={styles.notice}>{FEEDBACK_FAILED_KO}</p>
            <p className={`${styles.inset} ${styles.kept}`}>{trimmed}</p>
            <p className={styles.fine}>{FEEDBACK_KEPT_KO}</p>
            <div className={styles.actions}>
              <button type="button" className={styles.quiet} onClick={onClose}>
                {FEEDBACK_CLOSE_KO}
              </button>
              {/* 401 = 키 문제는 독자가 해결 못 한다 — the failure stands, without
                  a retry that cannot work. */}
              {retryable ? (
                <button type="button" className={styles.send} onClick={() => send(trimmed)}>
                  {FEEDBACK_RETRY_KO}
                </button>
              ) : null}
            </div>
          </div>
        ) : (
          <form
            className={styles.body}
            onSubmit={(event) => {
              event.preventDefault();
              if (trimmed && !sending) send(trimmed);
            }}
          >
            <p className={styles.guide}>{FEEDBACK_GUIDE_KO}</p>
            <textarea
              ref={field}
              className={`${styles.field} ${sending ? styles.fieldSending : ""}`}
              value={message}
              readOnly={sending}
              maxLength={4000}
              placeholder={FEEDBACK_PLACEHOLDER_KO}
              onChange={(event) => setMessage(event.target.value)}
            />
            <p className={styles.fine}>{FEEDBACK_FINE_KO}</p>
            <div className={styles.actions}>
              {/* 빈 입력에서만 — 「오류 색 없음」, so it is fine print explaining a
                  disabled button, never a validation message. */}
              {trimmed === "" ? <span className={styles.hint}>{FEEDBACK_EMPTY_HINT_KO}</span> : null}
              {/* 전송 중 닫기 숨김 */}
              {sending ? null : (
                <button type="button" className={styles.quiet} onClick={onClose}>
                  {FEEDBACK_CLOSE_KO}
                </button>
              )}
              <button type="submit" className={styles.send} disabled={trimmed === "" || sending}>
                {sending ? FEEDBACK_SENDING_KO : FEEDBACK_SEND_KO}
              </button>
            </div>
          </form>
        )}
      </div>
    </>
  );
}

/**
 * The footer's entry point and the panel it anchors — one control, so the footer
 * only has to place it.
 *
 * The nav's mobile row is **not** this component: it opens the same dialog but
 * has to close the menu sheet first and render the dialog outside it (see the
 * note above), so `Nav.tsx` owns that pair itself.
 */
export function FeedbackEntry({ className }: { className?: string }) {
  const [open, setOpen] = useState(false);
  const entry = useRef<HTMLButtonElement>(null);

  return (
    <span className={styles.anchor}>
      <button
        type="button"
        ref={entry}
        className={className}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {VOCKY_ROW_KO}
      </button>
      {open ? (
        <FeedbackDialog
          channel="web"
          variant="anchored"
          onClose={() => setOpen(false)}
          returnFocusTo={entry}
        />
      ) : null}
    </span>
  );
}
