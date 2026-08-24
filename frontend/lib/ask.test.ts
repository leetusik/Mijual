/**
 * The AI 질문 store's smoke check — eight cases, no framework.
 *
 * Run by `npm run smoke` (`node --test "lib/*.test.ts"`). What `next build`
 * cannot see is the things this surface is *made* of: the incremental SSE
 * decode (a chunk boundary can fall anywhere, including inside a Korean quote),
 * the ordering rule the chips depend on — a `citation` **defines** a number
 * immediately before the `text` that names it, so the chip is painted with its
 * sentence — and, from `P9.S8`, the **keyed reduce**: a block arriving twice on
 * one `block_id` is replaced where it stands, and the transient 진행 표시 line is
 * dropped at prose and never written to storage — and, from `P9.S10`, that
 * 「새 대화」 empties the stored thread as well as the live one. The rendering half
 * is `next build` and `P9.S9`/`P9.S11`'s browser passes.
 *
 * Repo rule: tests stay terse — minimal high-value cases, no scaffolding sprawl.
 */

import assert from "node:assert/strict";
import test from "node:test";
import { decodeSse } from "./api.ts";
import { createAskStore } from "./ask.ts";

const FRAMES = [
  'event: session\ndata: {"session_hash":"0f3a"}\n\n',
  'event: tool_row\ndata: {"tool":"get_event","row":"이벤트 읽기 → 계양전기 · ① 유상증자 · 20260724000546","ok":true}\n\n',
  'event: citation\ndata: {"number":1,"rcept_no":"20260724000546","api_tier":false,"quote":"청약 개시일"}\n\n',
  'event: text\ndata: {"text":"청약은 09-01에 시작합니다.","citations":[1]}\n\n',
  'event: footer\ndata: {"count":1,"evidence":["20260724000546"],"generated_at":"2026-08-22T12:00:00+09:00","links":[{"kind":"event","rcept_no":"20260724000546"}]}\n\n',
  'event: done\ndata: {"status":"done","kind":"answer","answer":"청약은 09-01에 시작합니다.","evidence":["20260724000546"],"quotes":["청약 개시일"],"blocked":0,"rounds":1,"tool_calls":1,"usage":{}}\n\n',
].join("");

/**
 * The whole stream in `size`-byte slices, so no frame arrives whole — and
 * honouring `signal`, because 중지 **is** the abort and a stub that ignored it
 * would test nothing.
 */
function stubStream(body: string, { size = 7, delay = 0 } = {}): void {
  globalThis.fetch = (async (_url: string, init: RequestInit = {}) => {
    const bytes = new TextEncoder().encode(body);
    let at = 0;
    let live = true;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        init.signal?.addEventListener("abort", () => {
          if (!live) return;
          live = false;
          controller.error(new Error("aborted"));
        });
      },
      async pull(controller) {
        if (delay > 0) await new Promise((resume) => setTimeout(resume, delay));
        if (!live) return;
        if (at >= bytes.length) {
          live = false;
          return controller.close();
        }
        controller.enqueue(bytes.slice(at, at + size));
        at += size;
      },
      cancel() {
        live = false;
      },
    });
    return new Response(stream, {
      status: 200,
      headers: { "content-type": "text/event-stream" },
    });
  }) as unknown as typeof fetch;
}

async function settled<T>(read: () => T, done: (value: T) => boolean): Promise<T> {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (done(read())) return read();
    await new Promise((resume) => setTimeout(resume, 5));
  }
  throw new Error("the turn never settled");
}

test("a frame split across chunks is decoded once, whole", () => {
  const half = 'event: text\ndata: {"text":"공시에 없는 내용은 해설';
  const first = decodeSse(half);
  assert.deepEqual(first.frames, []);
  assert.equal(first.rest, half);

  const { frames, rest } = decodeSse(`${half}하지 않습니다."}\n\nevent: don`);
  assert.equal(frames.length, 1);
  assert.equal(frames[0].event, "text");
  assert.equal(JSON.parse(frames[0].data).text, "공시에 없는 내용은 해설하지 않습니다.");
  assert.equal(rest, "event: don");
});

test("a turn paints tool rows, numbered chips and the footer, and ends done", async () => {
  stubStream(FRAMES);
  const store = createAskStore();
  store.ask("청약 언제 시작해요?");

  const state = await settled(
    () => store.getSnapshot(),
    (snapshot) => snapshot.turns[0]?.status === "done",
  );
  const turn = state.turns[0];

  assert.equal(state.sessionHash, "0f3a");
  assert.deepEqual(
    turn.blocks.map((block) => block.kind),
    ["tool", "text"],
  );
  // The chip's definition arrived before the sentence that names it, so the
  // renderer can draw both in one paint — 자리표시 칩·후행 부착 금지.
  assert.deepEqual(turn.chips[0], {
    number: 1,
    rcept_no: "20260724000546",
    api_tier: false,
    quote: "청약 개시일",
  });
  assert.deepEqual(turn.blocks[1], {
    kind: "text",
    text: "청약은 09-01에 시작합니다.",
    citations: [1],
  });
  assert.equal(turn.footer?.count, 1);
  assert.equal(turn.answer, "청약은 09-01에 시작합니다.");
});

