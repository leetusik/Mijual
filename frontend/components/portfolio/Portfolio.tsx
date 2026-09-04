"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CraftPanel } from "@/components";
import { ConversionOffer } from "@/components/auth";
import { InlineScript, clearMirror, jsonLiteral } from "@/components/chrome";
import {
  addHolding,
  deleteHolding,
  getPortfolio,
  getSamplePortfolio,
  getStock,
  setClaim as setClaimRequest,
  updateHolding,
} from "@/lib/api";
import { SESSION_KEY, readSessionHoldings } from "@/lib/holding";
import {
  SAMPLE_KEY,
  clearSample,
  ensureSample,
  isRemoved,
  removeSampleHolding,
  restoreSampleHolding,
  setSampleClaim,
  setSampleShares,
  sharesOf as sampleSharesOf,
  useSample,
} from "@/lib/sample";
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
 * **샘플** (R5-4) — the payload is the anonymous `GET /portfolio/sample` (four
 * live filings, one per state, chosen per request since `P4.F1`), and the
 * reader's edits live in `localStorage` (`lib/sample.ts`): "편집 가능 +
 * localStorage 저장(로그인 불요, 재방문 유지)".
 *
 * **The served composition is always what renders**, and the store holds only
 * what the reader *did* to it — a 보유량 override, an explicit 삭제, a 챙긴 돈
 * mark, each keyed by `corp_code`. The rows, the factors and the D-days are still
 * the server's. Filtering the served rows *by* a stored list is what v1 did, and
 * with a live composition it renders an empty sample the day the issuers move
 * (`lib/sample.ts` § v2). **No anonymous write exists and none is attempted**
 * (`P5.S8` note 13).
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
  sampleServed = null,
  anonymous,
}: {
  payload: PortfolioPayload;
  mode: "account" | "sample";
  preselect: ResolvedStock | null;
  /** 계정 mode: today's served 샘플 composition, read by the **server** so this
   * client has the rows and their names at hydration and the pre-hydration mirror
   * can size 계정 이전's slot before anything paints (`P12.F3`). `null` — 샘플 mode,
   * or a read that failed — falls back to the client-side read this surface always
   * did. */
  sampleServed?: PortfolioHolding[] | null;
  /** 샘플 mode: the session as the server already resolved it, for the 전환 제안
   * band (`P12.F3`; the `P4.F10` shape). Undefined in 계정 mode, where the band
   * does not render at all. */
  anonymous?: boolean;
}) {
  const [busy, setWorking] = useState(false);

  // The served payload is the truth this surface starts from; a re-read after a
  // write replaces it wholesale (see `run`). A fresh server render — a
  // navigation, a reload — wins over whatever the last re-read left here.
  const [payload, setPayload] = useState(served);
  useEffect(() => setPayload(served), [served]);

  const sample = useSample();
  const local = mode === "sample" ? sample : null;

  // Entering the sample marks this browser as holding one — no composition is
  // copied into it (that is v1's bug: see `lib/sample.ts` § v2). The store stays
  // empty until the reader actually edits something, and R5-4's 이전 제안 and
  // 샘플 종료 still key on its existence.
  useEffect(() => {
    if (mode !== "sample") return;
    ensureSample();
  }, [mode]);

  /**
   * The **release** half of `P12.F10`'s pre-hydration hide.
   *
   * Until this runs, the rows this browser removed have no box because
   * `SampleRules.tsx`'s generated CSS hides everything the `<head>` script
   * stamped on `<html>` — which is what lets the hydrating render carry every
   * served row (as it must: `useSample()`'s server snapshot is `null`) without a
   * single pixel moving when the next render drops them.
   *
   * It may not run any earlier than this. `sample !== null` is the moment
   * `useSyncExternalStore` has answered from the store rather than from the
   * server snapshot, so the commit that filtered the lists has already landed and
   * the hidden rows are gone from the DOM — releasing then moves nothing. And it
   * may not run later than this either: 되돌리기 puts a removed issuer back into
   * `local`, and a stamp still standing would keep the restored row invisible.
   */
  useEffect(() => {
    if (mode !== "sample" || sample === null) return;
    clearMirror("sample-removed");
  }, [mode, sample]);

  // A row is shown unless this browser removed **that issuer**; an issuer the
  // browser has never seen renders on sight.
  const shown = useCallback(
    (corpCode: string) => !isRemoved(local, corpCode),
    [local],
  );

  const sharesFor = useCallback(
    (corpCode: string, served: number | null | undefined) =>
      sampleSharesOf(local, corpCode, served),
    [local],
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
      if (mode === "sample") {
        setSampleShares(row.corp_code, shares);
        return;
      }
      if (row.id === undefined) return;
      run(() => updateHolding(row.id as number, shares));
    },
    [mode, run],
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
      if (mode === "sample") {
        removeSampleHolding(row.corp_code);
        return;
      }
      if (row.id === undefined) return;
      run(() => deleteHolding(row.id as number));
    },
    [armUndo, mode, run],
  );

  const restoreHolding = useCallback(() => {
    if (!undo) return;
    const entry = undo;
    setUndo(null);
    if (undoTimer.current !== null) window.clearTimeout(undoTimer.current);
    if (mode === "sample") {
      restoreSampleHolding(entry.corp_code, entry.shares);
      return;
    }
    run(() => addHolding(entry.corp_code, entry.shares));
  }, [undo, mode, run]);

  const claim = useCallback(
    (row: RightsRow, claimed: boolean) => {
      const key = row.lapse?.performance_rcept_no;
      if (!key) return;
      if (mode === "sample") {
        setSampleClaim(key, claimed);
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

  // 계정 이전 (R5-4) needs the **sample's** composition, which is not this page's
  // payload in 계정 mode — the store no longer carries it either (`P4.F1`). Since
  // `P12.F3` the **server** reads it (`sampleServed`, see `app/portfolio/page.tsx`)
  // and this client merges this browser's own edits over it; the composition is the
  // same anonymous read as before, moved to the half of the app that can do it
  // before first paint.
  const hasSample = sample !== null;

  // The **fallback** path, and only that (`P12.F3`): the server reads today's
  // served composition now, so this fires solely when that read failed — in which
  // case the offer lands exactly the way it did before, a round trip after mount.
  const [refetched, setRefetched] = useState<PortfolioHolding[] | null>(null);
  useEffect(() => {
    if (mode !== "account" || !hasSample || sampleServed !== null) return;
    let live = true;
    void getSamplePortfolio()
      .then((page) => {
        if (live) setRefetched(page.holdings);
      })
      .catch(() => undefined);
    return () => {
      live = false;
    };
  }, [mode, hasSample, sampleServed]);

  const sampleRows = sampleServed ?? refetched;

  const sampleForCarry = useMemo(() => {
    if (mode !== "account" || sample === null || sampleRows === null) return NO_HOLDINGS;
    const rows = sampleRows
      .filter((row) => !isRemoved(sample, row.corp_code))
      .map((row) => ({
        corp_code: row.corp_code,
        // The name is **served with the row**, so 계정 이전 no longer spends a
        // `GET /stocks/{corp_code}` per candidate to spell a name the sample
        // payload already carries: the band can fill its reserved slot in the same
        // commit that reads the store, rather than a round trip later.
        corp_name: row.corp_name,
        shares: sampleSharesOf(sample, row.corp_code, row.shares) ?? row.shares,
      }));
    return rows.length > 0 ? rows : NO_HOLDINGS;
  }, [mode, sample, sampleRows]);

  const carry = useCarryOffer({
    mode,
    empty: holdings.length === 0,
    heldCorpCodes,
    // `NO_HOLDINGS` rather than a fresh `[]`: this value is a dependency two
    // levels down, and a new array identity on every render is a render loop
    // (see `useCarryOffer`).
    sampleCorpCodes: sampleForCarry,
    // The *variant* keys on whether this browser holds a sample at all, not on
    // the fetched rows: the composition arrives a round trip later, and the offer
    // must not spend that round trip pretending to be the 세션 이월 one.
    hasSample,
  });

  // The reservation is a **pre-hydration device**, exactly like `P12.F2`'s ≤767
  // launcher guard: once the band it held a place for has rendered — or once this
  // browser has said it does not want one — the stamp comes off, so that a later
  // 담지 않기 leaves no 195 px of reserved nothing behind. See `carry.settled` for
  // why it can never come off earlier than that.
  useEffect(() => {
    if (carry.settled) clearMirror("carry-rows", "carry-kind");
  }, [carry.settled]);

  /** What the mirror needs to size the slot, from the **server's** own knowledge:
   * the sample rows this account does not already hold, the codes it does, and
   * whether the served portfolio is empty (which is 세션 이월's own condition). The
   * browser supplies the rest — whether it holds a sample at all, which rows it
   * removed, and either 담지 않기 flag — and it supplies it in its own process. */
  const reservation = useMemo(
    () =>
      carryReservationCode({
        pool: (sampleServed ?? [])
          .map((row) => row.corp_code)
          .filter((code) => !heldCorpCodes.has(code)),
        held: [...heldCorpCodes],
        empty: holdings.length === 0,
      }),
    [sampleServed, heldCorpCodes, holdings.length],
  );

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

      {mode === "account" ? (
        <>
          {/* The band's **slot** (`P12.F3`). It is `display: contents` — so a
              filled slot lays the band out exactly as an unwrapped `<CarryOver>`
              did, and an empty one is not a grid item at all and takes not even a
              gap — until the script below tells the CSS how many rows are coming,
              which sizes the empty slot to the band's exact height before
              anything paints. What used to be *inserted* into a painted page
              (215.28 px of push, `P12.R1`'s worst shift) is now *filled* into a
              box that is already the right size. */}
          <div className={styles.carrySlot}>
            {carry.entries.length > 0 ? (
              <CarryOver
                variant={carry.variant}
                entries={carry.entries}
                busy={busy}
                onKeep={keepCarried}
                onDiscard={carry.dismiss}
              />
            ) : null}
          </div>
          {/* Parser-blocking, and **immediately after the slot**: it must run
              before the holdings below it are parsed, and it needs this page's own
              served composition beside it, which the `<head>` half of the mirror
              cannot have. It reads two named storage keys, computes a row count,
              and stamps it. Nothing is written, nothing is sent. */}
          <InlineScript code={reservation} />
        </>
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
      {/* `P12.F3`: `anonymous` is the server's own answer (a 401, or no cookie at
          all — and on `?sample=1` the session it resolved for this request), so
          the band is in the first painted HTML instead of arriving 53 ms after it
          in dev and 2.2 s into a cold mobile load. 세션당 1회 is still the
          browser's, still `sessionStorage`, still written by `markSeen()` at the
          same moment — read before first paint by the pre-hydration mirror. */}
      {mode === "sample" ? (
        <ConversionOffer
          ready={holdings.length > 0}
          lead={false}
          initialAnonymous={anonymous}
        />
      ) : null}
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
 *
 * `sampleCorpCodes` arrives **already merged** — today's served sample composition
 * with this browser's own overrides and removals applied (see the caller). The
 * offer is therefore about rows the reader would recognise from the sample, not
 * about a list the browser froze on some earlier visit.
 */
function useCarryOffer({
  mode,
  empty,
  heldCorpCodes,
  sampleCorpCodes,
  hasSample,
}: {
  mode: "account" | "sample";
  empty: boolean;
  heldCorpCodes: ReadonlySet<string>;
  sampleCorpCodes: ReadonlyArray<CarryCandidate>;
  hasSample: boolean;
}): {
  variant: "session" | "migrate";
  entries: CarryEntry[];
  dismiss: () => void;
  /** Whether the pre-hydration mirror's reservation may be released
   * (`P12.F3`). It flips **only** in a state where releasing cannot move
   * anything: the band has rendered into the slot (so the slot is no longer
   * empty and the reserved height no longer applies to it), or there is no band
   * to render because this browser declined it — in which case the mirror
   * stamped nothing either, having read the same flag. It deliberately does not
   * flip merely because the component mounted: between "mounted" and "the store
   * has been read" the reservation is the only thing holding the band's place. */
  settled: boolean;
} {
  const variant: "session" | "migrate" =
    mode === "account" && hasSample ? "migrate" : "session";

  const key = variant === "migrate" ? MIGRATE_FLAG : CARRY_FLAG;
  const candidates = useMemo(() => {
    if (mode !== "account") return NO_HOLDINGS;
    if (variant === "migrate") {
      return sampleCorpCodes.filter((row) => !heldCorpCodes.has(row.corp_code));
    }
    if (!empty) return NO_HOLDINGS;
    return Object.entries(readSessionHoldings().entries)
      .filter(([corpCode]) => !heldCorpCodes.has(corpCode))
      .map(([corp_code, shares]): CarryCandidate => ({ corp_code, shares }));
    // `heldCorpCodes` is a Set identity that changes with the payload, which is
    // exactly when this should be recomputed.
  }, [mode, variant, empty, heldCorpCodes, sampleCorpCodes]);

  /**
   * 담지 않기 is read **during render**, not in an effect (`P12.F3`), and that is
   * what lets 계정 이전 fill its reserved slot in the *same commit* that reads the
   * sample store instead of a tick later. It is safe against hydration for a
   * mechanical reason: on the server, and on the first client render, `useSample`
   * answers `null`, so `candidates` is empty and the guard short-circuits before
   * touching `sessionStorage` — server and client agree on "no band", which is
   * exactly what the server rendered. `dismissedNow` carries a dismissal taken in
   * this render session, whose flag write the memo above has no reason to see.
   */
  const [dismissedNow, setDismissedNow] = useState(false);
  const flagged = useMemo(() => candidates.length > 0 && readFlag(key), [candidates, key]);
  const dismissed = dismissedNow || flagged;

  // 세션 이월's names are the one thing not served with its rows: 조회's
  // `sessionStorage` keeps a `corp_code` and a count, so the names still come from
  // `GET /stocks/{corp_code}` a round trip later — now into a slot already the
  // right size. 계정 이전's names arrive with the composition (see the caller).
  const [named, setNamed] = useState<CarryEntry[]>(NO_ENTRIES);
  useEffect(() => {
    if (variant !== "session") return;
    let live = true;
    if (candidates.length === 0) {
      // Functional, and identity-preserving: `setNamed([])` would store a new
      // array every time this effect ran, and a state update that always
      // "changes" is a render loop waiting for a dependency to churn.
      setNamed((current) => (current.length === 0 ? current : NO_ENTRIES));
      return;
    }
    void Promise.all(
      candidates.map(async (row) => {
        const name = await getStock(row.corp_code)
          .then((page) => page.stock.corp_name)
          .catch(() => null);
        return { corp_code: row.corp_code, corp_name: name, shares: row.shares };
      }),
    ).then((rows) => {
      if (live) setNamed(rows);
    });
    return () => {
      live = false;
    };
  }, [candidates, variant]);

  const entries = useMemo(() => {
    if (dismissed) return NO_ENTRIES;
    if (variant !== "migrate") return named;
    return candidates.map((row) => ({
      corp_code: row.corp_code,
      corp_name: row.corp_name ?? null,
      shares: row.shares,
    }));
  }, [dismissed, variant, candidates, named]);

  return {
    variant,
    entries,
    settled: entries.length > 0 || dismissed,
    dismiss: () => {
      setDismissedNow(true);
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
const NO_HOLDINGS: ReadonlyArray<CarryCandidate> = [];
const NO_ENTRIES: CarryEntry[] = [];

/** A row 계정 이전 or 세션 이월 could carry into the account. `corp_name` is present
 * for the sample's rows (the composition serves it) and absent for 조회's
 * sessionStorage entries, which keep a code and a count and nothing else. */
type CarryCandidate = { corp_code: string; corp_name?: string | null; shares: number };

/** 담지 않기 is remembered for the tab, never for the account: the value stays in
 * the browser, and a new session may ask again. */
const CARRY_FLAG = "mijual.portfolio.carry";
const MIGRATE_FLAG = "mijual.portfolio.migrate";

/**
 * The 이월 · 이전 제안 band's half of the **pre-hydration mirror** (`P12.F3`) — the
 * one computation the `<head>` script cannot do, because it needs this page's own
 * served composition.
 *
 * It runs while the parser is still above the holdings, reads exactly the keys
 * `useCarryOffer` reads and applies exactly the rules `useCarryOffer` applies —
 * a sample that parses, minus the rows this browser removed, minus what the
 * account already holds; or 조회's session entries when the served portfolio is
 * empty; nothing at all under either 담지 않기 flag — and stamps the resulting row
 * count on `<html>` for `Portfolio.module.css` to size the slot from. The two must
 * agree, and they agree by construction: the pool and the held codes are the
 * server's, the store and the flags are the browser's, and neither side guesses at
 * the other's half.
 *
 * It **writes nothing, sends nothing and loads nothing.** `security.md`'s
 * 「anonymous state never reaches the server」 is why there is no cookie here: the
 * sample's edits and the dismissal flags stay in this browser and are read by this
 * browser, 12 lines before they are needed.
 */
function carryReservationCode(data: {
  pool: readonly string[];
  held: readonly string[];
  empty: boolean;
}): string {
  return (
    `(function(){try{` +
    `var D=${jsonLiteral(data)},h=document.documentElement,n=0,k="";` +
    `var raw=null;try{raw=localStorage.getItem(${jsonLiteral(SAMPLE_KEY)})}catch(e){return}` +
    // A store that does not parse is no store, which is what `readSample()` says.
    `var st=null;if(raw){try{var v=JSON.parse(raw);if(v&&typeof v==="object")st=v}catch(e){}}` +
    `if(st){` +
    `if(sessionStorage.getItem(${jsonLiteral(MIGRATE_FLAG)})!==null)return;` +
    `var rm=Array.isArray(st.removed)?st.removed:[];` +
    `n=D.pool.filter(function(c){return rm.indexOf(c)<0}).length;k="migrate"` +
    `}else if(D.empty){` +
    `if(sessionStorage.getItem(${jsonLiteral(CARRY_FLAG)})!==null)return;` +
    `var lk=null;try{lk=sessionStorage.getItem(${jsonLiteral(SESSION_KEY)})}catch(e){return}` +
    `if(!lk)return;var en={};try{en=(JSON.parse(lk)||{}).entries||{}}catch(e){return}` +
    `n=Object.keys(en).filter(function(c){return D.held.indexOf(c)<0}).length;k="session"` +
    `}` +
    `if(n>0){h.setAttribute("data-mj-carry-rows",String(n));` +
    `h.setAttribute("data-mj-carry-kind",k);` +
    `h.style.setProperty("--mj-carry-rows",String(n))}` +
    `}catch(e){}})();`
  );
}

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
