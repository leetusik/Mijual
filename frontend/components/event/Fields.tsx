import type { ReactNode } from "react";
import { Citation, StateBadge } from "@/components";
import { dartUrl } from "@/lib/api";
import { won } from "@/lib/format";
import type { FieldPayload } from "@/lib/types";
import {
  APPRAISAL_EXERCISE_KO,
  DISSENT_NOTICE_KO,
  FIELD_ABSENT_KO,
  FORMULA_FINAL_KO,
  FORMULA_FIRST_KO,
  FORMULA_SECOND_KO,
  NOTICE_METHOD_KO,
  NOTICE_RECIPIENT_KO,
  NOTICE_WINDOW_KO,
  OPTION_KIND_KO,
  PAST_STEP_KO,
  SECTION_PROCEDURE_KO,
  SECTION_SCHEDULE_KO,
  SECTION_TERMS_KO,
  STEP_DEPENDENCY_KO,
  STEP_ONE_KO,
  STEP_TWO_KO,
  dartSourceLabelKo,
  optionWindowCaptionKo,
} from "./copy";
// The reading order, the story field and R10's citation-density rule are plain
// data (`P6.S6` moved the first two here), so the page and the 질문 스트립 read
// one payload the same way.
import { STORY_FIELD, fieldCites, fieldRank } from "./fieldOrder";
import styles from "./Event.module.css";

/**
 * The 본문 field sections (R3 §Page anatomy 4, re-cut by **R10 §4–§5**).
 *
 * > **Field sections** — section eyebrow `// {name}` (mono, tracked); rows =
 * > 220px label column (Korean `korean_name`) + value + `Citation` per field
 * > (`quote` verbatim, `rcept_no`). Only fields with `exposable: true` exist in
 * > the DOM; `display: "추후결정"` renders `StateBadge tbd`. Blocked fields:
 * > **no row, no marker.**
 *
 * Three rules the payload already enforces, restated because they are what this
 * component must not undo:
 *
 * 1. **A gate-blocked field is absent from `fields` entirely**, so "render every
 *    served field" *is* "render around the hole as if the row had never
 *    existed" (`states-and-trust.md` §4). Nothing here may add a placeholder, a
 *    dash or an explanation — a rule R10 explicitly keeps (§6 손대지 않은 것).
 * 2. **A 추후결정 field carries no value at all** — the contract refuses to build
 *    one (`mijual.present` raises on a value beside 추후결정), so the badge is
 *    the whole row and no date can leak next to it.
 * 3. **Labels come off the wire.** Every row's label is the served
 *    `korean_name`; this file holds no field-name table, only the section
 *    grouping, the order, and R10's density rule.
 *
 * ## What R10 changed here
 *
 * **The eyebrows are real headings.** `h2` with the `//` drawn by CSS, so a
 * screen-reader outline reads 회사명 → 2단계 절차 → 일정 → 발행 조건 → 정정공시
 * 반영 and the accessible name is 「일정」, not 「// 일정」 (walk finding 12).
 *
 * **A `[근거]` is no longer on every row** (operator direction, §5). A chip goes
 * where the on-screen value differs from the filing's words; a row that carries
 * the filer's sentence 1:1 gets none, because the quote panel would only re-print
 * what the reader is looking at. **Every section closes with one mono `DART 원문
 * {rcept} ↗` line** instead — mandatory where a section has no chips at all, and
 * rendered on every section as the round's cards draw it. Provenance does not
 * shrink: every value is still one tap from the 원문, which is what the locked
 * provenance sentence promises.
 *
 * **③'s 2단계 절차 is its own block**, ahead of the sections, with number pills
 * and `h3` step titles (§4). It used to be the nested value of one 220px row —
 * a numbered procedure inside a table cell — and the two rows the same field
 * carries (통지 방법 · 접수처) are now rows of their own under 발행 조건, exactly
 * as `detail/Procedure.html` draws them.
 */

/** 일정 holds the fields that state *when*; 발행 조건 holds the filing's terms.
 * `dissent_notice_procedure` is in neither: R10 gives it its own block. */
const SCHEDULE_FIELDS = new Set(["warrant_trading_period", "subscription_agents"]);

const PROCEDURE_FIELD = "dissent_notice_procedure";