test("a pre-stream refusal leaves the turn in the 중단 state with nothing invented", async () => {
  globalThis.fetch = (async () =>
    new Response(JSON.stringify({ error: { code: "rate_limited" } }), {
      status: 429,
      headers: { "content-type": "application/json" },
    })) as unknown as typeof fetch;

  const store = createAskStore();
  store.ask("한도가 있나요?");
  const state = await settled(
    () => store.getSnapshot(),
    (snapshot) => snapshot.turns[0]?.status === "error",
  );

  // No blocks, no copy, no code on the screen: the surface shows R6's one signed
  // 중단 row and 재시도, which is a rendering decision and not stored state.
  assert.deepEqual(state.turns[0].blocks, []);
  assert.equal(state.turns[0].answer, "");
});

test("중지 keeps the partial answer and ends the turn as 중단", async () => {
  stubStream(FRAMES, { size: 200, delay: 25 });
  const store = createAskStore();
  store.ask("청약 언제 시작해요?");

  await settled(
    () => store.getSnapshot(),
    (snapshot) => (snapshot.turns[0]?.blocks.length ?? 0) > 0,
  );
  store.stop();

  const state = await settled(
    () => store.getSnapshot(),
    (snapshot) => snapshot.turns[0]?.status === "aborted",
  );
  // 부분 답변 유지 — 지우기 금지.
  assert.ok(state.turns[0].blocks.length > 0);
});

test("a turn minted after a restored thread never reuses a stored id", async () => {
  // A thread written by an earlier build carries the legacy `t1`/`t2` ids and must
  // still hydrate (`Persisted.v` stays 1); they only have to stay distinct from
  // whatever *this* load mints — a collision would stream one answer into two
  // turns and retry the wrong one, not merely warn about a duplicate React key.
  const stored = {
    v: 1,
    scope: null,
    scopeChosen: false,
    sessionHash: null,
    turns: ["t1", "t2"].map((id) => ({
      id,
      question: `질문 ${id}`,
      scope: null,
      blocks: [],
      chips: [],
      links: [],
      footer: null,
      status: "done",
      answer: "답변.",
    })),
  };
  const items = new Map([["mijual.ask.thread", JSON.stringify(stored)]]);
  const scope = globalThis as { window?: unknown };
  scope.window = {
    sessionStorage: {
      getItem: (key: string) => items.get(key) ?? null,
      setItem: (key: string, value: string) => {
        items.set(key, value);
      },
    },
  };
  globalThis.fetch = (async () =>
    new Response(JSON.stringify({ error: { code: "rate_limited" } }), {
      status: 429,
      headers: { "content-type": "application/json" },
    })) as unknown as typeof fetch;

  try {
    const store = createAskStore();
    store.hydrate();
    store.ask("이번엔 어떻게 되나요?");
    const state = await settled(
      () => store.getSnapshot(),
      (snapshot) => snapshot.turns[2]?.status === "error",
    );
    const ids = state.turns.map((turn) => turn.id);
    assert.deepEqual(ids.slice(0, 2), ["t1", "t2"]);
    assert.equal(new Set(ids).size, 3);
  } finally {
    delete scope.window;
  }
});


/**
 * A turn as `P9.S3`/`P9.S5` land it on the wire — status, a data block, and a
 * calculation that settles on its own id **after** a 도구 행 arrived between the
 * two. That gap is the point: 「같은 `block_id`의 후속 이벤트는 추가가 아니라
 * 제자리 교체」, so the settled block must still sit where it was drawn.
 */
const R16_FRAMES = [
  'event: session\ndata: {"session_hash":"0f3a"}\n\n',
  'event: status\ndata: {"phase":"read","text":"질문을 읽고 있습니다","block_id":"status","persistent":false}\n\n',
  'event: status\ndata: {"phase":"open","text":"공시 원문을 읽고 있습니다","block_id":"status","persistent":false}\n\n',
  'event: tool_row\ndata: {"tool":"get_event","row":"이벤트 읽기 → 계양전기 · ① 유상증자 · 20260724000546","ok":true}\n\n',
  'event: citation\ndata: {"number":1,"rcept_no":"20260724000546","api_tier":false,"quote":"배정비율"}\n\n',
  'event: data\ndata: {"rows":[{"label":"배정비율","value":"0.2주","citation":1},{"label":"보유 주식","value":"1,000주","reader_input":true}],"block_id":"data-1","persistent":true}\n\n',
  'event: status\ndata: {"phase":"calc","text":"계산하고 있습니다","block_id":"status","persistent":false}\n\n',
  'event: calc\ndata: {"mode":"verified","name":"배정 신주","inputs":[{"label":"보유 주식","value":"1,000주","reader_input":true}],"state":"pending","block_id":"calc-2","persistent":true}\n\n',
  'event: tool_row\ndata: {"tool":"calculate","row":"계산 → 배정 신주 · 1건","ok":true}\n\n',
  'event: calc\ndata: {"mode":"verified","name":"배정 신주","inputs":[{"label":"보유 주식","value":"1,000주","reader_input":true}],"state":"done","expr":"1,000주 × 0.2주 = 200주","result":"200주","block_id":"calc-2","persistent":true}\n\n',
  'event: text\ndata: {"text":"배정 신주는 200주입니다.","citations":[1],"unverified":[[7,11]]}\n\n',
  'event: footer\ndata: {"count":1,"evidence":["20260724000546"],"generated_at":"2026-08-25T12:00:00+09:00","links":[]}\n\n',
  'event: done\ndata: {"status":"done","kind":"answer","answer":"배정 신주는 200주입니다.","evidence":["20260724000546"],"quotes":["배정비율"],"blocked":1,"filings":1,"rounds":2,"tool_calls":2,"usage":{}}\n\n',
].join("");

