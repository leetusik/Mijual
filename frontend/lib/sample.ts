"use client";

import { useSyncExternalStore } from "react";

/**
 * 샘플 포트폴리오's browser state — **localStorage, and nowhere else**.
 *
 * R5-4 signs the sample as a *mode* of 내 포트폴리오 that a reader enters with one
 * click and no account, edits, and leaves:
 *
 * > 편집 가능 + localStorage 저장(로그인 불요, **재방문 유지**); 로그인 시 이전
 * > 제안 → conversion offer.
 * > 종료: 샘플·브라우저 저장분 삭제 후 로드 전 상태 복귀.
 *
 * and the round's own §Portfolio line states the same rule for anonymous editing:
 * "익명/샘플 편집은 localStorage 저장 — 로그인 없이 재방문에도 유지".
 *
 * ## v2 — the browser stores **edits**, never the composition (`P4.F1`)
 *
 * v1 stored the whole composition: the first sample visit seeded
 * `{holdings: [{corp_code, shares}]}` from the served rows and every later visit
 * rendered *the browser's* list, filtering the served rows by it. That was sound
 * while `GET /portfolio/sample` served four **pinned** issuers, and it broke the
 * moment the server started choosing them per request (`P4.F1`: R5-4's four
 * states are fixed, the issuers in them are not) — a returning browser whose seed
 * named yesterday's issuers would filter today's rows down to **nothing** and
 * render an empty sample.
 *
 * So the rule inverted, and it is the same rule the rest of the product already
 * follows — *the server owns the rows, the browser owns the reader's edits*:
 *
 * * **the served composition is always shown.** An issuer this browser has never
 *   seen renders on sight; nothing is filtered in by a stored list.
 * * the browser keeps only what the reader **did**, keyed by `corp_code`: a
 *   보유량 override (`shares`), an **explicit** removal (`removed`), and R5-8's
 *   챙긴 돈 marks (`claims`, keyed by 실적보고서 `rcept_no`).
 * * an edit against an issuer the server no longer serves is **inert, and kept**
 *   — not pruned. Pruning would need the served composition in here (this module
 *   also runs in 계정 mode, where it is not served at all) and the composition
 *   moves daily: an ① that leaves 다가오는 마감 today is in 지나간 마감 tomorrow, and
 *   a reader's 삭제 of it should still hold when it comes back. The store is
 *   bounded by the issuers one reader has actually touched.
 *
 * R13 Q-D — 「영구 브라우저 편집을 수용한다」 — stays true for every edit that still
 * applies; what changed is that an edit is now a statement about an *issuer*
 * rather than about a list.
 *
 * **What the v1 migration loses, exactly once.** v1's `holdings` become 보유량
 * overrides, and v1's claims carry over untouched. A v1 **removal** cannot be
 * recovered: v1 recorded it only as an *absence* from a seed it never stored, so
 * "the reader deleted this row" and "this row was never in that browser's sample"
 * are the same bytes. Those readers see the removed issuer once more and can
 * delete it again — which is then remembered properly.
 *
 * ## The store's existence is still 「이 브라우저에 샘플이 로드됨」
 *
 * A v2 store therefore starts **empty** — no edits yet — and is written on the
 * first sample render exactly as v1's seed was. That is what R5-4's 이전 제안
 * (계정 이전, offered to a signed-in reader whose browser holds a sample) and
 * 샘플 종료 key on, and it stays a property of the browser rather than of the
 * composition.
 *
 * ## There is no anonymous write endpoint, and there must not be one
 *
 * `security` / `P5.S8` note 13: "Anonymous state never reaches the server …
 * Migration into an account is offered, never automatic." Everything in this
 * module stays in the browser; the only thing that ever leaves it is an ordinary
 * authenticated `POST /portfolio/holdings` the reader accepted (the 이전 제안).
 */

/** The one key this mode writes. Extends `P5.S14`'s convention — one dotted
 * namespace, one JSON object, a version field (`mijual.lookup.holdings` is 조회's
 * sessionStorage twin). */
export const SAMPLE_KEY = "mijual.portfolio.sample";

export type SampleHolding = { corp_code: string; shares: number };

export type SampleState = {
  v: 2;
  /** 보유량 this browser has changed, by `corp_code`. Absent = the served count. */
  shares: Record<string, number>;
  /** Issuers this browser removed **explicitly**. Hidden while they are served. */
  removed: string[];
  /** 실적보고서 `rcept_no`s this browser has marked 챙겼습니다 (R5-8). */
  claims: string[];
};

const EVENT = "mijual:sample";

/** A loaded sample with no edits in it yet. */
export function emptySample(): SampleState {
  return { v: 2, shares: {}, removed: [], claims: [] };
}

function strings(value: unknown): string[] {
  return Array.isArray(value)
    ? [...new Set(value.filter((item): item is string => typeof item === "string"))]
    : [];
}

function count(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value) && value > 0;
}