export function FieldSections({
  fields,
  reference,
  rceptNo,
  rightsType,
}: {
  fields: Record<string, FieldPayload>;
  /** The served KST day every "is this behind us" comparison is made against. */
  reference: string;
  /** The page's filing number — the section source lines' target (R10 §5). */
  rceptNo?: string | null;
  /** Which rights type the page is — only ③ has a procedure whose absence is a
   * stated fact rather than a missing section. */
  rightsType?: string | null;
}) {
  const rows = Object.values(fields)
    .filter((field) => field.field_key !== STORY_FIELD)
    .sort((a, b) => fieldRank(a.field_key) - fieldRank(b.field_key));

  const procedure = rows.find((field) => field.field_key === PROCEDURE_FIELD);
  const schedule = rows.filter((field) => SCHEDULE_FIELDS.has(field.field_key));
  const terms = rows.filter(
    (field) => !SCHEDULE_FIELDS.has(field.field_key) && field.field_key !== PROCEDURE_FIELD,
  );

  // ③'s procedure is the field the countdown is read from, so on a ③ page its
  // absence is not "one less section" — it is the same fact the countdown slot
  // is already stating, and R10 draws it in the same dashed frame **in a field
  // row** so the two read as one state rather than as two empty places (§10 box
  // 6, `detail/Procedure.html`'s 아시아나 case).
  const absentProcedure = rightsType === "R3" && !procedure;

  if (rows.length === 0 && !absentProcedure) return null;

  return (
    <>
      {absentProcedure ? (
        <section className={styles.sec}>
          <Row label={NOTICE_WINDOW_KO}>
            <span className={styles.absent}>{FIELD_ABSENT_KO}</span>
          </Row>
        </section>
      ) : null}

      {procedure ? <Procedure field={procedure} reference={reference} /> : null}

      <FieldSection name={SECTION_SCHEDULE_KO} rows={schedule} rceptNo={rceptNo} />
      <FieldSection
        name={SECTION_TERMS_KO}
        rows={terms}
        rceptNo={rceptNo}
        extra={procedure ? <ProcedureRows field={procedure} /> : null}
      />
    </>
  );
}

function FieldSection({
  name,
  rows,
  rceptNo,
  extra,
}: {
  name: string;
  rows: FieldPayload[];
  rceptNo?: string | null;
  /** Rows this section holds that are not fields of their own — ③'s 통지 방법
   * and 접수처, which the procedure field carries alongside its two windows. */
  extra?: ReactNode;
}) {
  if (rows.length === 0 && !extra) return null;
  return (
    <section className={styles.sec}>
      {/* The `//` is drawn by `::before` (R10 §5) — and Chrome puts generated
          content into the accessible name, so an unnamed eyebrow reads as
          「// 발행 조건」 to a screen reader. §10 box 7 requires the name without
          it, so the heading names itself with its own words. */}
      <h2 className={styles.eyebrow} aria-label={name}>
        {name}
      </h2>
      {rows.map((field) => (
        <FieldRow key={field.field_key} field={field} />
      ))}
      {extra}
      <SectionSource rceptNo={rceptNo} />
    </section>
  );
}

/**
 * The section-level source line (R10 §5) — the quiet alternative to a `[근거]`
 * on every row, and the reason the density rule costs no provenance: a section
 * whose rows print the filing's own words closes with one mono link into that
 * filing, and the reader is one tap from the 원문 either way.
 */
function SectionSource({ rceptNo }: { rceptNo?: string | null }) {
  if (!rceptNo) return null;
  return (
    <p className={styles.secsrc}>
      <a href={dartUrl(rceptNo)} target="_blank" rel="noreferrer">
        {dartSourceLabelKo(rceptNo)}
      </a>
    </p>
  );
}

/**
 * One field row: 220px label column · value · the field's `[근거]` where R10's
 * density rule puts one.
 *
 * The chip sits **inside the value**, immediately after it, because R10's quote
 * is an overlay popover: it opens over the page instead of pushing the rows
 * below it down, so the citation no longer needs a full-width area of its own.
 */
function FieldRow({ field }: { field: FieldPayload }) {
  const sub = twoPartSub(field.field_key, field.value);
  return (
    <div className={styles.row}>
      <p className={styles.rowLabel}>{field.korean_name}</p>
      <div className={styles.rowValue}>
        {field.display === "추후결정" ? (
          <StateBadge kind="tbd" />
        ) : (
          <FieldValue fieldKey={field.field_key} value={field.value} split />
        )}
        {fieldCites(field.field_key, Boolean(field.quote)) ? (
          <Citation
            rceptNo={field.rcept_no}
            quote={field.quote}
            span={field.span}
            label={field.korean_name}
          />
        ) : null}
        {sub ? <p className={styles.sub}>{sub}</p> : null}
      </div>
    </div>
  );
}