test("a block arriving twice on one id is replaced where it stands", async () => {
  stubStream(R16_FRAMES);
  const store = createAskStore();
  store.ask("1,000주면 몇 주 배정되나요?");

  const state = await settled(
    () => store.getSnapshot(),
    (snapshot) => snapshot.turns[0]?.status === "done",
  );
  const turn = state.turns[0];

  // Two `status` frames and two `calc` frames arrived; neither added a block, and
  // the 진행 표시 line is gone at the first sentence (R16 §2.1).
  assert.deepEqual(
    turn.blocks.map((block) => block.kind),
    ["tool", "data", "calc", "tool", "text"],
  );
  // The settled calculation is still **before** the 도구 행 that arrived between
  // `pending` and `done` — the block does not jump (§4 check 5).
  const calc = turn.blocks[2];
  assert.equal(calc.kind === "calc" && calc.state, "done");
  assert.equal(calc.kind === "calc" && calc.result, "200주");
  const rows = turn.blocks[1];
  assert.equal(rows.kind === "data" && rows.rows[0].citation, 1);
  assert.equal(rows.kind === "data" && rows.rows[1].reader_input, true);
  // 미확인 spans ride the sentence; the terminal's counters ride the turn.
  const prose = turn.blocks[4];
  assert.deepEqual(prose.kind === "text" && prose.unverified, [[7, 11]]);
  assert.equal(turn.filings, 1);
  assert.equal(turn.blocked, 1);
});

test("the transient 진행 표시 line is never written to sessionStorage", async () => {
  const writes: string[] = [];
  const scope = globalThis as { window?: unknown };
  scope.window = {
    sessionStorage: {
      getItem: () => null,
      setItem: (_key: string, value: string) => writes.push(value),
    },
  };
  stubStream(R16_FRAMES);

  try {
    const store = createAskStore();
    store.hydrate();
    let live = false;
    store.subscribe(() => {
      if (store.getSnapshot().turns[0]?.blocks.some((block) => block.kind === "status")) {
        live = true;
      }
    });
    store.ask("1,000주면 몇 주 배정되나요?");
    await settled(
      () => store.getSnapshot(),
      (snapshot) => snapshot.turns[0]?.status === "done",
    );

    // It really was on the screen …
    assert.ok(live);
    // … and it reached no write. A tab reloaded mid-turn would otherwise restore
    // 「공시 원문을 읽고 있습니다」 under a turn `settle()` marks 중단.
    assert.ok(writes.length > 0);
    assert.ok(!writes.some((payload) => payload.includes('"kind":"status"')));
  } finally {
    delete scope.window;
  }
});

/**
 * 「새 대화」 (R16 §2.7b) — 「스레드를 비우는 동작만 … 이력 목록·제목·복원을 만들지
 * 않는다」.
 *
 * Two halves are worth pinning, and neither is visible to `next build`: the
 * stored thread has to be emptied **with** the live one (a 새 대화 that left the
 * turns in `sessionStorage` would restore them on the next reload — a history the
 * record forbids), and the 범위 and the session handle have to survive, because
 * the control was given exactly one job and minting a second `session_hash` would
 * fork the 대화 로그's own grouping.
 */
test("새 대화 empties the thread and the storage behind it, and nothing else", async () => {
  const items = new Map<string, string>();
  const scope = globalThis as { window?: unknown };
  scope.window = {
    sessionStorage: {
      getItem: (key: string) => items.get(key) ?? null,
      setItem: (key: string, value: string) => {
        items.set(key, value);
      },
    },
  };
  stubStream(FRAMES);

  try {
    const store = createAskStore();
    store.hydrate();
    store.setScope({ rcept_no: "20260724000546", name: "계양전기" });
    store.ask("청약은 언제 시작하나요?");
    await settled(
      () => store.getSnapshot(),
      (snapshot) => snapshot.turns[0]?.status === "done",
    );

    store.newChat();
    const after = store.getSnapshot();
    assert.deepEqual(after.turns, []);
    assert.equal(after.sessionHash, "0f3a");
    assert.deepEqual(after.scope, { rcept_no: "20260724000546", name: "계양전기" });
    assert.deepEqual(JSON.parse(items.get("mijual.ask.thread") ?? "{}").turns, []);
  } finally {
    delete scope.window;
  }
});
