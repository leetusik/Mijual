/**
 * The AI 질문 conversation — **one store, two views** (R6 §상태 지속).
 *
 * R6 asks for three things that together decide this module's shape:
 *
 * > 대화 + 범위는 sessionStorage — 위젯↔페이지·페이지 이동에 살아남고 탭 닫으면
 * > 화면에서 사라짐. **스트리밍 중 이동/전환에도 끊김 없음.**
 *
 * A conversation that keeps streaming while the reader walks from the widget to
 * `/ask` cannot live inside either surface's component tree: navigating unmounts
 * one of them, and an unmounted owner drops the fetch. So the thread lives
 * **here**, in module scope, and the widget (`P6.S5`) and the dedicated page
 * (`P6.S6`) are two *views* subscribed to it. `components/ask/useAsk.ts` mounts
 * the provider once inside the app's persistent layout and exposes the snapshot
 * through `useSyncExternalStore`; nothing else may construct a second store.
 *
 * This file imports **no React** — the same rule `lib/session.ts` states for the
 * same reason: the store is plain state and a plain fetch, and keeping the hook
 * out of it is what lets `lib/ask.test.ts` run under `node --test`.
 *
 * ## What it owns
 *
 * - the turns (question + the answer's blocks, chips, links and footer),
 * - the 범위 (event ↔ 전체 공시), including whether the reader chose it,
 * - the anonymous `session_hash` the first SSE frame hands back,
 * - the SSE fetch lifecycle — start, and **abort as the only 중지** (there is no
 *   stop endpoint: the reader aborts, the consumer stops pulling, the server's
 *   generator is closed),
 * - hydration from and write-through to **sessionStorage, never localStorage**
 *   (R6-5/6, and note the trap: R5's 포트폴리오 helper follows a different rule).
 *
 * ## What it deliberately does not own
 *
 * No Korean copy (that is `components/ask/copy.ts`, transcribed with
 * provenance), no route (`lib/routes.ts` maps the server's link *kinds*), no
 * quota and no history list — 질문 수 무제한, and a 지난 대화 UI is forbidden
 * (R6 §Hard rules). The server keeps the anonymous log; this keeps the screen.
 */

// The `.ts` extension is what lets `node --test` (which strips types in place)
// resolve this import — `tsconfig.json`'s `allowImportingTsExtensions`, the same
// spelling every `lib/*.test.ts` already uses. `lib/ask.test.ts` covers the
// decoder and the store, so this module has to be loadable outside the bundler.
import { streamAsk, type AskHistoryTurn, type SseFrame } from "./api.ts";

// ---------------------------------------------------------------------------
// the shapes the wire speaks (`mijual.agent.events`, serialized by `frame()`)
// ---------------------------------------------------------------------------

/**
 * 갈 곳 — a destination **kind**, never an href.
 *
 * `mijual.agent.loop._links` serves `{kind, rcept_no?}` on purpose: "Serving a
 * filing number and a destination kind keeps one owner for every route and makes
 * it impossible for the agent to point at a page that does not exist." The
 * mapping to a URL is `components/ask/links.ts` over `lib/routes.ts`.
 */
export type AskLink = { kind: string; rcept_no?: string };

/**
 * One numbered 근거, as the `citation` frame defines it.
 *
 * `api_tier` (= the server's `quote is None`) is the R3 case: DART 공시 API 수치
 * with no 원문 스팬, where the 접수번호 *is* the citation handle. It is **a**
 * citation, not a missing one, and its block says so in the signed words.
 */
export type AskChip = {
  number: number;
  rcept_no: string;
  api_tier: boolean;
  quote?: string;
  span?: number[];
  field_key?: string;
};

/**
 * Every structured block carries R16 §1's two fields — **when the server sends
 * them**, which is the whole of 「추가만 한다」.
 *
 * `block_id` is a turn-stable id, and a second block with the same id is an
 * **in-place replacement, not an append** (P10). A block with no id is today's
 * append, so every pre-R16 frame reduces exactly as it always did. `persistent`
 * is the storage half: `false` says this block is shown to the reader and never
 * written to the thread — the 진행 표시 line and nothing else today.
 */
