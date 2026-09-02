import Link from "next/link";
import { CraftPanel } from "@/components";
import { AskPageScope, QuestionStrip, presetsFor } from "@/components/ask";
import { ROUTES } from "@/lib/routes";
import type { EventDetail as Detail } from "@/lib/types";
import { ConvertibleStrip } from "./Convertible";
import { Corrections } from "./Corrections";
import { FieldSections } from "./Fields";
import { EventHeader } from "./Header";
import { Offering } from "./Offering";
import { Withdrawn } from "./Withdrawn";
import { BOARD_LABEL_KO, PROVENANCE_KO, SPARSE_CLOSING_KO } from "./copy";
import styles from "./Event.module.css";

/**
 * One event's detail page (R3, re-cut by **R10**), composed in the round's own
 * order.
 *
 * > 1. Crumb "← 관제 현황판" · 2. Header · 3. 질문 스트립 · 4. 환산 블록 / ② 팩트
 * > 스트립 / ③ 2단계 절차 · 5. Field sections · 6. 정정 밴드 · 7. Provenance.
 *
 * ## R10: the page is **one craft panel**
 *
 * R3 gave the header a panel and left the body on the page background. Every
 * card R10 landed draws the whole page inside a single `<Panel>`, and its
 * geometry only closes that way: blocks inset themselves 20px from the panel
 * edge, sections are separated by hairlines rather than by page gaps, the 질문
 * 스트립 attaches to the header's bottom with a `border-top`, and the 정정 밴드
 * bleeds to both edges. So the panel moved out here and the header is a
 * `<header>` inside it.
 *
 * The type-specific content sits at position 4: ①'s 환산 블록 (and its 청약 결과
 * inset and 기재 불일치 block), ②'s API fact strip **above** the 본문 fields, and
 * ③'s 2단계 절차 — which R10 gives its own `h2` block, ahead of the field
 * sections, rather than folding it inside one 220px row.
 *
 * A **withdrawn** event renders the locked notice instead of the body, with the
 * 정정사항 evidence under it and nothing else: no fields, no countdown, no old
 * dates. The crumb and the provenance line stay, because they are the page's
 * frame rather than the card's body — the provenance line is exactly what the
 * citations on that page are instances of.
 *
 * ## AI 질문 (`P6.S6`, placement re-cut by R10 §9)
 *
 * Two additions R6 puts on this page and P5 deliberately left out (`P5.S13` note
 * 8), both entry points and neither a surface of its own:
 *
 * - the **질문 스트립**, now attached to the header's bottom edge inside the
 *   panel — 프리셋 칩 generated from this event's gate-passing fields, which open
 *   the widget (모바일: the page) in this event's 범위 with the question sent.
 *   R10 changes **placement and hit height only**; the strip's own design and
 *   copy are surface 7's;
 * - the page's **ambient 범위** — 「이벤트 상세에서 열면 범위 = 그 이벤트」 —
 *   bound by `AskPageScope`, which renders nothing and never overrides a 범위 the
 *   reader chose.
 *
 * Both need `{rcept_no, name}`, because the signed 범위 chip prints 「범위: {종목}
 * · {rcept_no}」; an event payload missing either (both are nullable on the wire)
 * gets neither. A **withdrawn** event keeps the ambient 범위 and offers no
 * presets: the page renders no fields to generate them from, and 철회 is the
 * refusal family the agent would answer with — 「답할 수 없는 질문은 프리셋으로
 * 제안하지 않음」.
 */
export function EventDetail({
  detail,
  initialAuthenticated,
}: {
  detail: Detail;
  /** Whether this **request** carried a session, resolved on the server by the
   * page (`P4.F10`) and passed straight through to `DeadlineOffer`, which is the
   * only thing on this page that reads it. It is a bare boolean on purpose — the
   * reader's `Account` never enters this page's HTML. `undefined` is legal and
   * means "nobody resolved it", which puts the line back on its client probe. */
  initialAuthenticated?: boolean;
}) {
  const withdrawn = detail.state === "withdrawn";
  const fieldCount = Object.keys(detail.fields).filter(
    (key) => key !== "correction_interpretation",
  ).length;
  const scope =
    detail.rcept_no && detail.corp_name
      ? { rcept_no: detail.rcept_no, name: detail.corp_name }
      : null;
  const presets = withdrawn ? [] : presetsFor(detail.fields);

  return (
    <main className={`content ${styles.page}`}>
      {scope ? <AskPageScope scope={scope} /> : null}

      <Link className={`mono ${styles.crumb}`} href={ROUTES.board}>
        ← {BOARD_LABEL_KO}
      </Link>

      <CraftPanel className={styles.card}>
        <EventHeader detail={detail} initialAuthenticated={initialAuthenticated} />

        {scope ? (
          <div className={styles.qstrip}>
            <QuestionStrip scope={scope} presets={presets} />
          </div>
        ) : null}

        {withdrawn ? (
          <Withdrawn detail={detail} />
        ) : (
          <>
            {detail.rights_type === "R1" ? <Offering detail={detail} /> : null}
            {detail.rights_type === "R2" && detail.convertible ? (
              <ConvertibleStrip view={detail.convertible} />
            ) : null}

            <FieldSections
              fields={detail.fields}
              reference={detail.countdown.reference}
              rceptNo={detail.rcept_no}
              rightsType={detail.rights_type}
            />

            {/* Sparse ② (본문 fields = 0): the fact strip and one factual line.
                No empty sections, no placeholders, no apology (R3). */}
            {detail.rights_type === "R2" && fieldCount === 0 ? (
              <p className={styles.sparse}>{SPARSE_CLOSING_KO}</p>
            ) : null}

            <Corrections detail={detail} />
          </>
        )}

        <p className={styles.provenance}>{PROVENANCE_KO}</p>
      </CraftPanel>
    </main>
  );
}
