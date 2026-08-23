import type { ReactNode } from "react";
import Link from "next/link";
import { CraftPanel, DDay, EstimateMarker, RightsChip, StateBadge } from "@/components";
import { count, won } from "@/lib/format";
import { eventPath } from "@/lib/routes";
import type { ConvertibleView, FieldPayload, RightsRow, StockPage } from "@/lib/types";
import { ConversionChain } from "./Conversion";
import {
  APPRAISAL_EXERCISE_KO,
  CONVERSION_OPEN_KO,
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  CONVERTIBLE_SOURCE_KO,
  DETAIL_LINK_KO,
  DISSENT_NOTICE_KO,
  FIELD_ABSENT_KO,
  FILED_SUFFIX_KO,
  MISSING_VALUE,
  NO_SCHEDULE_KO,
  OVERHANG_KO,
  PAST_STEP_KO,
  RCEPT_NO_KO,
  RIGHTS_SECTION_KO,
  SHARES_UNIT_KO,
  STEP_DEPENDENCY_KO,
  STEP_ONE_KO,
  STEP_TWO_KO,
  TRADING_OPEN_KO,
  subscriptionClosedParts,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * 진행 중인 권리 — N건 (R4 §4, **re-cut by R11 §4**).
 *
 * **The order is the server's** (`_live_rank`, `P5.S4` note 4): upcoming D-day
 * ascending → ② 진행 중 most-recently-opened first → 일정 추후결정, unranked and
 * last. A deadline you can still act on outranks an open window with nothing to
 * exercise (R4-4), and past ①/③ are absent — a past ① reappears below with its
 * 소멸 계산, the only honest place for it.
 *
 * Nothing here computes a date: `dday`, `days`, `date`, `window` and `reference`
 * are all served, computed upstream in KST (D-10).
 *
 * ## What R11 changed
 *
 * **A panel is a deadline, not a company.** On a single-stock page the corp name
 * is the `h1`, once; 풍전약품 used to title three identical panels. The panel head
 * is now chip + 접수번호·공시일 meta on the left, and the **governing label** as
 * the `h3` on the right, above the D-day and the window line.
 *
 * **② is one table per type, not one panel per filing** (findings 6–7). ② is
 * context with nothing to exercise (R4-4), and context belongs in a form that can
 * be compared: three filings side by side make their 전환가액·오버행·개시일
 * differences readable, and 600px of stacked panels becomes ≈190px. ① and ③ keep
 * their panels because they carry a deadline a reader can act on.
 *
 * **③ is drawn here for the first time** — R10 §4's 2단계 절차 block, including
 * its no-schedule form.
 *
 * **One way to the event**: 「상세 보기 →」, in the ① panel's foot and at the end of
 * a ② row. 접수번호 is an identifier and is never a link.
 */
export function RightsSection({
  page,
  shares,
  prompt,
  fallback,
}: {
  page: StockPage;
  shares: number | null;
  /** R11 §6's control, when this section is the one that carries it (a live ①
   * exists on the page). `StockView` decides; only the first ① block shows it. */
  prompt?: ReactNode;
  /** What stands in this section on a stock with **no** rights and **no** lapse:
   * R4's `NoRights` panel, which speaks for both sections at once (R11 §Empty,
   * `lookup/Empty.html` — the heading is still 「진행 중인 권리 — 0건」). */
  fallback?: ReactNode;
}) {
  const rows = page.rights.rows;
  const title = `${RIGHTS_SECTION_KO} — ${count(page.rights.count)}건`;
  const convertibles = rows.filter((row) => row.rights_type === "R2");
  const closedEnds = page.lapse.rows
    .map((row) => row.lapse.subscription_end)
    .filter((end): end is string => Boolean(end));

  // ② collapses into one table, placed where its **first** row ranked, so the
  // server's urgency order still decides what a reader meets first.
  let tableDrawn = false;
  let promptDrawn = false;
  const blocks: ReactNode[] = [];
  for (const row of rows) {
    if (row.rights_type === "R2") {
      if (!tableDrawn) {
        tableDrawn = true;
        blocks.push(<ConvertibleTable key="convertibles" rows={convertibles} />);
      }
      continue;
    }
    const carriesPrompt = Boolean(prompt) && !promptDrawn && row.rights_type === "R1" && row.offering;
    if (carriesPrompt) promptDrawn = true;
    blocks.push(
      <RightsPanel
        key={row.event_id}
        row={row}
        shares={shares}
        prompt={carriesPrompt ? prompt : undefined}
      />,
    );
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow} aria-label={title}>
        {title}
      </h2>

      {rows.length === 0 ? (
        // 0건 is a fact, not an absence to apologise for. Where the stock's
        // offering has simply closed, the section states that — and the line is a
        // bridge: the money it leads to is in 놓친 돈, further down this page. A
        // stock with nothing at all gets `fallback` instead, because there is no
        // closed offering to name.
        closedEnds.length > 0 ? (
          <CraftPanel>
            {closedEnds.map((end) => (
              <p key={end} className={styles.closed}>
                {subscriptionClosedParts.before}
                <span className={styles.v}>{end}</span>
                {subscriptionClosedParts.after}
              </p>
            ))}
          </CraftPanel>
        ) : (
          fallback ?? null
        )
      ) : (
        <ul className={styles.panels}>{blocks}</ul>
      )}
    </section>
  );
}