type BlockIdentity = { block_id?: string; persistent?: boolean };

/**
 * One 라벨/값 row — the schema R16 §2.3 fixes and §2.4 **reuses** for a 계산 블록's
 * inputs (「DataRow와 같은 행 스키마」), so both draw through one component.
 *
 * `citation` is the reader's chip **number**, from the same numbering the prose
 * uses (같은 근거 = 같은 번호, R6-4) — never an href and never a rcept_no. Its
 * absence with `reader_input` is a value the reader supplied: 「입력」 마커, 칩 없음.
 * `value` is a string the **server** stated; the surface never formats a number.
 */
export type AskDataRow = {
  label: string;
  value: string;
  citation?: number;
  reader_input?: boolean;
};

/** What a 계산 블록 computed — 검증된 계산 (the product's own money math) or
 * 식 계산 (whitelisted arithmetic). R16 §2.4: the two are never headed with the
 * same word, because rendering them identically launders one into the other. */
export type AskCalcMode = "verified" | "expr";

/** A calculation's lifecycle **on one `block_id`**: it arrives at call time with
 * its inputs drawn and is replaced in place by its outcome (§4 check 5 — the
 * block must not jump between the two). */
export type AskCalcState = "pending" | "done" | "error";

/** One painted thing inside an answer, in arrival order. */
export type AskBlock =
  | (BlockIdentity & { kind: "tool"; tool: string; row: string; ok: boolean })
  | (BlockIdentity & {
      kind: "text";
      text: string;
      citations: number[];
      /** R16 §2.5 / Q-B — character offsets **within this sentence** of a 공시
       * figure no tool returned, unit inside the span. The surface draws the
       * 「미확인」 marker on exactly those; the sentence stands (strip-don't-drop).
       * Rides the wire only when non-empty, so a turn with nothing to hedge
       * reduces to the same object a pre-R16 one did. */
      unverified?: number[][];
    })
  | (BlockIdentity & { kind: "refusal"; family: string; text: string })
  | (BlockIdentity & {
      /**
       * 진행 표시 — the one **transient** block (R16 §2.1).
       *
       * `text` is the server's own signed sentence (`mijual.agent.copy.STATUS_KO`),
       * rendered verbatim like a 도구 행: `components/ask/copy.ts` holds **no**
       * status strings, because the agent's Korean is composed once, server-side
       * (`P9.S3` decision 3). `phase` is the machine-readable tag beside it.
       */
      kind: "status";
      phase: string;
      text: string;
    })
  | (BlockIdentity & { kind: "data"; rows: AskDataRow[]; title?: string })
  | (BlockIdentity & {
      kind: "calc";
      mode: AskCalcMode;
      /** 검증된 계산's name is the **server's** (the operation that actually ran);
       * only 식 계산 lets the model name it (`P9.S5` decision 5). */
      name: string;
      inputs: AskDataRow[];
      state: AskCalcState;
      expr?: string;
      result?: string;
      /** An `error`'s reason, as data — the signed 「계산할 수 없습니다 — {이유}」
       * sentence is composed by the surface (`copy.ts`'s `calcError`). */
      why?: string;
    });

/** The prose kinds: what `released()` joins, and what kills the status line. */
function isProse(block: AskBlock): block is Extract<AskBlock, { kind: "text" | "refusal" }> {
  return block.kind === "text" || block.kind === "refusal";
}

/** 답변 푸터 — `근거 N건 · {rcept_no} · {생성시각 KST}` + 컨텍스트 링크. */
export type AskFooter = {
  count: number;
  evidence: string[];
  /** An absolute `+09:00` instant from the server. The browser slices it
   * (`lib/format.ts` `kstStamp`) and never re-derives a time. */
  generated_at: string;
  links: AskLink[];
};

/**
 * Where one turn is, and therefore which of R6's four SSE states it renders.
 *
 * `pending` = 답변 준비 중 (the request is out; nothing has been painted yet) ·
 * `streaming` = the prose is growing and the caret is on · `done` = 완료 (the
 * footer fades in) · `aborted` / `error` = 중단/오류, where the partial answer
 * **stands** and the signed inset row + 재시도 appear under it.
 */
