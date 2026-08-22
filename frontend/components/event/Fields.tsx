import { Citation, StateBadge } from "@/components";
import { won } from "@/lib/format";
import type { FieldPayload } from "@/lib/types";
import {
  APPRAISAL_EXERCISE_KO,
  DISSENT_NOTICE_KO,
  FORMULA_FINAL_KO,
  FORMULA_FIRST_KO,
  FORMULA_SECOND_KO,
  NOTICE_METHOD_KO,
  NOTICE_RECIPIENT_KO,
  OPTION_KIND_KO,
  PAST_STEP_KO,
  SECTION_SCHEDULE_KO,
  SECTION_TERMS_KO,
  STEP_DEPENDENCY_KO,
  STEP_ONE_KO,
  STEP_TWO_KO,
  optionWindowCaptionKo,
} from "./copy";
// The reading order and the story field moved to plain data in `P6.S6`, so the
// 질문 스트립 generates its preset chips in the same order this section renders.
import { STORY_FIELD, fieldRank } from "./fieldOrder";
import styles from "./Event.module.css";

/**
 * The 본문 field sections (R3 §Page anatomy 4).
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
 *    dash or an explanation.
 * 2. **A 추후결정 field carries no value at all** — the contract refuses to build
 *    one (`mijual.present` raises on a value beside 추후결정), so the badge is
 *    the whole row and no date can leak next to it.
 * 3. **Labels come off the wire.** Every row's label is the served
 *    `korean_name`; this file holds no field-name table, only the section
 *    grouping and the order.
 */

/** 일정 holds the fields that state *when*; 발행 조건 holds the filing's terms. */
const SCHEDULE_FIELDS = new Set([
  "warrant_trading_period",
  "subscription_agents",
  "dissent_notice_procedure",
]);

export function FieldSections({
  fields,
  reference,
}: {
  fields: Record<string, FieldPayload>;
  /** The served KST day every "is this behind us" comparison is made against. */
  reference: string;
}) {
  const rows = Object.values(fields)
    .filter((field) => field.field_key !== STORY_FIELD)
    .sort((a, b) => fieldRank(a.field_key) - fieldRank(b.field_key));

  const schedule = rows.filter((field) => SCHEDULE_FIELDS.has(field.field_key));
  const terms = rows.filter((field) => !SCHEDULE_FIELDS.has(field.field_key));

  if (rows.length === 0) return null;

  return (
    <>
      <FieldSection name={SECTION_SCHEDULE_KO} rows={schedule} reference={reference} />
      <FieldSection name={SECTION_TERMS_KO} rows={terms} reference={reference} />
    </>
  );
}

function FieldSection({
  name,
  rows,
  reference,
}: {
  name: string;
  rows: FieldPayload[];
  reference: string;
}) {
  if (rows.length === 0) return null;
  return (
    <section className={styles.section}>
      <p className={styles.eyebrow}>// {name}</p>
      {rows.map((field) => (
        <FieldRow key={field.field_key} field={field} reference={reference} />
      ))}
    </section>
  );
}

/**
 * One field row: 220px label column · value · the field's own `[근거]`.
 *
 * The citation is **chip + quote panel in one element**, and a quote runs from
 * one line to 600 characters — so the citation gets a full-width area of its own
 * on both layouts and the *chip* is placed inside it: right-aligned on the label
 * row at ≤480px (R3 §Mobile), and under the value on desktop, where the label
 * holds its own 220px column. A panel confined to a chip-sized column would wrap
 * Korean prose one character per line, which is what the layout is arranged to
 * avoid.
 */