/** ① and ③: a craft panel headed by its deadline, closed by 「상세 보기 →」. */
function RightsPanel({
  row,
  shares,
  prompt,
}: {
  row: RightsRow;
  shares: number | null;
  prompt?: ReactNode;
}) {
  return (
    <CraftPanel as="li">
      <RightsHead row={row} />

      {row.rights_type === "R1" && row.offering ? (
        <ConversionChain
          factors={row.offering}
          shares={shares}
          finalPriceDate={row.offering.final_price_date}
          confirmedPrice={row.offering.confirmed_price}
          prompt={shares === null ? prompt : undefined}
        />
      ) : null}

      {row.rights_type === "R3" ? <Procedure row={row} /> : null}

      {row.rcept_no ? (
        <p className={styles.rowfoot}>
          <Link className={styles.golink} href={eventPath(row.rcept_no)}>
            {DETAIL_LINK_KO}
          </Link>
        </p>
      ) : null}
    </CraftPanel>
  );
}

/**
 * The panel head (R11 §4).
 *
 * Left: the type chip and the mono meta that says **which filing** this is —
 * 접수번호 and the served `original_rcept_dt`. The detail header's 「정정 반영」
 * belongs to `corrections.versions`, which this route does not serve, so it is
 * simply absent here rather than guessed at.
 *
 * Right: the governing label as an `h3`, the D-day (or the 추후결정 badge when the
 * schedule is undecided — `dday: null`, R11 §4 and §10 box 3), and the window
 * line. The window's dates are **never dropped**; the state word tells a reader
 * how to read them, and it differs per rights type (`ui-traps.md` #5): an open ①
 * is 「거래 가능」, an open ② is 「진행 중」, a closed ①/③ wears ③'s own 「기한 지남」
 * chip, and **「종료」 exists nowhere in this product**.
 */
function RightsHead({ row }: { row: RightsRow }) {
  const countdown = row.countdown;
  const [start, end] = countdown.window;
  const state = countdown.window_state;
  const hasDDay = countdown.dday !== null && countdown.days !== null;
  const phrase =
    state === "open" && row.rights_type === "R1"
      ? TRADING_OPEN_KO
      : state === "open" && row.rights_type === "R2"
        ? CONVERSION_OPEN_KO
        : null;
  // ②'s window is not the kind that closes, so it never wears the chip.
  const past = state === "closed" && row.rights_type !== "R2";

  return (
    <div className={styles.rhead}>
      <div className={styles.rid}>
        <span className={styles.rchip}>
          <RightsChip rightsType={row.rights_type} />
        </span>
        {row.rcept_no || row.original_rcept_dt ? (
          <p className={styles.rmeta}>
            {row.rcept_no ? (
              <span>
                {RCEPT_NO_KO} {row.rcept_no}
              </span>
            ) : null}
            {row.original_rcept_dt ? (
              <span>
                {row.original_rcept_dt} {FILED_SUFFIX_KO}
              </span>
            ) : null}
          </p>
        ) : null}
      </div>

      <div className={styles.rwhen}>
        <h3 className={styles.whenlab}>{countdown.label_ko}</h3>

        {hasDDay ? (
          <DDay
            dday={countdown.dday as string}
            days={countdown.days as number}
            date={countdown.date}
          />
        ) : (
          // 추후결정 means *no date* — never a dash, never the date it replaced.
          <StateBadge kind="tbd" />
        )}

        {start && end ? (
          <p className={styles.win}>
            <span className={styles.dates}>
              {start} ~ {end}
            </span>
            {phrase ? <span className={styles.live}>{phrase}</span> : null}
            {past ? <span className={styles.past}>{PAST_STEP_KO}</span> : null}
          </p>
        ) : null}

        {/* The badge says the state; this says what follows from it. Never a date
            beside either (`ui-traps.md` #4). */}
        {hasDDay ? null : <p className={styles.win}>{NO_SCHEDULE_KO}</p>}
      </div>
    </div>
  );
}