export type AskTurnStatus = "pending" | "streaming" | "done" | "aborted" | "error";

/** 범위 — an event, or nothing (= 전체 공시). The name is the 종목 the chip prints. */
export type AskScope = { rcept_no: string; name: string };

/** One exchange: the reader's question and the answer built frame by frame. */
export type AskTurn = {
  id: string;
  question: string;
  /** The 범위 this turn was asked in. A later 범위 change never touches it —
   * 「범위 전환은 새 질문부터 적용 (기존 답변 불변)」. */
  scope: AskScope | null;
  blocks: AskBlock[];
  /** Chip definitions in arrival order; a `text` block names their numbers. */
  chips: AskChip[];
  links: AskLink[];
  footer: AskFooter | null;
  status: AskTurnStatus;
  /** The released prose, for the next turn's `history`. From the terminal where
   * there is one, and from the released blocks where the reader pressed 중지. */
  answer: string;
  /** 공시 M건 읽음 — how many **distinct 접수번호** this turn actually read.
   * `TurnEnd.filings`, a **server-known** value: R16 §1 forbids parsing it back
   * out of the 도구 행 strings, and it is the `events` half of `trace(tools,
   * events)`. 0 until the terminal arrives, and 0 for a turn that read nothing. */
  filings: number;
  /** `TurnEnd.blocked` — **removed markers**, not dropped sentences (R16 §1).
   * Under strip-don't-drop the prose survives and only an unhonoured marker is
   * taken out, so this is a signal about the model's citing. Nothing renders it
   * today; it rides the turn so an operator's view can. */
  blocked: number;
  /** Why an `aborted` / `error` turn stopped — `round_budget` · `tool_budget` ·
   * `call_budget` mean **소진**, which R16 §2.7 draws as dimmed prose and a folded
   * 도구 흐름 and *nothing else*; R14's 「연결이 끊겼습니다」 inset stays for the
   * disconnect state alone. Structural, never key material. */
  reason: string | null;
};

export type AskState = {
  /** Is the widget open? **Not persisted** — see `PERSISTED` below. */
  open: boolean;
  /** Has sessionStorage been read yet? Views render the same either way. */
  hydrated: boolean;
  scope: AskScope | null;
  /** True once the reader set or cleared 범위 themselves; a page's ambient scope
   * then stops overriding it (「×로 전체 공시로 해제」 must stick). */
  scopeChosen: boolean;
  /** The anonymous handle from frame one. Sent back on the next turn; **never a
   * cookie**, never derived from anything about the reader. */
  sessionHash: string | null;
  turns: AskTurn[];
};

/** The store's whole surface. `P6.S6`'s page uses exactly this and adds nothing. */
export type AskStore = {
  subscribe: (listener: () => void) => () => void;
  getSnapshot: () => AskState;
  /** The pre-hydration snapshot, stable by identity so SSR and the first client
   * render agree (`useSyncExternalStore`'s third argument). */
  getServerSnapshot: () => AskState;
  /** Read sessionStorage once, on mount. Safe to call twice. */
  hydrate: () => void;
  open: () => void;
  close: () => void;
  toggle: () => void;
  /** The page's ambient 범위 (an event detail page states its own). Applied when
   * the widget **opens**, per 「이벤트 상세에서 열면 범위 = 그 이벤트」 — never
   * over a 범위 the reader chose. */
  setPageScope: (scope: AskScope | null) => void;
  /** The reader's (or the 질문 스트립's) own choice. */
  setScope: (scope: AskScope | null) => void;
  /** 전체 공시로 해제. **R16 retired the chip and its ×** (§0 폐기 ①), so no
   * surface calls this today — the 범위 state itself stays (「`scope` 상태 자체는
   * 서버·스토어에서 제거하지 않아도 되지만 표면에 그리지 않는다」) and so does the
   * one door that releases it. */
  clearScope: () => void;
  /** Ask, and stream the answer into a new turn. */
  ask: (question: string) => void;
  /** 중지 — abort the fetch. Nothing is retracted; released text stands. */
  stop: () => void;
  /** 재시도 — run the same question again, in place of the turn that broke. */
  retry: (turnId: string) => void;
  /**
   * 「새 대화」 — **empty the thread, and nothing else** (R16 §2.7b).
   *
   * > 스레드를 비우는 동작만 — 이력 목록·제목·복원을 만들지 않는다 (R6 금지 유지).
   *
   * So this clears `turns` (the write-through clears the stored thread with it)
   * and leaves the 범위 and the session handle where they are: the reader is the
   * same anonymous session asking a new question, and minting a second
   * `session_hash` would fork the 대화 로그's own grouping — a storage decision
   * this control was never given. A turn still in flight is aborted first, the
   * same way 중지 does it: without that, frames would keep arriving for a turn
   * that no longer exists (harmless — `patchTurn` no-ops — but the fetch would
   * run on for a conversation the reader has already left).
   */
  newChat: () => void;
};

