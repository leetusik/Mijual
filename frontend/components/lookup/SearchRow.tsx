"use client";

import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { suggestStocks } from "@/lib/api";
import { ROUTES, stockPath } from "@/lib/routes";
import type { StockSuggestion } from "@/lib/types";
import { SEARCH_PLACEHOLDER_KO, SEARCH_SUBMIT_KO } from "@/components/landing/copy";
import styles from "./SearchRow.module.css";

/** ~150 ms: long enough that a fast typist spends one request per word, short
 * enough that the list is there before the finger leaves the key. */
const DEBOUNCE_MS = 150;

export type SearchRowClassNames = {
  /** The surface's own form/row class — the 560px geometry stays its business. */
  form: string;
  /** The surface's own console input class (R2's dark field, or R4's). */
  input: string;
  /** The surface's own 조회 button class (`--live-solid`). */
  submit: string;
};

/**
 * The one search row — the landing hero's and R4's, the same component
 * (`P7.S4`, operator item 2).
 *
 * ## What it is, and why a candidate list does not break the product's rule
 *
 * `GET /stocks?q=` resolves **unique or declines**, and both its docstrings say
 * why: "a guess that opened a different company's 놓친 돈 is the one defect class
 * this product cannot ship". That rule is about the *system* picking silently. A
 * reader **choosing** 계양전기 out of a list is the opposite of a silent guess —
 * so the list exists, and what keeps it safe is the handle: every candidate
 * carries its `corp_code` and a chosen one is navigated to as
 * `/stocks/{corp_code}` (`stockPath`), never re-resolved from its name.
 *
 * **The form is still a plain GET.** With no candidates on screen, Enter submits
 * `?q=` to `/stocks` exactly as before — the four-tier resolver, the redirect
 * onto the handle on a hit, R4's locked 검색 불일치 sentence on a miss (an
 * ambiguous prefix included). The typeahead is an addition on top of a row that
 * works with JavaScript off, which is the property `P5.S12` and R4 §2 both state.
 *
 * ## Enter, in four steps (R9 §8, walk finding 11)
 *
 * Typing 「삼성」 offered 삼성에스디에스 and 삼성제약 and then a plain Enter threw
 * both away, landing on `/stocks?q=삼성`'s 「일치하는 종목이 없습니다」. R9's rule
 * keeps the offer without guessing which one is meant:
 *
 * 1. candidates open, **nothing highlighted** → Enter **selects the first**
 *    (no navigation, no submit — the same state as one ↓);
 * 2. something highlighted → Enter goes there (P7's rule, unchanged);
 * 3. the typed text is **exactly** a candidate's 종목명 or 종목코드 → the first
 *    Enter goes, because there is nothing to disambiguate;
 * 4. no candidates at all → the plain GET submit above.
 *
 * The rule lives here, in the one shared row, so the hero and R4's header cannot
 * drift apart — R11 owns what the `/stocks` **page** then says (its 불일치
 * sentence, its 조사, whether it lists prefix candidates of its own), and this
 * round touched none of it.
 *
 * ## The unsigned element, in the signed idiom
 *
 * No round draws a dropdown. So this one invents nothing: square (R1), a
 * hairline border, the surrounding console field's own colours (R2 §Cosmos in the
 * hero, R4's `--surface-inset` field on /stocks), a fade and nothing else, the
 * 종목코드 in mono beside the name in sans, 44px rows on mobile. **It mints no
 * Korean copy at all** — a candidate is its company's name and its ticker, the
 * list needs no heading, and an empty result renders *nothing* rather than a new
 * sentence (the submit already owns the 검색 불일치 line).
 *
 * ## Two dev-time traps this shape avoids (`P7.S1`/`P7.S2` findings)
 *
 * - **StrictMode double-invokes effects.** Every piece of state here is the
 *   component's, the effect's cleanup aborts its own request, and nothing is
 *   claimed in module scope — the shape that made the account slot render nothing
 *   in dev. The first run is also a no-op by construction: `typed` starts false,
 *   so mounting fires **no** request no matter how many times the effect runs.
 * - **One request per debounced keystroke, never a stale answer.** The timer and
 *   an `AbortController` are torn down together on every change of the query, so
 *   an in-flight suggestion for `계` cannot land after `계양`'s.
 */