/**
 * ③'s 2단계 절차 (R11 §4, R10 §4's block).
 *
 * Both windows come from **one served field**, `dissent_notice_procedure`. Where
 * this route does not carry it, each step states the absence in the round's
 * dashed chip 「현재 버전 공시에 없음」 — the frame R10 gives an absent field, and
 * not a placeholder: no fabricated date, and no reason why (D-14). Nothing is
 * computed here; "past" is a comparison of two **served** ISO days, the step's own
 * end against `countdown.reference`, the KST day the server computed against.
 *
 * 매수예정가 is R3's detail-page field and is deliberately not on this surface.
 */
function Procedure({ row }: { row: RightsRow }) {
  const record = procedureRecord(row.fields?.dissent_notice_procedure);
  const reference = row.countdown.reference;
  const steps = [
    {
      ordinal: STEP_ONE_KO,
      title: DISSENT_NOTICE_KO,
      start: isoDay(record?.notice_start_date),
      end: isoDay(record?.notice_end_date),
    },
    {
      ordinal: STEP_TWO_KO,
      title: APPRAISAL_EXERCISE_KO,
      start: isoDay(record?.exercise_start_date),
      end: isoDay(record?.exercise_end_date),
    },
  ];

  return (
    <>
      <div className={styles.steps}>
        {steps.map((step) => {
          const past = Boolean(step.end && step.end < reference);
          return (
            <div
              key={step.ordinal}
              className={past ? `${styles.step} ${styles.pastStep}` : styles.step}
            >
              <div className={styles.snum}>
                <span>{step.ordinal}</span>
              </div>
              <div className={styles.sbody}>
                <div className={styles.sHead}>
                  <h4 className={styles.stitle}>{step.title}</h4>
                  {past ? <span className={styles.past}>{PAST_STEP_KO}</span> : null}
                </div>
                {step.start && step.end ? (
                  <p className={styles.swin}>
                    {step.start} ~ {step.end}
                  </p>
                ) : (
                  <p className={styles.absent}>{FIELD_ABSENT_KO}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <p className={styles.sdep}>{STEP_DEPENDENCY_KO}</p>
    </>
  );
}

/**
 * ② — **one table for the type, one row per filing** (R11 §4, findings 6–7).
 *
 * The chip is drawn once, for the type; the columns are the three facts R4-4
 * names (전환가액 · 전환 시 주식수 · 오버행) plus the filing that carries them and
 * the 개시일 it counts down to. Every one of those is a **fact** from the
 * `cvbdIsDecsn` API row, so none carries `[근거]`: an API row has no character
 * offsets, and one source line under the table answers for all of them (R10 §3's
 * density rule). A value the row does not carry renders 「⋯」 — never a 0, never a
 * dash sentence and never a reason.
 *
 * A past opening reads 「진행 중」, in `--live`, and **never 종료** (`ui-traps.md`
 * #5): ②'s window *opens*, so there is nothing about it that has ended.
 */
function ConvertibleTable({ rows }: { rows: RightsRow[] }) {
  if (rows.length === 0) return null;
  // The 개시 column's own name is served on every row — `countdown.label_ko`,
  // 「전환청구 개시」 — so the header is the payload's word, not a second one.
  const openingLabel = rows[0].countdown.label_ko;

  return (
    <CraftPanel as="li">
      <div className={styles.ctab}>
        <div className={styles.ctop}>
          <RightsChip rightsType="R2" />
        </div>

        <div className={`${styles.ctrow} ${styles.cthead}`}>
          <span>{FILED_SUFFIX_KO}</span>
          <span>{CONVERSION_PRICE_KO}</span>
          <span>{CONVERTED_SHARES_KO}</span>
          <span>{OVERHANG_KO}</span>
          <span>{openingLabel}</span>
          <span />
        </div>

        {rows.map((row) => (
          <ConvertibleRow key={row.event_id} row={row} />
        ))}

        <p className={styles.ctsrc}>
          <span>{CONVERTIBLE_SOURCE_KO}</span>
          <span>{count(rows.length)}건</span>
        </p>
      </div>
    </CraftPanel>
  );
}

function ConvertibleRow({ row }: { row: RightsRow }) {
  const view: ConvertibleView | undefined = row.convertible;
  const countdown = row.countdown;
  const open = countdown.window_state === "open";
  const hasDDay = countdown.dday !== null && countdown.days !== null;

  return (
    <div className={styles.ctrow}>
      <span className={styles.ctfiled}>
        {row.original_rcept_dt ? (
          <span className={styles.ctdate}>{row.original_rcept_dt}</span>
        ) : null}
        {row.rcept_no ? <span className={styles.ctrcept}>{row.rcept_no}</span> : null}
      </span>

      <Fact label={CONVERSION_PRICE_KO} view={view?.conversion_price} render={won} />
      <Fact
        label={CONVERTED_SHARES_KO}
        view={view?.shares}
        render={(value) => `${count(value)}${SHARES_UNIT_KO}`}
      />
      <Fact label={OVERHANG_KO} view={view?.overhang_pct} render={(value) => `${value}%`} />

      <span className={styles.ctwhen}>
        {countdown.date ? <span className={styles.dates}>{countdown.date}</span> : null}
        {open ? (
          <span className={styles.live}>{CONVERSION_OPEN_KO}</span>
        ) : hasDDay ? (
          <DDay
            dday={countdown.dday as string}
            days={countdown.days as number}
            showDate={false}
          />
        ) : null}
      </span>

      {row.rcept_no ? (
        <Link className={styles.golink} href={eventPath(row.rcept_no)}>
          {DETAIL_LINK_KO}
        </Link>
      ) : (
        <span />
      )}
    </div>
  );
}

/** One ② cell. `data-l` is the ≤767px card's own label, drawn by CSS so the
 * desktop table does not print the column name twice on one row. */
function Fact({
  label,
  view,
  render,
}: {
  label: string;
  view?: { value: string | number; estimated: boolean };
  render: (value: string | number) => string;
}) {
  if (!view) {
    return (
      <span className={styles.ctmiss} data-l={label}>
        {MISSING_VALUE}
      </span>
    );
  }
  return (
    <span className={styles.ctval} data-l={label}>
      <EstimateMarker estimated={view.estimated}>{render(view.value)}</EstimateMarker>
    </span>
  );
}

function procedureRecord(field?: FieldPayload): Record<string, unknown> | null {
  const value = field?.value;
  if (value === null || typeof value !== "object" || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

/** A served calendar day, or nothing. An unknown shape is an absent window, and
 * an absent window is stated — never filled in. */
function isoDay(value: unknown): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

/**
 * ②'s dilution context as **내 포트폴리오** renders it (R4 §②/③, decision R4-4).
 *
 * R11 replaced this shape on 내 종목 조회 with the table above; 보유 종목 is R5's
 * surface and no round has re-cut it, so its rows keep the three fact lines they
 * were signed with. The component stays exported for that one caller
 * (`components/portfolio/Deadlines.tsx`) and is unchanged.
 */
export function Dilution({ view }: { view: ConvertibleView }) {
  const cells: Array<{ label: string; value: string; estimated: boolean }> = [];

  if (view.overhang_pct) {
    cells.push({
      label: OVERHANG_KO,
      value: `${view.overhang_pct.value}%`,
      estimated: view.overhang_pct.estimated,
    });
  }
  if (view.shares) {
    cells.push({
      label: CONVERTED_SHARES_KO,
      value: `${count(view.shares.value)}${SHARES_UNIT_KO}`,
      estimated: view.shares.estimated,
    });
  }
  if (view.conversion_price) {
    cells.push({
      label: CONVERSION_PRICE_KO,
      value: won(view.conversion_price.value),
      estimated: view.conversion_price.estimated,
    });
  }

  if (cells.length === 0) return null;

  return (
    <div className={styles.dilution}>
      {cells.map((cell) => (
        <p key={cell.label} className={styles.factor}>
          <span className={styles.factorLabel}>{cell.label}</span>
          <EstimateMarker estimated={cell.estimated}>
            <span className="mono">{cell.value}</span>
          </EstimateMarker>
        </p>
      ))}
    </div>
  );
}
