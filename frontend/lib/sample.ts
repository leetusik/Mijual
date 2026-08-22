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
 * ## Why the whole composition is stored, not a diff
 *
 * `GET /portfolio/sample` serves the fixed R5-4 composition every time
 * (`P5.S8`: four pinned issuers, live corpus events). A reader may change a
 * 보유량 or delete a row, and both must survive a revisit — so the store holds
 * **which issuers are in the sample and with what count**, seeded from the served
 * composition the first time and authoritative afterwards. A "diff" would have to
 * name a deletion of a row that may or may not still be in the served list, which
 * is a second way to say the same thing.
 *
 * Nothing derived is stored: no amount, no D-day, no name. The rows, the
 * countdowns and the factors are always the server's, and the browser only says
 * *whose* rows and *how many* shares — the same split the account mode has, where
 * the server stores a count and the browser multiplies (`P5.S8` note 1).
 *
 * ## 챙긴 돈 in the sample (R5-8)
 *
 * > 계정에 저장, 샘플/익명에서는 **이 브라우저(localStorage)에**.
 *
 * The mark is keyed on the 증권발행실적보고서's own `rcept_no` — the same key the
 * account-mode endpoint uses (`PUT /portfolio/claims/{rcept_no}`, `P5.S8` note 7)
 * — so an anonymous mark addresses the identical row and could be carried into an
 * account without translation.
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
  v: 1;
  /** The sample's composition as this browser has edited it. */
  holdings: SampleHolding[];
  /** 실적보고서 `rcept_no`s this browser has marked 챙겼습니다 (R5-8). */
  claims: string[];
};

const EVENT = "mijual:sample";

function parse(raw: string | null): SampleState | null {
  if (!raw) return null;
  try {
    const value: unknown = JSON.parse(raw);
    if (!value || typeof value !== "object") return null;
    const state = value as Partial<SampleState>;
    const holdings = Array.isArray(state.holdings)
      ? state.holdings.filter(
          (row): row is SampleHolding =>
            !!row &&
            typeof row.corp_code === "string" &&
            typeof row.shares === "number" &&
            Number.isSafeInteger(row.shares) &&
            row.shares > 0,
        )
      : [];
    const claims = Array.isArray(state.claims)
      ? state.claims.filter((value): value is string => typeof value === "string")
      : [];
    return { v: 1, holdings, claims };
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