/** A plain row this surface composes rather than reads — ③'s 통지 방법 and
 * 접수처, whose labels are R3's own constants and whose values are served. */
function Row({ label, children }: { label: string; children: ReactNode }) {
  if (!children) return null;
  return (
    <div className={styles.row}>
      <p className={styles.rowLabel}>{label}</p>
      <div className={styles.rowValue}>{children}</div>
    </div>
  );
}

/**
 * R10 §3's two-part value: the value line, then the filing's own sentence under
 * it — never joined into one run-on by an em dash (walk finding 8). The reason
 * line renders **after** the citation, so the chip stays on the value it cites.
 */
function twoPartSub(fieldKey: string, value: unknown): string | undefined {
  if (fieldKey !== "lockup_release") return undefined;
  const record = asRecord(value);
  return record ? text(record.detail) : undefined;
}

/**
 * One field's value, in the filer's own words wherever the filing has any.
 *
 * R3 states the rule for ② and it generalises: "render each option's `detail`
 * string as the value" — the `detail` a filing carries *is* the value, because it
 * states the convention the structured keys cannot (`ui-traps.md` #1). So every
 * shape below renders served strings and served dates, and nothing else: no
 * derived date, no re-punctuated quote, no label this file made up.
 *
 * Exported because the CorrectionStory renders `field_moves`' 정정 전/정정 후
 * sides "verbatim" — which means with this same reading, so a moved value and
 * the value on the card cannot look like two different things.
 */
export function FieldValue({
  fieldKey,
  value,
  reference,
  moved = false,
  split = false,
}: {
  fieldKey: string;
  value: unknown;
  reference?: string;
  /** This value is a 정정 전/정정 후 side rather than the card's own row. Only
   * what the filing *moved* belongs in a diff, so the round's connective
   * sentences — ③'s dependency line — stay on the card and out of both
   * sides, where they would read as a change that never happened. */
  moved?: boolean;
  /** The caller renders this value's reason line itself (R10's two-part value),
   * so the citation can sit between the two. */
  split?: boolean;
}) {
  const record = asRecord(value);
  if (record === null) return null;

  switch (fieldKey) {
    case "warrant_trading_period":
      return <Period start={text(record.start_date)} end={text(record.end_date)} />;

    case "subscription_agents":
      return <SubscriptionAgents entries={asList(record.entries)} />;

    case "issue_price_formula":
      return (
        <div className={styles.stack}>
          <Sub label={FORMULA_FIRST_KO} value={text(record.first_price_method)} />
          <Sub label={FORMULA_SECOND_KO} value={text(record.second_price_method)} />
          <Sub label={FORMULA_FINAL_KO} value={text(record.final_price_method)} />
        </div>
      );

    case "option_schedule":
      return <OptionSchedule options={asList(record.options)} />;

    case "lockup_release":
      return (
        <>
          {text(record.release_date) ? (
            <span className="mono">{text(record.release_date)}</span>
          ) : null}
          {split ? null : <Detail text={text(record.detail)} />}
        </>
      );

    case "dissent_notice_procedure":
      // R10 gives this field its own block on the card; a **diff side** still
      // renders it inline, because what the correction moved is the whole value.
      return <DissentProcedure value={record} reference={reference} moved={moved} />;

    case "appraisal_price":
      return typeof record.price === "number" ? (
        <span className="mono">{won(record.price)}</span>
      ) : null;

    default:
      // A field this surface has no drawn form for still has the filer's own
      // sentence. Nothing is invented for a shape nobody designed.
      return <Detail text={text(record.detail)} />;
  }
}

/** 신주인수권증서 상장·매매기간 and every other genuine window: two served days.
 * (`option_schedule`'s pair is **not** one of these — see `OptionSchedule`.) */
function Period({ start, end }: { start?: string; end?: string }) {
  if (!start && !end) return null;
  if (start && end && start !== end) {
    return (
      <span className="mono">
        {start} ~ {end}
      </span>
    );
  }
  return <span className="mono">{start ?? end}</span>;
}

