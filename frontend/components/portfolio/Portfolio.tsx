"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CraftPanel } from "@/components";
import { ConversionOffer } from "@/components/auth";
import {
  addHolding,
  deleteHolding,
  getPortfolio,
  getStock,
  setClaim as setClaimRequest,
  updateHolding,
} from "@/lib/api";
import { readSessionHoldings } from "@/lib/holding";
import { clearSample, readSample, useSample, writeSample } from "@/lib/sample";
import type { Portfolio as PortfolioPayload, PortfolioHolding, RightsRow } from "@/lib/types";
import { AddHolding, type ResolvedStock } from "./AddHolding";
import { CarryOver, type CarryEntry } from "./CarryOver";
import { Deadlines } from "./Deadlines";
import { Holdings } from "./Holdings";
import { SampleBanner } from "./SampleBanner";
import { EMPTY_BODY_KO, EMPTY_TITLE_KO, HOLDING_CAPTION_KO, UNDO_SECONDS } from "./copy";
import styles from "./Portfolio.module.css";

/**
 * 내 포트폴리오 — the 2층 itself, in its two modes (R5 §Portfolio, §D-day 목록,
 * §샘플 포트폴리오).
 *
 * ## No page 대제목, by revision
 *
 * 개정 ③: "본문 대제목 제거 — **header nav가 위치 표시**". So this surface opens
 * with its content: the banner where there is one, the holdings, then the D-day
 * sections. The layer's name appears exactly once in the product, in the account
 * menu that leads here (`components/chrome/AccountSlot.tsx`).
 *
 * ## Two modes, one rendering
 *
 * **계정** — the payload is `GET /portfolio` for the signed-in reader, and every
 * edit is an ordinary authenticated write followed by a re-read of the same
 * endpoint, so the sections, their order and their D-days stay the server's.
 * Nothing here re-composes a row.
 *
 * **샘플** (R5-4) — the payload is the anonymous `GET /portfolio/sample` (the four
 * pinned filings, live), and the reader's edits live in `localStorage`
 * (`lib/sample.ts`): "편집 가능 + localStorage 저장(로그인 불요, 재방문 유지)".
 * The store holds *which issuers, with what count* and the browser's 챙긴 돈
 * marks; the rows, the factors and the D-days are still the server's, and the
 * client only overrides the two numbers it owns. **No anonymous write exists and
 * none is attempted** (`P5.S8` note 13).
 *
 * ⚠ **종목 추가 is an account affordance and is not offered in 샘플 모드.** R5-4
 * signs the sample as a fixed composition that is *editable* (보유량, 삭제, and
 * R5-8's mark) and endable; adding an arbitrary issuer would need this client to
 * compose that issuer's rows and place them into 다가오는/지나간 itself — a second
 * composition site for exactly the placement rules `P5.S8` owns (a past ③, for
 * one, appears in no 조회 payload at all), which is how two surfaces start
 * disagreeing. Recorded for `P5.S19`/`P5.REVIEW` rather than implemented against
 * a contract that does not serve it.
 */