// ---------------------------------------------------------------------------
// sessionStorage — the whole screen-persistence rule, in two keys
// ---------------------------------------------------------------------------

/**
 * The thread. **`P6.S6` reads this same key and writes nothing of its own.**
 *
 * One key, one JSON object, versioned like `lib/holding.ts`'s: `{v: 1, scope,
 * scopeChosen, sessionHash, turns}`. `open` is **not** in it — the record makes
 * the *conversation* survive a move, not the overlay's open state, and a widget
 * that reopened itself on every reload would be an unsigned behaviour. The
 * launcher restores it in one click with the thread intact.
 *
 * Never `localStorage`: R6-5/6 scopes screen persistence to the tab, and R5's
 * 포트폴리오 helper follows a different rule that must not be copied here.
 */
export const THREAD_KEY = "mijual.ask.thread";

type Persisted = {
  v: 1;
  scope: AskScope | null;
  scopeChosen: boolean;
  sessionHash: string | null;
  turns: AskTurn[];
};

const INITIAL: AskState = {
  open: false,
  hydrated: false,
  scope: null,
  scopeChosen: false,
  sessionHash: null,
  turns: [],
};

/** A turn read back from storage can no longer be running: the fetch died with
 * the page. That is exactly R6's 중단 state — 부분 답변 유지 + the signed inset
 * row — so it is what a restored `pending`/`streaming` turn becomes. */
function settle(status: AskTurnStatus): AskTurnStatus {
  return status === "pending" || status === "streaming" ? "aborted" : status;
}

/**
 * What may be written to the thread: **persistent blocks only** (R16 §1 —
 * 「`StatusEvent`는 저장하지 않는다」).
 *
 * The filter is load-bearing rather than tidy. A write-through happens on every
 * frame, so a tab reloaded mid-turn would otherwise restore a turn `settle()`
 * marks 중단 with a live 「공시를 찾고 있습니다」 under it — a progress line for a
 * turn that stopped progressing before the reader left the page.
 */
function persistedBlocks(blocks: AskBlock[]): AskBlock[] {
  return blocks.filter((block) => block.persistent !== false);
}

/** A stored turn, made current: its fetch died with the page (R6's 중단 state),
 * and a thread written before R16 carries no turn metadata — 0 and `null` are
 * the honest readings of "this was never sent", the same reading a turn that
 * read nothing gets. */
function restore(turn: AskTurn): AskTurn {
  return {
    ...turn,
    status: settle(turn.status),
    blocks: persistedBlocks(turn.blocks ?? []),
    filings: turn.filings ?? 0,
    blocked: turn.blocked ?? 0,
    reason: turn.reason ?? null,
  };
}

function readThread(): Persisted | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(THREAD_KEY);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    const value = parsed as Partial<Persisted>;
    if (value.v !== 1 || !Array.isArray(value.turns)) return null;
    return {
      v: 1,
      scope: value.scope ?? null,
      scopeChosen: value.scopeChosen ?? false,
      sessionHash: typeof value.sessionHash === "string" ? value.sessionHash : null,
      turns: value.turns.map(restore),
    };
  } catch {
    // An unreadable thread is no thread. A conversation is a convenience of this
    // tab; a broken one must never break the page it floats over.
    return null;
  }
}