function Detail({ text }: { text?: string }) {
  return text ? <p className={styles.detail}>{text}</p> : null;
}

/** A labelled line inside a value — the Korean label in the quietest ink, never
 * in mono (R1: Korean prose is never mono; the mono labels below are 1차/2차/확정,
 * which are the served `korean_name`'s own parenthetical). */
function SubLine({ label, children }: { label: string; children?: ReactNode }) {
  if (!children) return null;
  return (
    <p className={styles.sub}>
      <span className={styles.subLabel}>{label}</span> {children}
    </p>
  );
}

function Sub({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <p className={styles.sub}>
      <span className={`mono ${styles.subLabel}`}>{label}</span> {value}
    </p>
  );
}

/**
 * 청약 취급처 — R3: "renders as a target/agent/date table (구주주 rows bolded)".
 *
 * The 구주주 row is the one a shareholder acts on (the grounding pack says so of
 * this very field: "the 구주주 window … is the one a shareholder cares about"),
 * which is why the round singles it out. There are no column headers: the three
 * cells are the filing's own 대상자 / 증권사 / 청약일, and a header would be a
 * Korean string nobody signed. R10 frames the table in a hairline and collapses
 * it to one column at ≤767px — a long value reads as a list, not a squeezed
 * table.
 */
function SubscriptionAgents({ entries }: { entries: Record<string, unknown>[] }) {
  if (entries.length === 0) return null;
  return (
    <div className={styles.agents}>
      {entries.map((entry, index) => {
        const target = text(entry.target);
        const own = target?.includes("구주주") ?? false;
        return (
          <div key={`${index}-${target ?? ""}`} className={styles.agentRow}>
            <span className={own ? styles.agentTargetOwn : styles.agentTarget}>{target}</span>
            <span className={styles.agentName}>{text(entry.agent)}</span>
            <span className={`mono ${styles.agentWhen}`}>
              <Period start={text(entry.start_date)} end={text(entry.end_date)} />
            </span>
          </div>
        );
      })}
    </div>
  );
}

/**
 * 콜·풋 세부 스케줄 — the date-convention trap, rendered the one safe way.
 *
 * `ui-traps.md` #1: `start_date`/`end_date` bracket a **recurring** claim right,
 * and the stored value carries no basis marker, so the pair alone cannot say
 * which convention a filing used. The value is therefore the filer's own
 * `detail` string, and the two dates appear **only** inside R3's caption —
 * never as a plain 기간 and never as a bar. R10 keeps the cards as R3 drew them
 * and makes only the bracket unbreakable, which is why the caption is composed
 * from its three parts rather than from one template string.
 */