function parse(raw: string | null): SampleState | null {
  if (!raw) return null;
  try {
    const value: unknown = JSON.parse(raw);
    if (!value || typeof value !== "object") return null;
    const state = value as Record<string, unknown>;
    const claims = strings(state.claims);

    const shares: Record<string, number> = {};
    if (Array.isArray(state.holdings)) {
      // v1 → v2: the stored composition becomes 보유량 overrides. A v1 removal is
      // unrecoverable (see the module docstring) and is forgotten here, once.
      for (const row of state.holdings) {
        if (!row || typeof row !== "object") continue;
        const holding = row as Record<string, unknown>;
        if (typeof holding.corp_code === "string" && count(holding.shares)) {
          shares[holding.corp_code] = holding.shares;
        }
      }
      return { v: 2, shares, removed: [], claims };
    }

    if (state.shares && typeof state.shares === "object") {
      for (const [corpCode, value] of Object.entries(state.shares as Record<string, unknown>)) {
        if (count(value)) shares[corpCode] = value;
      }
    }
    return { v: 2, shares, removed: strings(state.removed), claims };
  } catch {
    // A broken store is treated as no sample: the mode is a courtesy, and a
    // parse failure must never take a page down.
    return null;
  }
}

// `useSyncExternalStore` compares snapshots by identity, so the parsed object is
// cached against the raw string it came from — re-parsing on every render would
// return a new object every time and loop.
let cachedRaw: string | null = null;
let cachedState: SampleState | null = null;

/** The sample this browser holds, or `null` when no sample is loaded. */
export function readSample(): SampleState | null {
  if (typeof window === "undefined") return null;
  let raw: string | null = null;
  try {
    raw = window.localStorage.getItem(SAMPLE_KEY);
  } catch {
    return null;
  }
  if (raw !== cachedRaw) {
    cachedRaw = raw;
    cachedState = parse(raw);
  }
  return cachedState;
}

/** Write, and tell every subscriber in this tab (the `storage` event only fires
 * in the *other* tabs). */
export function writeSample(state: SampleState): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(SAMPLE_KEY, JSON.stringify(state));
  } catch {
    // Storage denied: the reader loses persistence across a revisit, which is a
    // courtesy, not a fact they need. Never throw inside an edit.
  }
  window.dispatchEvent(new Event(EVENT));
}

/** Apply one edit to whatever this browser holds — an absent store counts as an
 * empty one, so an edit is never lost to a missing seed. */
function edit(change: (state: SampleState) => SampleState): void {
  writeSample(change(readSample() ?? emptySample()));
}

/** Mark this browser as holding a sample, without asserting any edit. Written on
 * the first sample render; v1's seed did this as a side effect of storing the
 * composition, which is the part that had to go. */
export function ensureSample(): void {
  if (typeof window === "undefined" || readSample() !== null) return;
  writeSample(emptySample());
}

/** 보유량 수정 on one row. */
export function setSampleShares(corpCode: string, shares: number): void {
  edit((state) => ({ ...state, shares: { ...state.shares, [corpCode]: shares } }));
}

/** 삭제 — explicit, and remembered while that issuer is still served. */
export function removeSampleHolding(corpCode: string): void {
  edit((state) => ({
    ...state,
    removed: [...new Set([...state.removed, corpCode])],
  }));
}

/** 되돌리기 (the 8초 undo): the removal goes, and the count the row had is kept. */
export function restoreSampleHolding(corpCode: string, shares: number | null): void {
  edit((state) => ({
    ...state,
    shares: shares === null ? state.shares : { ...state.shares, [corpCode]: shares },
    removed: state.removed.filter((code) => code !== corpCode),
  }));
}

/** 챙긴 돈 (R5-8) — this browser's own mark on one 실적보고서. */
export function setSampleClaim(rceptNo: string, claimed: boolean): void {
  edit((state) => ({
    ...state,
    claims: claimed
      ? [...new Set([...state.claims, rceptNo])]
      : state.claims.filter((value) => value !== rceptNo),
  }));
}

/** This browser's 보유량 for an issuer, or the served one. */
export function sharesOf(
  state: SampleState | null,
  corpCode: string,
  served: number | null | undefined,
): number | null {
  const edited = state?.shares[corpCode];
  return edited ?? served ?? null;
}

/** Did this browser delete that issuer from its sample? */
export function isRemoved(state: SampleState | null, corpCode: string): boolean {
  return state !== null && state.removed.includes(corpCode);
}

/**
 * 샘플 종료 — "샘플·브라우저 저장분 삭제 후 로드 전 상태 복귀".
 *
 * The whole store goes, claims included: they were this browser's assertions
 * about a sample that no longer exists.
 */
export function clearSample(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(SAMPLE_KEY);
  } catch {
    /* nothing to clear if storage is denied */
  }
  window.dispatchEvent(new Event(EVENT));
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener(EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

/** The sample state, live — for the surface that renders it and for the chrome
 * slot R5-4 replaces while it is loaded. */
export function useSample(): SampleState | null {
  return useSyncExternalStore(subscribe, readSample, () => null);
}

/** "Is a sample loaded in this browser?" — the chrome's question. Server-rendered
 * as `false`, so the slot never claims a sample the browser has not loaded. */
export function useSampleActive(): boolean {
  return useSample() !== null;
}
