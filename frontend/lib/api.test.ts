/**
 * The API client's smoke check — deliberately three cases and no framework.
 *
 * Run with `npm run smoke` (`node --test lib/`), which uses Node's own runner and
 * its native TypeScript stripping: no jest, no vitest, no jsdom, no fixtures. The
 * *rendering* half of the smoke check is `next build`, which prerenders `app/page.tsx`
 * through the shell and every primitive; what cannot be seen there is what this
 * wrapper puts on the wire, so that is what is asserted here.
 *
 * Repo rule: tests stay terse — minimal high-value cases, no scaffolding sprawl.
 */

import assert from "node:assert/strict";
import test from "node:test";
import { ApiError, CSRF_HEADER, dartUrl, request } from "./api.ts";

type Call = { url: string; init: RequestInit };

function stubFetch(status: number, body: unknown): Call[] {
  const calls: Call[] = [];
  globalThis.fetch = (async (url: string, init: RequestInit = {}) => {
    calls.push({ url: String(url), init });
    return new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json" },
    });
  }) as unknown as typeof fetch;
  return calls;
}

test("a mutating call carries X-Mijual-CSRF and the session cookie; a read does not", async () => {
  const calls = stubFetch(200, { holding: { id: 1, corp_code: "00102618", shares: 500 } });

  await request("/portfolio/holdings", { method: "POST", json: { shares: 500 } });
  await request("/board/summary");

  const [write, read] = calls;
  assert.equal(new Headers(write.init.headers).get(CSRF_HEADER), "1");
  assert.equal(write.init.credentials, "include");
  assert.equal(write.init.body, JSON.stringify({ shares: 500 }));
  // The guard is on unsafe methods only: a GET that sent it would still work,
  // but it would blur where the rule actually lives.
  assert.equal(new Headers(read.init.headers).get(CSRF_HEADER), null);
  assert.equal(read.init.credentials, "include");
});

test("an error envelope becomes an ApiError carrying the code, not the English message", async () => {
  stubFetch(409, {
    error: { code: "holding_exists", message: "already held", message_ko: "…" },
  });

  const failure = await request("/portfolio/holdings", { method: "POST", json: {} }).then(
    () => null,
    (error: unknown) => error,
  );

  assert.ok(failure instanceof ApiError);
  assert.equal(failure.status, 409);
  assert.equal(failure.code, "holding_exists");
  assert.equal(failure.messageKo, "…");
});

test("the DART link is the one shape the whole product uses", () => {
  assert.equal(
    dartUrl("20260724000546"),
    "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260724000546",
  );
});