export function Portfolio({
  payload: served,
  mode,
  preselect,
}: {
  payload: PortfolioPayload;
  mode: "account" | "sample";
  preselect: ResolvedStock | null;
}) {
  const [busy, setWorking] = useState(false);

  // The served payload is the truth this surface starts from; a re-read after a
  // write replaces it wholesale (see `run`). A fresh server render — a
  // navigation, a reload — wins over whatever the last re-read left here.
  const [payload, setPayload] = useState(served);
  useEffect(() => setPayload(served), [served]);

  const sample = useSample();
  const local = mode === "sample" ? sample : null;

  // The sample's first load seeds the browser from the served composition; every
  // later visit is the browser's own version of it.
  useEffect(() => {
    if (mode !== "sample" || readSample() !== null) return;
    writeSample({
      v: 1,
      holdings: payload.holdings.map((row) => ({
        corp_code: row.corp_code,
        shares: row.shares,
      })),
      claims: [],
    });
  }, [mode, payload]);

  const localShares = useMemo(
    () => new Map((local?.holdings ?? []).map((row) => [row.corp_code, row.shares])),
    [local],
  );

  const shown = useCallback(
    (corpCode: string) => (local === null ? true : localShares.has(corpCode)),
    [local, localShares],
  );

  const sharesFor = useCallback(
    (corpCode: string, served: number | null | undefined) =>
      localShares.get(corpCode) ?? served ?? null,
    [localShares],
  );

  const holdings: PortfolioHolding[] = useMemo(
    () =>
      payload.holdings
        .filter((row) => shown(row.corp_code))
        .map((row) => ({ ...row, shares: sharesFor(row.corp_code, row.shares) ?? row.shares })),
    [payload.holdings, shown, sharesFor],
  );

  const upcoming = useMemo(
    () => payload.upcoming.filter((row) => shown(row.corp_code)),
    [payload.upcoming, shown],
  );
  const past = useMemo(
    () => payload.past.filter((row) => shown(row.corp_code)),
    [payload.past, shown],
  );

  const heldCorpCodes = useMemo(
    () => new Set(holdings.map((row) => row.corp_code)),
    [holdings],
  );

  // ---------------------------------------------------------------------
  // Mutations — an account write plus a re-read, or a localStorage write
  // ---------------------------------------------------------------------

  /**
   * Every account edit is `write → re-read`, never a local recomposition: the
   * server owns the rows, the factors, the placement and the D-days, so once the
   * write lands we ask **the same endpoint** for the whole payload again and
   * render whatever comes back. A failed write re-reads too — the surface then
   * shows the truth instead of an edit that did not happen.
   *
   * The re-read is this client's own `GET /portfolio` rather than
   * `router.refresh()`. Both are one request to one authority — this page reads
   * that same endpoint — and this one is the cheaper of the two: it costs no
   * server re-render of the whole route, and Next 16 answers a `refresh()` by
   * re-prefetching every `<Link>` in the viewport as well (vercel/next.js
   * #93210), which is a burst of server work per 보유량 edit. What comes back is
   * the served payload, whole: the rows, the placement and the D-days are still
   * composed exactly once, on the server.
   */
  const reread = useCallback(() => {
    if (mode !== "account") return Promise.resolve();
    return getPortfolio()
      .then(setPayload)
      .catch(() => undefined);
  }, [mode]);

  const run = useCallback(
    (work: () => Promise<unknown>) => {
      setWorking(true);
      void work()
        .catch(() => undefined)
        .then(reread)
        .finally(() => setWorking(false));
    },
    [reread],
  );

  const [editing, setEditing] = useState<string | null>(null);

  const saveShares = useCallback(
    (row: PortfolioHolding, shares: number) => {
      if (local !== null) {
        writeSample({
          ...local,
          holdings: local.holdings.map((entry) =>
            entry.corp_code === row.corp_code ? { ...entry, shares } : entry,
          ),
        });
        return;
      }
      if (row.id === undefined) return;
      run(() => updateHolding(row.id as number, shares));
    },
    [local, run],
  );

  // 삭제 = 즉시 + 8초 되돌리기 (모달 없음). The row is really gone; what the
  // client keeps for 8 seconds is the two facts needed to put it back.
  const [undo, setUndo] = useState<CarryEntry | null>(null);
  const undoTimer = useRef<number | null>(null);

  const armUndo = useCallback((entry: CarryEntry) => {
    setUndo(entry);
    if (undoTimer.current !== null) window.clearTimeout(undoTimer.current);
    undoTimer.current = window.setTimeout(() => setUndo(null), UNDO_SECONDS * 1000);
  }, []);

  useEffect(
    () => () => {
      if (undoTimer.current !== null) window.clearTimeout(undoTimer.current);
    },
    [],
  );

  const removeHolding = useCallback(
    (row: PortfolioHolding) => {
      setEditing(null);
      armUndo({ corp_code: row.corp_code, corp_name: row.corp_name, shares: row.shares });
      if (local !== null) {
        writeSample({
          ...local,
          holdings: local.holdings.filter((entry) => entry.corp_code !== row.corp_code),
        });
        return;
      }
      if (row.id === undefined) return;
      run(() => deleteHolding(row.id as number));
    },
    [armUndo, local, run],
  );

  const restoreHolding = useCallback(() => {
    if (!undo) return;
    const entry = undo;
    setUndo(null);
    if (undoTimer.current !== null) window.clearTimeout(undoTimer.current);
    if (mode === "sample") {
      const current = readSample() ?? { v: 1 as const, holdings: [], claims: [] };
      writeSample({
        ...current,
        holdings: [...current.holdings, { corp_code: entry.corp_code, shares: entry.shares }],
      });
      return;
    }
    run(() => addHolding(entry.corp_code, entry.shares));
  }, [undo, mode, run]);

  const claim = useCallback(
    (row: RightsRow, claimed: boolean) => {
      const key = row.lapse?.performance_rcept_no;
      if (!key) return;
      if (mode === "sample") {
        const current = readSample() ?? { v: 1 as const, holdings: [], claims: [] };
        const claims = claimed
          ? [...new Set([...current.claims, key])]
          : current.claims.filter((value) => value !== key);
        writeSample({ ...current, claims });
        return;
      }
      run(() => setClaimRequest(key, claimed));
    },
    [mode, run],
  );

  const claimedOf = useCallback(
    (row: RightsRow) => {
      const key = row.lapse?.performance_rcept_no;
      if (!key) return null;
      if (mode === "sample") return (local?.claims ?? []).includes(key);
      return row.claimed === true;
    },
    [mode, local],
  );

  const add = useCallback(
    (stock: ResolvedStock, shares: number) => run(() => addHolding(stock.corp_code, shares)),
    [run],
  );

  // ---------------------------------------------------------------------
  // The two offers (R5-3, R5-4) — see `CarryOver.tsx`
  // ---------------------------------------------------------------------

  const carry = useCarryOffer({
    mode,
    empty: holdings.length === 0,
    heldCorpCodes,
    // `NO_HOLDINGS` rather than a fresh `[]`: this value is a dependency two
    // levels down, and a new array identity on every render is a render loop
    // (see `useCarryOffer`).
    sampleCorpCodes: sample?.holdings ?? NO_HOLDINGS,
  });

  const keepCarried = useCallback(
    (entries: CarryEntry[]) => {
      setWorking(true);
      void Promise.all(entries.map((entry) => addHolding(entry.corp_code, entry.shares)))
        .catch(() => undefined)
        .then(reread)
        .finally(() => {
          setWorking(false);
          carry.dismiss();
          // A sample the reader has just carried into their account is no longer
          // a sample: its rows are theirs now, so the mode ends and the chrome
          // slot returns to the account menu.
          if (carry.variant === "migrate") clearSample();
        });
    },
    [carry, reread],
  );

  return (
    <div className={styles.surface}>
      {mode === "sample" ? <SampleBanner /> : null}

      {carry.entries.length > 0 ? (
        <CarryOver
          variant={carry.variant}
          entries={carry.entries}
          busy={busy}
          onKeep={keepCarried}
          onDiscard={carry.dismiss}
        />
      ) : null}

      {holdings.length === 0 ? (
        <CraftPanel>
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>{EMPTY_TITLE_KO}</p>
            <p className={styles.emptyBody}>{EMPTY_BODY_KO}</p>
          </div>
        </CraftPanel>
      ) : (
        <Holdings
          rows={holdings}
          busy={busy}
          captionKo={mode === "sample" ? null : HOLDING_CAPTION_KO}
          editing={editing}
          onEditing={setEditing}
          undo={undo}
          onSave={saveShares}
          onDelete={removeHolding}
          onUndo={restoreHolding}
        />
      )}

      {mode === "account" ? (
        <AddHolding
          preselect={preselect}
          heldCorpCodes={heldCorpCodes}
          busy={busy}
          onAdd={add}
          onEditExisting={setEditing}
        />
      ) : null}

      <Deadlines
        reference={payload.reference}
        upcoming={upcoming}
        past={past}
        sharesOf={(row) => sharesFor(row.corp_code, row.shares)}
        claimedOf={claimedOf}
        onClaim={claim}
        claimCaption={mode === "sample" ? "local" : "account"}
        busy={busy}
      />

      {/* R13 §4 (Q-E) — the product's one conversion offer, on the surface that
          had none: R12's band, **after 지나간 마감** so it never stands above a
          number, at R12's own tier (inset, no brackets, dismissible, once per
          session, anonymous only — the band probes the session itself). It
          renders **without R12's lead line**, because 「이 보유량은 탭을 닫으면
          사라집니다」 is false here: a sample's edits live in `localStorage` and
          survive the tab (R5-4; Q-D accepted that permanence and withdrew 종료).
          `ready` is R12's own condition — "a per-holding value has rendered" —
          which on this surface is simply: there are holdings to talk about. */}
      {mode === "sample" ? <ConversionOffer ready={holdings.length > 0} lead={false} /> : null}
    </div>
  );
}