export function SearchRow({
  label,
  defaultValue,
  variant,
  classNames,
}: {
  /** The surface's signed name — the input's label and the listbox's. */
  label: string;
  /** The query R4 keeps in the box so it can be edited rather than retyped. */
  defaultValue?: string;
  /** Which console field this row sits in; only the candidate list's ink. */
  variant: "hero" | "surface";
  classNames: SearchRowClassNames;
}) {
  const router = useRouter();
  const listboxId = useId();
  const [query, setQuery] = useState(defaultValue ?? "");
  const [candidates, setCandidates] = useState<StockSuggestion[]>([]);
  /** −1 = nothing highlighted. The list never pre-selects: the reader chooses. */
  const [active, setActive] = useState(-1);
  const [open, setOpen] = useState(false);
  /** No request until someone actually types — mounting must ask nothing. */
  const typed = useRef(false);

  useEffect(() => {
    const text = query.trim();
    if (!typed.current || text === "") {
      setCandidates([]);
      setActive(-1);
      return;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => {
      suggestStocks(text, { signal: controller.signal })
        .then((data) => {
          setCandidates(data.candidates);
          setActive(-1);
          setOpen(true);
        })
        // An aborted keystroke and an API that is not answering are both silence:
        // the surface's failure state is "no candidates", never an error message.
        .catch(() => undefined);
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  const shown = open && candidates.length > 0;
  const optionId = (index: number) => `${listboxId}-o${index}`;

  function choose(candidate: StockSuggestion) {
    setOpen(false);
    setActive(-1);
    // The exact handle, never the name that was typed. The box keeps its text so
    // the page a reader is leaving does not flicker into a different query.
    router.push(stockPath(candidate.corp_code));
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setOpen(false);
      setActive(-1);
      return;
    }
    if (event.key === "Enter") {
      // No candidates on screen → the plain GET submit, exactly as before, and
      // the JS-off path with it (R9 §8, rule 4).
      if (!shown) return;

      if (active >= 0) {
        // Something is highlighted → go there (P7's rule, unchanged; rule 2).
        event.preventDefault();
        choose(candidates[active]);
        return;
      }

      // Nothing highlighted. R9 §8 rule 3: an input that is *exactly* one of the
      // candidates is not ambiguous, so the first Enter goes — matching the name
      // as typed, or the 종목코드 case-insensitively (a ticker is a handle, not a
      // word). Otherwise rule 1: Enter **selects the first candidate** and goes
      // nowhere, which is the same state as one ↓. The hero never guesses, and it
      // never throws away the list it just offered (walk finding 11).
      event.preventDefault();
      const typedText = query.trim();
      const exact = candidates.find(
        (candidate) =>
          candidate.corp_name?.trim() === typedText ||
          candidate.stock_code?.toLowerCase() === typedText.toLowerCase() ||
          candidate.corp_code.toLowerCase() === typedText.toLowerCase(),
      );
      if (exact) {
        choose(exact);
        return;
      }
      setActive(0);
      return;
    }
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    if (candidates.length === 0) return;
    event.preventDefault();
    setOpen(true);
    setActive((current) => {
      const last = candidates.length - 1;
      if (event.key === "ArrowDown") return current >= last ? 0 : current + 1;
      return current <= 0 ? last : current - 1;
    });
  }

  return (
    // `suppressHydrationWarning` on the form and the input is not papering over
    // a mismatch of ours: password managers and mobile Chrome's autofill stamp
    // their own attributes (`__gchrome_uniqueid` and friends) onto every form
    // control *before* React hydrates, and React then reports the extension's
    // attribute as a server/client divergence. It suppresses one element deep,
    // so a real mismatch in anything nested here is still reported.
    <form
      className={classNames.form}
      action={ROUTES.stocks}
      method="get"
      role="search"
      suppressHydrationWarning
    >
      <span className={`${styles.field} ${variant === "hero" ? styles.hero : styles.surface}`}>
        <input
          suppressHydrationWarning
          className={classNames.input}
          type="text"
          name="q"
          value={query}
          onChange={(event) => {
            typed.current = true;
            setQuery(event.target.value);
            setOpen(true);
          }}
          onKeyDown={onKeyDown}
          onBlur={() => {
            setOpen(false);
            setActive(-1);
          }}
          aria-label={label}
          placeholder={SEARCH_PLACEHOLDER_KO}
          autoComplete="off"
          role="combobox"
          aria-expanded={shown}
          aria-controls={listboxId}
          aria-autocomplete="list"
          aria-activedescendant={shown && active >= 0 ? optionId(active) : undefined}
        />

        {shown ? (
          <ul className={styles.listbox} id={listboxId} role="listbox" aria-label={label}>
            {candidates.map((candidate, index) => (
              <li
                key={candidate.corp_code}
                id={optionId(index)}
                role="option"
                aria-selected={index === active}
                className={`${styles.option} ${index === active ? styles.active : ""}`}
                // The blur that a click would cause fires *before* the click, and
                // it closes the list. Keeping focus in the input is what makes a
                // tap on a candidate reach `choose` at all.
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => choose(candidate)}
                onMouseEnter={() => setActive(index)}
              >
                <span className={styles.name}>{candidate.corp_name ?? candidate.corp_code}</span>
                {candidate.stock_code ? (
                  <span className={`mono ${styles.code}`}>{candidate.stock_code}</span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : null}
      </span>

      <button className={classNames.submit} type="submit">
        {SEARCH_SUBMIT_KO}
      </button>
    </form>
  );
}
