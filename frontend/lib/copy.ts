/**
 * Every Korean string the trust primitives render, and where each one comes from.
 *
 * **Nothing here is invented.** Korean-only product surface is a constraint whose
 * other half is that *inventing a Korean string is a design change*, not an
 * implementation detail — copy is locked and comes from
 * `docs/reference/design/grounding/copy-inventory.md`, which is itself generated
 * from the code that emits it. So this module is a transcription with a citation
 * per line, and a string that has no citation does not belong in it.
 *
 * Strings that belong to a *surface* rather than to a primitive (the hero, the
 * footer's provenance sentence, the ② 진행 중 strip, R4's 검색 불일치 line …) are
 * that surface's slice to transcribe — `P5.S11`–`P5.S17`. This file holds only
 * what the seven R1/R2 primitives need.
 */

/** 추후결정 — the whole rendered vocabulary for a `tbd` field.
 *
 * Source: `mijual.gates.exposure.TBD_DISPLAY_KO`, served in every field payload
 * as `display`. `ui-traps.md` #4: it means *no date*, not an unknown one — the
 * badge never appears beside a date, and the superseded date it replaced is
 * structurally absent from the contract and cannot leak. */
export const TBD_DISPLAY_KO = "추후결정";

/** 철회 — the locked notice per rights type, replacing the card body.
 *
 * Source: `mijual.gates.exposure.WITHDRAWN_NOTICE_KO`, byte-identical; it also
 * arrives on a withdrawn event's payload as `notice_ko`, which is the copy the
 * surface should prefer when it has one. Verified against `copy-inventory.md`
 * §State notices. */
export const WITHDRAWN_NOTICE_KO: Record<RightsType, string> = {
  R1: "이 유상증자는 철회되었습니다",
  R2: "이 사채 발행은 철회되었습니다",
  R3: "이 합병은 철회되었습니다",
};

/** 발행사 기재 불일치 — the locked literal.
 *
 * Source: `mijual.present.money.MISMATCH_LABEL_KO` / `ui-traps.md` #2. It states
 * that *the issuer's filing contradicts itself*; it must never be phrased so a
 * reader thinks 미주알 made the mistake, and the two readings are never
 * reconciled. */
export const MISMATCH_LABEL_KO = "발행사 기재 불일치";

/** The system-wide estimate mark's text.
 *
 * Source: R3's build prompt, §Estimate mark — "`EstimateMarker` is the ONLY
 * estimate mark: value + bordered 「추정」 tag". The 「」 are the design record's
 * own quoting notation (the same brackets wrap 「예정」, 「진행 중」 and whole
 * sentences elsewhere in these documents); the *border* is the enclosure the
 * round specifies, so the rendered text is the two characters. */
export const ESTIMATE_TAG_KO = "추정";

/** The per-field citation chip.
 *
 * Source: R1's build prompt — "per-field `[근거]` chip (mono 11, `--live`, dotted
 * underline)". Here the brackets **are** part of the string: the chip has no
 * border, and the record writes it in square brackets every time. */
export const CITATION_CHIP_KO = "[근거]";

/** The 소멸주의보 sub-brand badge (R1 `brand/Subbrand.html`, kept by R2). */
export const LAPSE_ALERT_KO = "소멸주의보";

/** The timezone suffix under a D-day.
 *
 * Source: R1's build prompt — "date below in mono 11 `--ink-3` + \"KST\"". Every
 * date and D-day in this product is computed upstream in Asia/Seoul; the suffix
 * is what says so on the surface. */
export const KST_KO = "KST";

/** The three rights types, as the product names them. */
export type RightsType = "R1" | "R2" | "R3";

/** RightsChip's full labels — R2's board tabs, and `copy-inventory.md`
 * §Product terminology. **No ①②③ numbering in the UI** (R1 revision). */
export const RIGHTS_LABEL_KO: Record<RightsType, string> = {
  R1: "유상증자 신주인수권",
  R2: "전환사채 오버행",
  R3: "주식매수청구권",
};

/** RightsChip's `compact` labels — R1's build prompt ("유증 / CB / 매수청구"),
 * which R2 reuses for the mobile tab strip. */
export const RIGHTS_LABEL_COMPACT_KO: Record<RightsType, string> = {
  R1: "유증",
  R2: "CB",
  R3: "매수청구",
};