/**
 * Which offer, if any, this visit should make — and the names it needs.
 *
 * R5-3's 세션 이월 is offered **on an empty account portfolio** ("빈 포트폴리오에
 * inset 행") for holdings 조회 remembered in this tab's `sessionStorage`; R5-4's
 * 계정 이전 is offered to a signed-in reader whose browser still holds a sample.
 * Neither is ever automatic, and declining keeps the browser's value — so the
 * dismissal is a session flag, not a deletion.
 *
 * The names come from `GET /stocks/{corp_code}`, the same anonymous read 조회 uses
 * for a stock: `sessionStorage` and the sample store both keep a `corp_code` and
 * a count and nothing else, because a stored name would be a second spelling of a
 * fact the corpus already owns.
 */
function useCarryOffer({
  mode,
  empty,
  heldCorpCodes,
  sampleCorpCodes,
}: {
  mode: "account" | "sample";
  empty: boolean;
  heldCorpCodes: ReadonlySet<string>;
  sampleCorpCodes: ReadonlyArray<{ corp_code: string; shares: number }>;
}): { variant: "session" | "migrate"; entries: CarryEntry[]; dismiss: () => void } {
  const variant: "session" | "migrate" =
    mode === "account" && sampleCorpCodes.length > 0 ? "migrate" : "session";
  const [entries, setEntries] = useState<CarryEntry[]>([]);
  const [dismissed, setDismissed] = useState(true);

  const key = variant === "migrate" ? MIGRATE_FLAG : CARRY_FLAG;
  const candidates = useMemo(() => {
    if (mode !== "account") return [] as Array<{ corp_code: string; shares: number }>;
    if (variant === "migrate") {
      return sampleCorpCodes.filter((row) => !heldCorpCodes.has(row.corp_code));
    }
    if (!empty) return [];
    return Object.entries(readSessionHoldings().entries)
      .filter(([corpCode]) => !heldCorpCodes.has(corpCode))
      .map(([corp_code, shares]) => ({ corp_code, shares }));
    // `heldCorpCodes` is a Set identity that changes with the payload, which is
    // exactly when this should be recomputed.
  }, [mode, variant, empty, heldCorpCodes, sampleCorpCodes]);

  useEffect(() => {
    let live = true;
    if (candidates.length === 0) {
      // Functional, and identity-preserving: `setEntries([])` would store a new
      // array every time this effect ran, and a state update that always
      // "changes" is a render loop waiting for a dependency to churn.
      setEntries((current) => (current.length === 0 ? current : NO_ENTRIES));
      return;
    }
    setDismissed(readFlag(key));
    void Promise.all(
      candidates.map(async (row) => {
        const named = await getStock(row.corp_code)
          .then((page) => page.stock.corp_name)
          .catch(() => null);
        return { corp_code: row.corp_code, corp_name: named, shares: row.shares };
      }),
    ).then((named) => {
      if (live) setEntries(named);
    });
    return () => {
      live = false;
    };
  }, [candidates, key]);

  return {
    variant,
    entries: dismissed ? [] : entries,
    dismiss: () => {
      setDismissed(true);
      writeFlag(key);
    },
  };
}

