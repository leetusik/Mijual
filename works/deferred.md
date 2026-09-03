# Deferred Jobs

> Generated dashboard. Do not put detailed deferred context here; edit each `works/deferred/<state>/<DID>/` folder instead.

## Summary

- Open: `36`
- Promoted: `6`
- Dropped: `3`

## Open

| ID | Status | Title | Source | Trigger | Path |
|---|---|---|---|---|---|
| `D10` | `deferred` | Serve the ① 구주주 청약 / 일반공모 windows and the 결의일 on the stock route (Q29b + Q31b) | P8.REVIEW | If a later round wants the designed lines, rather than dropping them from the record | `works/deferred/open/D10` |
| `D11` | `deferred` | Serve the 집계 범위 dates on a stockless read (Q32b) | P8.REVIEW | When the entry page should date its own boundary | `works/deferred/open/D11` |
| `D12` | `deferred` | Density round for the ② row and the 놓친 돈 breakdown at 390 (Q34b) | P8.REVIEW | When mobile scroll length on 조회 becomes a complaint | `works/deferred/open/D12` |
| `D13` | `deferred` | Regenerate board-snapshot.md with the top 진행 중 rows and every 추후결정 name (Q13) | P8.REVIEW | Before the next design round that needs the board strips | `works/deferred/open/D13` |
| `D14` | `deferred` | Teach export_design_grounding.py to read the frontend copy.ts, or protect the hand-written tails | P8.REVIEW | Before anyone regenerates the grounding pack | `works/deferred/open/D14` |
| `D16` | `deferred` | 운영 대화 로그에 저장된 구조화 블록을 보여줄지 결정 | P9.REVIEW | When 품질 점검 needs to read a calculation, or a 대화 로그 design round opens. | `works/deferred/open/D16` |
| `D17` | `deferred` | 대화 로그가 「미확인」 hedge를 보존해야 하는지 결정 | P9.REVIEW | Same as the stored-blocks decision: 품질 점검 need or a 대화 로그 design round. | `works/deferred/open/D17` |
| `D18` | `deferred` | ▷ 추정 계산을 독자에게 노출할지 결정 | P9.REVIEW | When 「내 증서는 얼마어치인가」 is wanted in the assistant. | `works/deferred/open/D18` |
| `D19` | `deferred` | 보안 가드 로그의 보관·마스킹 정책을 정한다 | P9.REVIEW | Before deploy (P4), or the first time the guard fires in production. | `works/deferred/open/D19` |
| `D2` | `deferred` | De-duplication pass for hint_duplicate versions and hint_split_evidence collided event keys | P2.S3 | if P2.S8 corpus work or P3 event pages trip over them | `works/deferred/open/D2` |
| `D20` | `deferred` | 마커 기하 두 표기의 불일치를 정리한다 | P9.REVIEW | A design round that touches the 추정 tag. | `works/deferred/open/D20` |
| `D21` | `deferred` | 계산 error 블록이 실제로는 도달 불가능한 문제 | P9.REVIEW | If a reader reports a stuck calculation, or when the prompt is next revised. | `works/deferred/open/D21` |
| `D22` | `deferred` | 암시적 프롬프트 캐시가 한 번도 적립되지 않는 이유를 조사 | P9.REVIEW | When per-turn cost matters, or before deploy. | `works/deferred/open/D22` |
| `D24` | `deferred` | /ops has no 390px layout — the whole bar stacks, not just the mark | P10.S5 | Next ops design pass, or the first time /ops is needed from a phone | `works/deferred/open/D24` |
| `D25` | `deferred` | Code comments and dev-tooling banners still name the retired product | P10.REVIEW | Next time a slice edits those files anyway, or if the identifier rename is ever taken on | `works/deferred/open/D25` |
| `D26` | `deferred` | The AI 질문 launcher's open state is covered by the widget and can never be seen | P10.REVIEW | The next design round that opens the AI 질문 surface, or the next time the launcher's state table is edited | `works/deferred/open/D26` |
| `D27` | `deferred` | /ops/feedback overflows horizontally at 1280 — the desktop half of the ops layout gap | P10.REVIEW | Whenever D24 is picked up, or the first time the operator needs the feedback tab on a 1280 screen | `works/deferred/open/D27` |
| `D3` | `deferred` | Backfill pifricDecsn (유무상증자결정) history pre-2026, mirroring the P2.S7 CB backfill | P2.S8 | if P2.S9 sampling or P3 retrospective views need pre-2026 ① depth | `works/deferred/open/D3` |
| `D30` | `deferred` | 푸터 「AI 질문」 링크가 390에서 40 × 44 | P11.REVIEW | The next mobile-target pass | `works/deferred/open/D30` |
| `D31` | `deferred` | 푸터 전화번호가 600-620px에서 두 줄로 끊긴다 | P11.REVIEW | Next footer/chrome work, or before the P4 demo video | `works/deferred/open/D31` |
| `D32` | `deferred` | API가 죽으면 랜딩(/)이 500 — 영문 오류 화면 | P11.REVIEW | Next landing work, or P4 deployment hardening | `works/deferred/open/D32` |
| `D33` | `deferred` | tests/test_web_site.py가 운영자의 실제 이메일·전화를 고정한다 | P11.REVIEW | The operator's answer to gate decision 4 | `works/deferred/open/D33` |
| `D35` | `deferred` | 동적 세그먼트의 404는 SSR 없이 클라이언트에서만 그려진다 | P11.F3 | Next 404/error-surface work, or P4 deployment hardening | `works/deferred/open/D35` |
| `D36` | `deferred` | 인용 팝오버가 아랫줄 칩들을 덮는다 | P11.REVIEW | The next AI 질문 design round, or an operator complaint after the P4 demo | `works/deferred/open/D36` |
| `D37` | `deferred` | 404가 한글 주소를 퍼센트 인코딩된 채로 보여준다 | P11.REVIEW | The next 404/error-surface work (natural pair with D35), or before the P4 demo | `works/deferred/open/D37` |
| `D38` | `deferred` | 답변 푸터가 근거 5건 중 3건만 링크한다 | P11.REVIEW | The next AI 질문 answer-footer work | `works/deferred/open/D38` |
| `D39` | `deferred` | 404 라우트에만 폰트 preload 링크가 없다 | P11.REVIEW | The next font or 404 work, or any Next upgrade | `works/deferred/open/D39` |
| `D40` | `deferred` | Decide the 정정 해석 thinking preset (D-4) | P4.REVIEW | The first production run whose extract stage hits the call ceiling, or before any backfill. | `works/deferred/open/D40` |
| `D41` | `deferred` | Harden what the public repo publishes (box IP/user/paths in deploy/**, the operator's alert address in works/**) | P4.REVIEW | Before the URL is circulated beyond the judges, or immediately if the repo stays public after the contest. | `works/deferred/open/D41` |
| `D42` | `deferred` | Settle the harness's production boundary (ssh oracle-cloud reads, docker compose over ssh, .env.prod credential read) | P4.REVIEW | The next slice that needs box inspection or an /ops login. | `works/deferred/open/D42` |
| `D43` | `deferred` | This Mac's MagicDNS answer for www.jujutower.com (false-red make smoke-prod www line) | P4.REVIEW | The next red www line — check dig @1.1.1.1 before believing it; fix the local resolver or split-DNS. | `works/deferred/open/D43` |
| `D44` | `deferred` | board 자동 갱신 re-downloads the whole board every 60 s per open tab (no ETag/304, no delta endpoint) | P4.R1 | When concurrent readers or egress start to matter, or when a 정정 makes a delta endpoint worth having anyway | `works/deferred/open/D44` |
| `D45` | `deferred` | Measure Malgun Gothic's Hangul advance and close the Windows half of the font fallback | P4.REVIEW | The next time a Windows machine is available, or the first Windows-sourced report of a cold-cache re-wrap | `works/deferred/open/D45` |
| `D6` | `deferred` | R15 admin /ops polish round (surface 8) — dropped from P8 by operator | P8.S16 | Operator asks to polish 운영 관제 / revisit any Q59-Q65 item | `works/deferred/open/D6` |
| `D8` | `deferred` | Strip the // eyebrow from the accessible name on 조회 and 보유 종목 (Q21) | P8.REVIEW | Each surface next round, or as one small cross-surface job before P4 | `works/deferred/open/D8` |
| `D9` | `deferred` | Carry the ③ 반대의사 통지 procedure fields onto GET /stocks/{corp_code} (Q30b) | P8.REVIEW | When 조회 and 상세 disagreeing about the same filing becomes a reported problem | `works/deferred/open/D9` |

## Promoted

| ID | Status | Title | Promoted To | Path |
|---|---|---|---|---|
| `D1` | `promoted` | Identity-scope the API-backed gates: re-pair 정정 filings joined to the wrong 사채/이벤트 | `P5.S5` | `works/deferred/promoted/D1` |
| `D15` | `promoted` | Take the R7 implementation rules off the /ops door | `P4.S4` | `works/deferred/promoted/D15` |
| `D28` | `promoted` | 시작 카드의 회사가 늙는다 — a data-derived start-card set | `P11.F1` | `works/deferred/promoted/D28` |
| `D4` | `promoted` | Multi-span citations for multi-addend 실적보고서 figures | `P5.S20` | `works/deferred/promoted/D4` |
| `D5` | `promoted` | Favicon + per-route <title>/meta for the reader chrome | `P4.S5` | `works/deferred/promoted/D5` |
| `D7` | `promoted` | Make the notification_pref save an upsert (Q49) | `P4.S2` | `works/deferred/promoted/D7` |

## Dropped

| ID | Status | Title | Reason | Path |
|---|---|---|---|---|
| `D23` | `dropped` | P4 mail subject still carries the retired name [미주알] | Resolved by operator decision (intent.md, 2026-09-02): P4.S2 re-signed the mail subject to [주주의관제탑] {종목} — {마감명} {D-표기} ({date}); 미주알 appears nowhere in the mail layer | `works/deferred/dropped/D23` |
| `D29` | `dropped` | 의견 카드가 다른 카드와 구별되지 않는다 | Superseded by P11.F1: the 의견 card is removed from the start screen at the operator's gate rejection, so a card that files a row in the reader's name no longer exists to be indistinguishable from the others. | `works/deferred/dropped/D29` |
| `D34` | `dropped` | 프로덕션에서 React #418 하이드레이션 불일치가 한 번 관측됨 | Cause found and fixed at P11.F3. The production #418(text) was /_not-found being prerendered while RequestedPath renders usePathname(): reproducible 5/5 on a 404 route before the fix, 0 across 58 loads over 13 route/viewport combinations after. D34's single sighting came from a multi-route sweep that did not record which URL was in flight, so this cannot be proven to be that sighting — but the signature matches exactly and no other #418 source survives. Re-file if a third sighting appears. | `works/deferred/dropped/D34` |
