/**
 * The AI 질문 store's smoke check — four cases, no framework.
 *
 * Run by `npm run smoke` (`node --test "lib/*.test.ts"`). What `next build`
 * cannot see is the two things this surface is *made* of: the incremental SSE
 * decode (a chunk boundary can fall anywhere, including inside a Korean quote)
 * and the ordering rule the chips depend on — a `citation` **defines** a number
 * immediately before the `text` that names it, so the chip is painted with its
 * sentence. Both are asserted here; the rendering half is `next build` and
 * `P6.S7`'s browser pass.
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
