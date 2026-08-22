# Intent — P7

- Captured at: 2026-08-23T06:17:28+09:00
- Origin: operator

## Original Input (verbatim)

> just p5 and p6 done but no login exists, 의견 doesn't work, /ask doesn't work, total messed up right now. fix theses:
>
> 1. remove "내 종목 조회" nav. on the 관제 현황판 only enough.
> 2. 내 종목 조회 search shows list of related ones when a user type the text on the input. before the submit.
> 3. when 내 종목 조회 input box selected, the focusing blue box just annoying. and its right side covered by 조회 box. just remove it. and no selected focus on all the input boxes.
> 4. the 관제 현황판 list should be show some amount of firms not by all at onces. and "전환청구 진행 중 — 개시일이 지나 지금 전환할 수 있는 전환사채 60건
> 펼치기일정 추후결정 — 카운트다운 없이 감시 중인 이벤트 4건
> 펼치기" these does nothing. 펼치기 got no meaning, no work.
> 5. login should be exists
> 6. the count down just stopped and refreshed only when the page is reloaded.
> 7. auto reload just refresh everything. even when I'm typing something, just refresh the whole thing. we shoudn't do like that.
> 8. AI 질문 jsut doesn't work on the dev. can't send anything.
> 9. sample portfolio page just look not organized. and "청약·매도로 챙겼습니다" clicked, should 놓친돈 stuff gone or smth.
> 10. "본인 표시 · 이 브라우저(localStorage)에" this kind of descriptive bullshits everywhere. remove this kind of things.
>
> +
> 11. no widget even exists.

## Confirmed Intent (refined + clarified)

P5 (web build) and P6 (AI 질문 agent) are marked done, but the running product is broken or rough in 11 confirmed ways. One fix-pass phase, ordered **before P4 (Ship & Submit)**, fixes all of them. Every fix is checked against the signed P3 design (RESPECT THE DESIGN — double-check everything; no freelance restyling) and verified in a real browser on the running dev stack.

1. **Nav cleanup:** remove the "내 종목 조회" item from the global nav — that surface lives on the 관제 현황판 (landing) only.
2. **Search typeahead:** 내 종목 조회 search shows matching stocks as the user types, before submit.
3. **Focus rings:** remove the blue focus outline on the 내 종목 조회 input (its right side is clipped by the 조회 button) — and remove the selected-focus outline on all input boxes.
4. **Board pagination + dead toggles:** the 관제 현황판 firm list shows a limited amount at a time instead of everything at once; the "펼치기" toggles on the section headers ("전환청구 진행 중 … 60건", "일정 추후결정 … 4건") currently do nothing — make them actually work.
5. **Login:** the auth code exists (`frontend/app/auth/login/page.tsx`, `Nav.tsx`/`AccountSlot.tsx` reference 로그인) but login is not visible/reachable/working on the dev site. Investigate why and make login genuinely reachable and functional.
6. **Live countdowns:** countdowns are static and only update on page reload — they must tick live.
7. **Non-destructive refresh:** auto-refresh replaces the whole page state and wipes in-progress typing — refresh data without stomping user input/state.
8. **AI 질문 send broken:** on dev, nothing can be sent — 의견 (feedback) and /ask don't work. Fix end to end.
9. **Sample portfolio:** the page looks disorganized — tidy it (checked against the design); and clicking "청약·매도로 챙겼습니다" must actually affect the 놓친 돈 display (e.g. the entry clears/moves).
10. **Self-narrating copy:** remove implementation-detail copy like "본인 표시 · 이 브라우저(localStorage)에…" wherever this pattern appears.
11. **Missing widget:** the AI 질문 widget doesn't render at all — fix.

## Clarifications Resolved

- Q: One phase or split (login is the largest chunk)? — A: One phase.
- Q: Items 3/9/10 change the approved P3 design — design round or direct fixes? — A: "respect the design, double check everything" — no new design round; verify every fix against the signed design.
- Q: Where relative to P4 (Ship & Submit)? — A: Before P4 (phase order 3.5).
- Q: Scope of "login should be exists"? — A: "not even seen in the web. you look up." — Claude checked: the auth pages and nav account slot exist in code but don't appear/work on the running site; investigate and fix.

## Notes

- Operator's framing: "total messed up right now" — the phase is about making the already-built product actually work, not new features.
