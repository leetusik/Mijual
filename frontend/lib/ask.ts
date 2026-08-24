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

/** One painted thing inside an answer, in arrival order. */
export type AskBlock =
  | { kind: "tool"; tool: string; row: string; ok: boolean }
  | { kind: "text"; text: string; citations: number[] }
  | { kind: "refusal"; family: string; text: string };

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
  /** The chip's × → 전체 공시. */
  clearScope: () => void;
  /** Ask, and stream the answer into a new turn. */
  ask: (question: string) => void;
  /** 중지 — abort the fetch. Nothing is retracted; released text stands. */
  stop: () => void;
  /** 재시도 — run the same question again, in place of the turn that broke. */
  retry: (turnId: string) => void;
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
      turns: value.turns.map((turn) => ({ ...turn, status: settle(turn.status) })),
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
      turns: state.turns,
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
  return turn.blocks.flatMap((block) => (block.kind === "tool" ? [] : [block.text])).join(" ");
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
            blocks: [
              ...turn.blocks,
              {
                kind: "tool",
                tool: String(data.tool ?? ""),
                row: String(data.row ?? ""),
                ok: data.ok !== false,
              },
            ],
          };
        case "citation":
          return { ...turn, chips: [...turn.chips, data as unknown as AskChip] };
        case "text":
          return {
            ...turn,
            status: "streaming",
            blocks: [
              ...turn.blocks,
              {
                kind: "text",
                text: leading(data.text),
                citations: Array.isArray(data.citations) ? (data.citations as number[]) : [],
              },
            ],
          };
        case "refusal":
          return {
            ...turn,
            status: "streaming",
            blocks: [
              ...turn.blocks,
              {
                kind: "refusal",
                family: String(data.family ?? ""),
                text: leading(data.text),
              },
            ],
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
            answer: typeof data.answer === "string" ? data.answer : released(turn),
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
          ? { ...turn, status: "aborted", answer: released(turn) }
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
    }));
    start(turn.id, turn.question, turn.scope);
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
  };
}

/** The one thread this tab has. `components/ask/useAsk.ts` provides it. */
export const askStore = createAskStore();