function FieldRow({ field, reference }: { field: FieldPayload; reference: string }) {
  return (
    <div className={styles.row}>
      <p className={styles.rowLabel}>{field.korean_name}</p>
      <Citation
        className={styles.rowCite}
        rceptNo={field.rcept_no}
        quote={field.quote}
        span={field.span}
        label={field.korean_name}
      />
      <div className={styles.rowValue}>
        {field.display === "추후결정" ? (
          <StateBadge kind="tbd" />
        ) : (
          <FieldValue fieldKey={field.field_key} value={field.value} reference={reference} />
        )}
      </div>
    </div>
  );
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
 * columns "verbatim" — which means with this same reading, so a moved value and
 * the value on the card cannot look like two different things.
 */
export function FieldValue({
  fieldKey,
  value,
  reference,
  moved = false,
}: {
  fieldKey: string;
  value: unknown;
  reference?: string;
  /** This value is a 정정 전/정정 후 column rather than the card's own row. Only
   * what the filing *moved* belongs in a diff, so the round's connective
   * sentences — ③'s dependency line — stay on the card and out of both
   * columns, where they would read as a change that never happened. */
  moved?: boolean;
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
        <div className={styles.stack}>
          {text(record.release_date) ? (
            <span className="mono">{text(record.release_date)}</span>
          ) : null}
          <Detail text={text(record.detail)} />
        </div>
      );

    case "dissent_notice_procedure":
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

function Sub({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <p className={styles.sub}>
      <span className={`mono ${styles.subLabel}`}>{label}</span>
      <span>{value}</span>
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
 * Korean string nobody signed.
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
 * never as a plain 기간 and never as a bar.
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
              <p className={styles.caption}>{optionWindowCaptionKo(start, end)}</p>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

/**
 * ③'s 2단계 절차 (R3 §Type-specific rules).
 *
 * > **③**: governing = 통지 마감 (the earlier step). 2단계 절차 as numbered
 * > structure: ① 반대의사 통지 (window) ② 매수청구 행사 (window), with the
 * > dependency sentence "1단계에서 반대의사를 통지한 주주만 행사 가능". Past
 * > steps: chip "기한 지남", faint.
 *
 * The whole structure is one served field's value, which is why it renders here
 * rather than as a block of its own: `dissent_notice_procedure` carries both
 * windows, the 통지 방법, the 접수처 and the filer's own sentence, and it carries
 * one citation for all of them.
 *
 * "Past" is a comparison of two served ISO days — the step's own end date against
 * `countdown.reference`, the KST day the server computed this page against. No
 * `Date`, no browser clock and no derived D-day: those are the server's
 * (D-10), and a step chip must not disagree with the countdown above it.
 */
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
      <div className={styles.steps}>
        <Step
          ordinal={STEP_ONE_KO}
          label={DISSENT_NOTICE_KO}
          start={text(value.notice_start_date)}
          end={text(value.notice_end_date)}
          reference={reference}
        />
        <Step
          ordinal={STEP_TWO_KO}
          label={APPRAISAL_EXERCISE_KO}
          start={text(value.exercise_start_date)}
          end={text(value.exercise_end_date)}
          reference={reference}
        />
      </div>
      {moved ? null : <p className={styles.dependency}>{STEP_DEPENDENCY_KO}</p>}
      <Sub label={NOTICE_METHOD_KO} value={text(value.method)} />
      <Sub label={NOTICE_RECIPIENT_KO} value={text(value.recipient)} />
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
}: {
  ordinal: string;
  label: string;
  start?: string;
  end?: string;
  reference?: string;
}) {
  if (!start && !end) return null;
  const past = Boolean(reference && end && end < reference);
  return (
    <div className={past ? `${styles.step} ${styles.stepPast}` : styles.step}>
      <p className={styles.stepHead}>
        <span className={`mono ${styles.stepOrdinal}`}>{ordinal}</span>
        <span className={styles.stepLabel}>{label}</span>
        {past ? <span className={styles.pastChip}>{PAST_STEP_KO}</span> : null}
      </p>
      <p className={`mono ${styles.stepWindow}`}>
        <Period start={start} end={end} />
      </p>
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
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => asRecord(item) !== null) : [];
}

function text(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}