function writeThread(state: AskState): void {
  if (typeof window === "undefined") return;
  try {
    const payload: Persisted = {
      v: 1,
      scope: state.scope,
      scopeChosen: state.scopeChosen,
      sessionHash: state.sessionHash,
      turns: state.turns.map((turn) => {
        const blocks = persistedBlocks(turn.blocks);
        return blocks.length === turn.blocks.length ? turn : { ...turn, blocks };
      }),
    };
    window.sessionStorage.setItem(THREAD_KEY, JSON.stringify(payload));
  } catch {
    // Storage denied or full: the tab keeps its conversation in memory and loses
    // it on reload. Nothing the reader is told changes, so nothing is thrown.
  }
}

// ---------------------------------------------------------------------------
// the store
// ---------------------------------------------------------------------------

/**
 * A turn id must be unique **across page loads**, not merely within one.
 *
 * This module is re-evaluated on every full load, so a bare counter restarts at
 * 0 — while `hydrate()` installs the sessionStorage thread with the ids it was
 * written with. The first fresh turn after a reload then re-minted `t1`, and the
 * id is not only React's key: `patchTurn` rewrites **every** matching turn,
 * `history(exceptId)` filters by it and `retry` takes the **first** match. A
 * collision streamed one answer into two turns and retried the wrong one.
 *
 * So the id is made collision-free at the source: one random tag per module
 * evaluation (i.e. per page load) plus the counter. The counter keeps ids short
 * and readable in order; the tag is what a restored turn — legacy `t1`, or a
 * previous load's `t<tag>-1` — can never carry.
 */
const SESSION_TAG = sessionTag();

