# Deferred Jobs

> Generated dashboard. Do not put detailed deferred context here; edit each `works/deferred/<state>/<DID>/` folder instead.

## Summary

- Open: `25`
- Promoted: `2`
- Dropped: `0`

## Open

| ID | Status | Title | Source | Trigger | Path |
|---|---|---|---|---|---|
| `D10` | `deferred` | Serve the ① 구주주 청약 / 일반공모 windows and the 결의일 on the stock route (Q29b + Q31b) | P8.REVIEW | If a later round wants the designed lines, rather than dropping them from the record | `works/deferred/open/D10` |
| `D11` | `deferred` | Serve the 집계 범위 dates on a stockless read (Q32b) | P8.REVIEW | When the entry page should date its own boundary | `works/deferred/open/D11` |
| `D12` | `deferred` | Density round for the ② row and the 놓친 돈 breakdown at 390 (Q34b) | P8.REVIEW | When mobile scroll length on 조회 becomes a complaint | `works/deferred/open/D12` |
| `D13` | `deferred` | Regenerate board-snapshot.md with the top 진행 중 rows and every 추후결정 name (Q13) | P8.REVIEW | Before the next design round that needs the board strips | `works/deferred/open/D13` |
| `D14` | `deferred` | Teach export_design_grounding.py to read the frontend copy.ts, or protect the hand-written tails | P8.REVIEW | Before anyone regenerates the grounding pack | `works/deferred/open/D14` |
| `D15` | `deferred` | Take the R7 implementation rules off the /ops door | P8.REVIEW | Before P4 Ship & Submit, or whenever D6 is promoted | `works/deferred/open/D15` |
| `D16` | `deferred` | 운영 대화 로그에 저장된 구조화 블록을 보여줄지 결정 | P9.REVIEW | When 품질 점검 needs to read a calculation, or a 대화 로그 design round opens. | `works/deferred/open/D16` |
| `D17` | `deferred` | 대화 로그가 「미확인」 hedge를 보존해야 하는지 결정 | P9.REVIEW | Same as the stored-blocks decision: 품질 점검 need or a 대화 로그 design round. | `works/deferred/open/D17` |
| `D18` | `deferred` | ▷ 추정 계산을 독자에게 노출할지 결정 | P9.REVIEW | When 「내 증서는 얼마어치인가」 is wanted in the assistant. | `works/deferred/open/D18` |
| `D19` | `deferred` | 보안 가드 로그의 보관·마스킹 정책을 정한다 | P9.REVIEW | Before deploy (P4), or the first time the guard fires in production. | `works/deferred/open/D19` |
| `D2` | `deferred` | De-duplication pass for hint_duplicate versions and hint_split_evidence collided event keys | P2.S3 | if P2.S8 corpus work or P3 event pages trip over them | `works/deferred/open/D2` |
| `D20` | `deferred` | 마커 기하 두 표기의 불일치를 정리한다 | P9.REVIEW | A design round that touches the 추정 tag. | `works/deferred/open/D20` |
| `D21` | `deferred` | 계산 error 블록이 실제로는 도달 불가능한 문제 | P9.REVIEW | If a reader reports a stuck calculation, or when the prompt is next revised. | `works/deferred/open/D21` |
| `D22` | `deferred` | 암시적 프롬프트 캐시가 한 번도 적립되지 않는 이유를 조사 | P9.REVIEW | When per-turn cost matters, or before deploy. | `works/deferred/open/D22` |
| `D23` | `deferred` | P4 mail subject still carries the retired name [미주알] | P10.DECOMP | When P4 implements the 마감 임박 mail, before the first send | `works/deferred/open/D23` |
| `D24` | `deferred` | /ops has no 390px layout — the whole bar stacks, not just the mark | P10.S5 | Next ops design pass, or the first time /ops is needed from a phone | `works/deferred/open/D24` |
| `D25` | `deferred` | Code comments and dev-tooling banners still name the retired product | P10.REVIEW | Next time a slice edits those files anyway, or if the identifier rename is ever taken on | `works/deferred/open/D25` |
| `D26` | `deferred` | The AI 질문 launcher's open state is covered by the widget and can never be seen | P10.REVIEW | The next design round that opens the AI 질문 surface, or the next time the launcher's state table is edited | `works/deferred/open/D26` |
| `D27` | `deferred` | /ops/feedback overflows horizontally at 1280 — the desktop half of the ops layout gap | P10.REVIEW | Whenever D24 is picked up, or the first time the operator needs the feedback tab on a 1280 screen | `works/deferred/open/D27` |
| `D3` | `deferred` | Backfill pifricDecsn (유무상증자결정) history pre-2026, mirroring the P2.S7 CB backfill | P2.S8 | if P2.S9 sampling or P3 retrospective views need pre-2026 ① depth | `works/deferred/open/D3` |
| `D5` | `deferred` | Favicon + per-route <title>/meta for the reader chrome | P8.S2 | when the operator wants the tab/branding polish, or before P4 Ship & Submit | `works/deferred/open/D5` |
| `D6` | `deferred` | R15 admin /ops polish round (surface 8) — dropped from P8 by operator | P8.S16 | Operator asks to polish 운영 관제 / revisit any Q59-Q65 item | `works/deferred/open/D6` |
| `D7` | `deferred` | Make the notification_pref save an upsert (Q49) | P8.REVIEW | Before P4 Ship & Submit, or the moment any second client can save preferences | `works/deferred/open/D7` |
| `D8` | `deferred` | Strip the // eyebrow from the accessible name on 조회 and 보유 종목 (Q21) | P8.REVIEW | Each surface next round, or as one small cross-surface job before P4 | `works/deferred/open/D8` |
| `D9` | `deferred` | Carry the ③ 반대의사 통지 procedure fields onto GET /stocks/{corp_code} (Q30b) | P8.REVIEW | When 조회 and 상세 disagreeing about the same filing becomes a reported problem | `works/deferred/open/D9` |

## Promoted

| ID | Status | Title | Promoted To | Path |
|---|---|---|---|---|
| `D1` | `promoted` | Identity-scope the API-backed gates: re-pair 정정 filings joined to the wrong 사채/이벤트 | `P5.S5` | `works/deferred/promoted/D1` |
| `D4` | `promoted` | Multi-span citations for multi-addend 실적보고서 figures | `P5.S20` | `works/deferred/promoted/D4` |

## Dropped

| ID | Status | Title | Reason | Path |
|---|---|---|---|---|
| - | - | - | - | - |