/**
 * Two frozen empties, and the bug they close.
 *
 * A React dependency is compared by identity, so a `[]` written inline in a
 * render is a *different* value every render. Here that mattered twice over:
 * `sampleCorpCodes` feeds a `useMemo` that feeds an effect's dependency list,
 * and the effect sets state — so an inline `[]` made the effect re-run and
 * re-set state on every render, forever. The visible symptom was not a warning
 * or a hang but **the App Router quietly refusing to move**: every client
 * navigation and every `router.refresh()` from this surface was interrupted by
 * the next render and its RSC fetch aborted (`net::ERR_ABORTED`, measured), so
 * links did nothing and the page never picked up a write. One shared empty per
 * shape fixes it at the root.
 */
const NO_HOLDINGS: ReadonlyArray<{ corp_code: string; shares: number }> = [];
const NO_ENTRIES: CarryEntry[] = [];

/** 담지 않기 is remembered for the tab, never for the account: the value stays in
 * the browser, and a new session may ask again. */
const CARRY_FLAG = "mijual.portfolio.carry";
const MIGRATE_FLAG = "mijual.portfolio.migrate";

function readFlag(key: string): boolean {
  try {
    return window.sessionStorage.getItem(key) !== null;
  } catch {
    return false;
  }
}

function writeFlag(key: string): void {
  try {
    window.sessionStorage.setItem(key, "1");
  } catch {
    /* storage denied — the offer simply asks again */
  }
}