function sessionTag(): string {
  // `crypto.randomUUID` is **secure-context only**, and the operator also browses
  // this product over plain http on the tailnet — so the fallbacks are the live
  // path there, not dead code. Only the entropy source varies; the id shape does
  // not, which keeps both access paths on identical behaviour.
  const source: Crypto | undefined = globalThis.crypto;
  if (typeof source?.randomUUID === "function") return source.randomUUID().slice(0, 8);
  if (typeof source?.getRandomValues === "function") {
    return Array.from(source.getRandomValues(new Uint8Array(4)), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join("");
  }
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

let counter = 0;
function nextId(): string {
  counter += 1;
  return `t${SESSION_TAG}-${counter}`;
}

/**
 * A block's text as it enters the store — **R14 Q-E's normalization**, and the
 * whole of it.
 *
 * The citation gate releases one verified sentence per `text` frame and the
 * sentences arrive with the whitespace the model wrote between them, so the
 * second and later frames carry a leading space or newline. R6 signs 스트리밍 as
 * 「프로즈 자람」 — one paragraph growing — and the live surface instead rendered a
 * line per sentence with a visible indent on each continuation (R14 walk finding
 * 3). The round decided the paragraph, and decided that the fix belongs **here**
 * rather than in CSS: a `<br>`, a `white-space: pre-wrap` or a `display: block`
 * in prose would each be a second answer to the same question, and the store is
 * the one place a block's text is written. The only gap between two sentences is
 * therefore `Ask.module.css`'s `0.25em`.
 *
 * **Leading only.** Trailing whitespace is left alone (a sentence may legitimately
 * end where the next frame continues it), and the reader's own question keeps its
 * `white-space: pre-wrap` — 독자가 친 것은 독자가 친 그대로다.
 */
function leading(text: unknown): string {
  return String(text ?? "").replace(/^\s+/, "");
}

/** The released prose of a turn with no terminal — the same join the server's
 * own `CitationGate.answer` uses, so a 중지 and a `done` produce one shape. */
function released(turn: AskTurn): string {
  return turn.blocks
    .filter(isProse)
    .map((block) => block.text)
    .join(" ");
}

// ---------------------------------------------------------------------------
// the keyed reduce — P10's client half
// ---------------------------------------------------------------------------

/** The block identity the wire carries, **only when it carries one**. The server
 * puts `block_id`/`persistent` on a frame together or not at all. */
function identity(data: Record<string, unknown>): BlockIdentity {
  const id = data.block_id;
  if (typeof id !== "string") return {};
  return { block_id: id, persistent: data.persistent !== false };
}

/**
 * Put a block in the thread: **replace the one wearing its id, or append**.
 *
 * R16 §1: 「같은 `block_id`의 후속 이벤트는 추가가 아니라 제자리 교체」. Replacing
 * *in place* rather than removing and pushing is the whole point — a 계산 블록 that
 * settled `pending → done` must not jump past the 도구 행 that arrived between the
 * two (§4 check 5), and the 진행 표시 line must stay one line rather than five.
 */
function place(blocks: AskBlock[], block: AskBlock): AskBlock[] {
  if (block.block_id === undefined) return [...blocks, block];
  const at = blocks.findIndex((existing) => existing.block_id === block.block_id);
  if (at < 0) return [...blocks, block];
  const next = blocks.slice();
  next[at] = block;
  return next;
}

/**
 * Drop the transient 진행 표시 line.
 *
 * R16 §2.1 says 「첫 `TextEvent`가 오면 제거」, and the terminal is the other half
 * (`P9.S6` note 12): a 보안 refusal turn is `status · refusal · done` and emits no
 * `TextEvent` at all, and a stream cut on the way emits no terminal — either would
 * leave 「질문을 읽고 있습니다」 sitting under a turn that ended. The server cannot
 * unsend a transient block, so the client is the last word on it.
 */
function withoutStatus(blocks: AskBlock[]): AskBlock[] {
  return blocks.some((block) => block.kind === "status")
    ? blocks.filter((block) => block.kind !== "status")
    : blocks;
}

/** The 라벨/값 rows of a `data` block or a 계산's inputs — one reading, because
 * §2.4 gives them one schema. A row the server could not state is not sent, so
 * nothing here invents a value or a format. */
function dataRows(value: unknown): AskDataRow[] {
  if (!Array.isArray(value)) return [];
  return value.map((entry) => {
    const row = (entry ?? {}) as Partial<AskDataRow>;
    return {
      label: String(row.label ?? ""),
      value: String(row.value ?? ""),
      ...(typeof row.citation === "number" ? { citation: row.citation } : {}),
      ...(row.reader_input ? { reader_input: true } : {}),
    };
  });
}

/** A terminal's counter, read as 0 when the frame predates the field. */
function counted(value: unknown): number {
  return typeof value === "number" ? value : 0;
}

/**
 * A closure store rather than a class: every action is already bound, so a view
 * can pass `store.close` straight to `onClick` without a `this` to lose.
 */
export function createAskStore(): AskStore {
  let state: AskState = INITIAL;
  let pageScope: AskScope | null = null;
  let controller: AbortController | null = null;
  let stopping = false;
  const listeners = new Set<() => void>();

  function emit(next: AskState, { persist = true } = {}): void {
    state = next;
    if (persist && next.hydrated) writeThread(next);
    for (const listener of listeners) listener();
  }

  function patch(changes: Partial<AskState>, options?: { persist?: boolean }): void {
    emit({ ...state, ...changes }, options);
  }

  /** Replace one turn in place, leaving every other reference untouched. */
  function patchTurn(id: string, change: (turn: AskTurn) => AskTurn): void {
    let touched = false;
    const turns = state.turns.map((turn) => {
      if (turn.id !== id) return turn;
      touched = true;
      return change(turn);
    });
    if (touched) patch({ turns });
  }

  function history(exceptId: string): AskHistoryTurn[] {
    return state.turns
      .filter((turn) => turn.id !== exceptId && turn.answer !== "")
      .map((turn) => ({ question: turn.question, answer: turn.answer }));
  }

  /** One frame, painted. The transport reorders nothing, so neither does this:
   * a `citation` **defines** a chip immediately before the `text` that names its
   * number, which is what lets the chip be drawn in the same paint as its
   * sentence (R6: 자리표시 칩·후행 부착 금지). */
  function apply(id: string, frame: SseFrame): void {
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(frame.data) as Record<string, unknown>;
    } catch {
      return; // A frame this client cannot read is a frame it does not paint.
    }

    if (frame.event === "session") {
      const handle = data.session_hash;
      if (typeof handle === "string") patch({ sessionHash: handle });
      return;
    }

    patchTurn(id, (turn) => {
      switch (frame.event) {
        case "tool_row":
          return {
            ...turn,
            status: "streaming",
            blocks: place(turn.blocks, {
              kind: "tool",
              tool: String(data.tool ?? ""),
              row: String(data.row ?? ""),
              ok: data.ok !== false,
              ...identity(data),
            }),
          };
        case "citation":
          return { ...turn, chips: [...turn.chips, data as unknown as AskChip] };
        case "status":
          // Once prose has arrived the line is gone **for good**: the loop stops
          // emitting after the first release, and a status line reappearing under
          // a sentence the reader is reading would be a second thing moving on a
          // surface whose whole progress vocabulary is one replaced line.
          return turn.blocks.some(isProse)
            ? turn
            : {
                ...turn,
                blocks: place(turn.blocks, {
                  kind: "status",
                  phase: String(data.phase ?? ""),
                  text: String(data.text ?? ""),
                  ...identity(data),
                }),
              };
        case "data":
          return {
            ...turn,
            status: "streaming",
            blocks: place(turn.blocks, {
              kind: "data",
              rows: dataRows(data.rows),
              ...(typeof data.title === "string" ? { title: data.title } : {}),
              ...identity(data),
            }),
          };
        case "calc":
          return {
            ...turn,
            status: "streaming",
            blocks: place(turn.blocks, {
              kind: "calc",
              mode: data.mode === "expr" ? "expr" : "verified",
              name: String(data.name ?? ""),
              inputs: dataRows(data.inputs),
              state: data.state === "done" || data.state === "error" ? data.state : "pending",
              ...(typeof data.expr === "string" ? { expr: data.expr } : {}),
              ...(typeof data.result === "string" ? { result: data.result } : {}),
              ...(typeof data.why === "string" ? { why: data.why } : {}),
              ...identity(data),
            }),
          };
        case "text":
          return {
            ...turn,
            status: "streaming",
            blocks: place(withoutStatus(turn.blocks), {
              kind: "text",
              text: leading(data.text),
              citations: Array.isArray(data.citations) ? (data.citations as number[]) : [],
              ...(Array.isArray(data.unverified) && data.unverified.length > 0
                ? { unverified: data.unverified as number[][] }
                : {}),
              ...identity(data),
            }),
          };
        case "refusal":
          return {
            ...turn,
            status: "streaming",
            blocks: place(withoutStatus(turn.blocks), {
              kind: "refusal",
              family: String(data.family ?? ""),
              text: leading(data.text),
              ...identity(data),
            }),
          };
        case "links":
          return { ...turn, links: (data.links as AskLink[]) ?? [] };
        case "footer":
          return { ...turn, footer: data as unknown as AskFooter };
        case "done":
        case "aborted":
        case "error":
          return {
            ...turn,
            status: frame.event,
            blocks: withoutStatus(turn.blocks),
            answer: typeof data.answer === "string" ? data.answer : released(turn),
            filings: counted(data.filings),
            blocked: counted(data.blocked),
            reason: typeof data.reason === "string" ? data.reason : null,
          };
        default:
          return turn;
      }
    });
  }

  async function run(id: string, question: string, scope: AskScope | null): Promise<void> {
    controller?.abort();
    const own = new AbortController();
    controller = own;
    stopping = false;

    try {
      const stream = streamAsk(
        {
          question,
          scope_rcept_no: scope?.rcept_no,
          session: state.sessionHash ?? undefined,
          history: history(id),
        },
        { signal: own.signal },
      );
      for await (const frame of stream) apply(id, frame);
      // A stream that ends without its terminal was cut on the way (a proxy, a
      // dropped socket). That is the same 중단 the reader would see from a 중지,
      // and the partial answer above it stands.
      patchTurn(id, (turn) =>
        turn.status === "pending" || turn.status === "streaming"
          ? {
              ...turn,
              status: "aborted",
              blocks: withoutStatus(turn.blocks),
              answer: released(turn),
            }
          : turn,
      );
    } catch {
      const stopped = stopping || own.signal.aborted;
      // 중지 is 중단, not an error — but both render R6's one 중단/오류 state, and
      // a **pre-stream** refusal (429 `rate_limited`, `invalid_question`, a dead
      // service) lands here too, with no blocks: that turn shows the same inset
      // row and 재시도 and no invented sentence, because the design writes state
      // copy and no error copy at all. Nothing about `error` is ever rendered.
      patchTurn(id, (turn) => ({
        ...turn,
        status: stopped ? "aborted" : "error",
        // A turn that ended without its terminal still loses its progress line —
        // 중지 and a dropped socket are exactly where it would otherwise outlive
        // the turn it was narrating.
        blocks: withoutStatus(turn.blocks),
        answer: released(turn),
      }));
    } finally {
      if (controller === own) controller = null;
      stopping = false;
    }
  }

  function start(id: string, question: string, scope: AskScope | null): void {
    void run(id, question, scope);
  }

  // Named functions, not methods: a view passes `store.close` straight to an
  // `onClick`, and a method would arrive with no `this`.
  function subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  function hydrate(): void {
    if (state.hydrated) return;
    const stored = readThread();
    emit(
      {
        ...state,
        hydrated: true,
        scope: stored?.scope ?? state.scope,
        scopeChosen: stored?.scopeChosen ?? state.scopeChosen,
        sessionHash: stored?.sessionHash ?? state.sessionHash,
        turns: stored?.turns ?? state.turns,
      },
      { persist: false },
    );
  }

  function open(): void {
    // 「이벤트 상세에서 열면 범위 = 그 이벤트 … 그 외 = 전체 공시」 — the page's own
    // scope applies at the moment of opening, and never over a 범위 the reader
    // set or cleared themselves.
    patch({ open: true, scope: !state.scopeChosen && pageScope ? pageScope : state.scope });
  }

  function close(): void {
    // Closing is not 중지: a turn in flight keeps streaming into the store, so
    // reopening shows the answer that arrived meanwhile.
    patch({ open: false });
  }

  function ask(question: string): void {
    const text = question.trim();
    if (text === "") return;
    const turn: AskTurn = {
      id: nextId(),
      question: text,
      scope: state.scope,
      blocks: [],
      chips: [],
      links: [],
      footer: null,
      status: "pending",
      answer: "",
      filings: 0,
      blocked: 0,
      reason: null,
    };
    patch({ turns: [...state.turns, turn] });
    start(turn.id, turn.question, turn.scope);
  }

  function retry(turnId: string): void {
    const turn = state.turns.find((candidate) => candidate.id === turnId);
    if (!turn) return;
    // The same question, in the same 범위, in the turn's own place — a retry is
    // this turn again, not a second question in the thread. The partial answer it
    // replaces is cleared by the reader's own action, which is the one thing
    // 「부분 답변 유지 — 지우기 금지」 does not forbid.
    patchTurn(turnId, (previous) => ({
      ...previous,
      blocks: [],
      chips: [],
      links: [],
      footer: null,
      status: "pending",
      answer: "",
      filings: 0,
      blocked: 0,
      reason: null,
    }));
    start(turn.id, turn.question, turn.scope);
  }

  /** 「새 대화」 (R16 §2.7b) — the thread, emptied. See `AskStore.newChat`. */
  function newChat(): void {
    stopping = true;
    controller?.abort();
    patch({ turns: [] });
  }

  return {
    subscribe,
    getSnapshot: () => state,
    getServerSnapshot: () => INITIAL,
    hydrate,
    open,
    close,
    toggle: () => (state.open ? close() : open()),
    setPageScope: (scope) => {
      pageScope = scope;
    },
    setScope: (scope) => patch({ scope, scopeChosen: true }),
    clearScope: () => patch({ scope: null, scopeChosen: true }),
    ask,
    stop: () => {
      stopping = true;
      controller?.abort();
    },
    retry,
    newChat,
  };
}

/** The one thread this tab has. `components/ask/useAsk.ts` provides it. */
export const askStore = createAskStore();