function OptionSchedule({ options }: { options: Record<string, unknown>[] }) {
  if (options.length === 0) return null;
  return (
    <div className={styles.stack}>
      {options.map((option, index) => {
        const kind = text(option.kind);
        const start = text(option.start_date);
        const end = text(option.end_date);
        return (
          <div key={`${index}-${kind ?? ""}`} className={styles.option}>
            <p className={styles.optionHead}>
              {kind && OPTION_KIND_KO[kind] ? (
                <span className={styles.optionKind}>{OPTION_KIND_KO[kind]}</span>
              ) : null}
              {text(option.holder) ? (
                <span className={styles.optionHolder}>{text(option.holder)}</span>
              ) : null}
            </p>
            <Detail text={text(option.detail)} />
            {start && end ? (
              <p className={styles.caption}>
                {optionWindowCaptionKo.before}
                <span className="mono">{optionWindowCaptionKo.range(start, end)}</span>
                {optionWindowCaptionKo.after}
              </p>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

/**
 * ③'s 2단계 절차 as its own block (R3 §Type-specific rules, **R10 §4**).
 *
 * > **③**: governing = 통지 마감 (the earlier step). 2단계 절차 as numbered
 * > structure: ① 반대의사 통지 (window) ② 매수청구 행사 (window), with the
 * > dependency sentence "1단계에서 반대의사를 통지한 주주만 행사 가능". Past
 * > steps: chip "기한 지남", faint.
 *
 * The whole structure is one served field's value — `dissent_notice_procedure`
 * carries both windows, the 통지 방법, the 접수처 and the filer's own sentence,
 * and one citation for all of them. R3 rendered it inside a single field row;
 * R10 gives the two steps a framed block with number pills and `h3` titles, and
 * puts 통지 방법 / 접수처 in the 발행 조건 section as rows of their own.
 *
 * "Past" is a comparison of two served ISO days — the step's own end date against
 * `countdown.reference`, the KST day the server computed this page against. No
 * `Date`, no browser clock and no derived D-day: those are the server's (D-10),
 * and a step chip must not disagree with the countdown above it.
 */
function Procedure({ field, reference }: { field: FieldPayload; reference: string }) {
  const record = asRecord(field.value);
  if (record === null) return null;
  return (
    <div className={styles.steps}>
      <h2 className={styles.eyebrow} aria-label={SECTION_PROCEDURE_KO}>
        {SECTION_PROCEDURE_KO}
      </h2>
      <Step
        ordinal={STEP_ONE_KO}
        label={DISSENT_NOTICE_KO}
        start={text(record.notice_start_date)}
        end={text(record.notice_end_date)}
        reference={reference}
      >
        {/* The filer's own sentence about the notice — verbatim, and the only
            place it renders. */}
        {text(record.detail)}
      </Step>
      <Step
        ordinal={STEP_TWO_KO}
        label={APPRAISAL_EXERCISE_KO}
        start={text(record.exercise_start_date)}
        end={text(record.exercise_end_date)}
        reference={reference}
      >
        {STEP_DEPENDENCY_KO}
      </Step>
    </div>
  );
}

/** The two rows ③'s procedure field carries besides its windows. Their labels
 * are R3's own constants and their values are served strings; R10 §5 lists them
 * among the rows that print the filing 1:1, so neither carries a chip and the
 * section's source line answers for both. */
function ProcedureRows({ field }: { field: FieldPayload }) {
  const record = asRecord(field.value);
  if (record === null) return null;
  return (
    <>
      <Row label={NOTICE_METHOD_KO}>{text(record.method)}</Row>
      <Row label={NOTICE_RECIPIENT_KO}>{text(record.recipient)}</Row>
    </>
  );
}

/** ③'s procedure inside a **diff side** — the whole value, inline, because what
 * a correction moved is the field, not the card's arrangement of it. */
function DissentProcedure({
  value,
  reference,
  moved,
}: {
  value: Record<string, unknown>;
  reference?: string;
  moved?: boolean;
}) {
  return (
    <div className={styles.stack}>
      <SubLine label={DISSENT_NOTICE_KO}>
        <Period start={text(value.notice_start_date)} end={text(value.notice_end_date)} />
      </SubLine>
      <SubLine label={APPRAISAL_EXERCISE_KO}>
        <Period start={text(value.exercise_start_date)} end={text(value.exercise_end_date)} />
      </SubLine>
      {moved ? null : <p className={styles.stepDep}>{STEP_DEPENDENCY_KO}</p>}
      <SubLine label={NOTICE_METHOD_KO}>{text(value.method)}</SubLine>
      <SubLine label={NOTICE_RECIPIENT_KO}>{text(value.recipient)}</SubLine>
      <Detail text={text(value.detail)} />
    </div>
  );
}

function Step({
  ordinal,
  label,
  start,
  end,
  reference,
  children,
}: {
  ordinal: string;
  label: string;
  start?: string;
  end?: string;
  reference?: string;
  children?: ReactNode;
}) {
  if (!start && !end) return null;
  const past = Boolean(reference && end && end < reference);
  return (
    <div className={past ? `${styles.step} ${styles.stepPast}` : styles.step}>
      <div className={styles.stepNum}>
        <span>{ordinal}</span>
      </div>
      <div className={styles.stepBody}>
        <div className={styles.stepHead}>
          <h3 className={styles.stepTitle}>{label}</h3>
          <span className={styles.stepWindow}>
            <Period start={start} end={end} />
          </span>
          {/* Never 종료-coloured: a passed step is faint, and --alert means
              expiring/lost. The word is the same one a closed ① window wears. */}
          {past ? <span className={styles.past}>{PAST_STEP_KO}</span> : null}
        </div>
        {children ? <p className={styles.stepDep}>{children}</p> : null}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Payload readers — the contract's values are records of strings, dates and
// numbers, and every one of them is read defensively: an unknown shape renders
// nothing rather than `[object Object]`.
// ---------------------------------------------------------------------------

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function asList(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => asRecord(item) !== null)
    : [];
}

function text(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}
