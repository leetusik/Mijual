import Link from "next/link";
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
 * One event's detail page (R3), composed in the round's own order.
 *
 * > 1. Crumb "← 관제 현황판" · 2. Header panel · 3. 환산 블록 (① only) ·
 * > 4. Field sections · 5. 정정 strip · 6. Provenance line.
 *
 * The type-specific content sits at position 3: ①'s 환산 블록 (and its 청약 결과
 * inset and 기재 불일치 block), ②'s API fact strip **above** the 본문 fields, and
 * ③'s 2단계 절차 — which is not a block of its own but the rendering of the one
 * served field that carries both windows, so it arrives inside the field
 * sections where its citation belongs.
 *
 * A **withdrawn** event renders the locked notice instead of the body, with the
 * 정정사항 evidence under it and nothing else: no fields, no countdown, no old
 * dates. The crumb and the provenance line stay, because they are the page's
 * frame rather than the card's body — the provenance line is exactly what the
 * one citation on that page is an instance of.
 *
 * ## AI 질문 (`P6.S6`)
 *
 * Two additions R6 puts on this page and P5 deliberately left out (`P5.S13` note
 * 8), both entry points and neither a surface of its own:
 *
 * - the **질문 스트립** under the header — 프리셋 칩 generated from this event's
 *   gate-passing fields, which open the widget (모바일: the page) in this event's
 *   범위 with the question sent. 「스트립 자체는 답변을 렌더하지 않음」, and it
 *   holds no state;
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
export function EventDetail({ detail }: { detail: Detail }) {
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

      <EventHeader detail={detail} />

      {scope ? <QuestionStrip scope={scope} presets={presets} /> : null}

      {withdrawn ? (
        <Withdrawn detail={detail} />
      ) : (
        <>
          {detail.rights_type === "R1" ? <Offering detail={detail} /> : null}
          {detail.rights_type === "R2" && detail.convertible ? (
            <ConvertibleStrip view={detail.convertible} />
          ) : null}

          <FieldSections fields={detail.fields} reference={detail.countdown.reference} />

          {/* Sparse ② (본문 fields = 0): the fact strip and one factual line.
              No empty sections, no placeholders, no apology (R3). */}
          {detail.rights_type === "R2" && fieldCount === 0 ? (
            <p className={styles.sparse}>{SPARSE_CLOSING_KO}</p>
          ) : null}

          <Corrections detail={detail} />
        </>
      )}

      <p className={styles.provenance}>{PROVENANCE_KO}</p>
    </main>
  );
}
