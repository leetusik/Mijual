# P4.S8 — result

- **status:** `done`
- **summary:** 첨부2 기능명세서 written (five Korean 양식 headings verbatim, English body, Korean
  product strings, ~7.9k words → 16 A4 pages) and rendered to PDF beside 첨부1; §1–§4 describe
  production as it runs on 2026-09-02, and §5 is a judge-executable script whose seven anonymous
  blocks were executed once by this slice against `https://jujutower.com` in real Chrome at 1280 and
  390 (one AI 질문, one model call), with the account-bound blocks marked 운영자 검증 항목.
- **files_changed:**
  - `docs/reference/challenge/submission/drafts/02_기능명세서.md` (new, 601 lines / 53.7 KB)
  - `docs/reference/challenge/submission/drafts/02_기능명세서.pdf` (new, 16 pages, 1,013,532 B)
  - `works/phases/active/P4/phase.md` (notebook edit)
  - `works/phases/active/P4/slices/P4.S8/result.md` (this file)
- **validation:**
  | command / check | result |
  |---|---|
  | five `##` headings byte-identical to the README extraction, in order, no sixth | **PASS** (5/5 exact) |
  | `grep -ci` 미주알 · mijual · 파인튜닝 · fine-tun · PyTorch · Hugging Face | **0 / 0 / 0 / 0 / 0 / 0** |
  | every §5 URL curled (14 GETs + 2 redirects) | **PASS** — all as written |
  | §5 anonymous blocks V1–V7 executed in real Chrome 152 at 1280 **and** 390 | **PASS** (log below) |
  | §5 V8 (redirects, robots, sitemap, health) by direct HTTP request | **PASS** |
  | `python3 scripts/render_submission_pdf.py <in> <out>` + PDF pages opened | **PASS** — Korean renders, tables intact, §5 blocks readable |
  | `make smoke-prod` | **16 pass · 1 fail** — the `www` FAIL is this Mac's resolver, not production (known `## Operator Questions` entry); re-checked green with `--resolve` |
  | `python3 scripts/workflow.py validate` | **PASS** (pre-existing `oversized_doc_sections=11` warning only) |
- **deviations:** three, all small — see *Deviations* below.
- **doc_impact:** one line appended to `phase.md` (`product` / `security` — the agent declares
  **seven** tools, not five).
- **doc_versions:** n/a
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a

---

## What was written, and why it is shaped this way

The document is the **specification of what is deployed**, deliberately carrying none of 첨부1's
argument. Structure and discipline are modelled on the landed `01_공모전기획서.md`: the same header
table (팀명 주주의관제탑 · 구성원 성명 `〈제출자 직접 기재〉 — 개인(1인) 참가`), an "On this document"
note, the `[근거]` / `▷` convention, and a closing provenance line. Two rules were added because this
document is about a **live** service rather than a stored corpus:

1. **Every live figure is a dated snapshot**, stated as such in the header note and repeated at each
   figure (`2026-09-02 18:00 KST`).
2. **§5 is written by observable state, never by 종목.** This is the `P4.F1` note's demand and it is
   load-bearing: the board, the 샘플 포트폴리오's four rows and two of the four AI 질문 cards all pick
   today's companies, so a judge running the script during 09-07 → 09-11 will see different names.
   Each block therefore says "an ① whose 발행가 is not yet fixed, counting down" and then gives the
   2026-09-02 reading as a clearly-marked *dated example*. `## Operator Questions` asked whether to
   accept that or pin the example; this document does **both** — state first, dated example second —
   which is the only shape that stays true after the freeze.

Other shaping decisions worth carrying:

- **§1.4 names the exclusions out loud** (카카오톡 · 마이데이터/계좌연동/거래 · MCP 서버 · EB·분할합병 ·
  가격 피드 · `/ops` as 심사 대상 아님), because the 양식's rule (미구현·향후 기능은 제외) only helps a
  judge if they know *not to look*.
- **§2 has no 「부분 구현」 row.** Every row is 구현 완료 · 배포됨; anything partial went to §1.4.
- **The mail is described as 「deployed and transport-proven」, never as demonstrated** (§5.5 states
  the distinction explicitly), per the `P4.S4` note — the transport sent a real password-reset mail
  from production on 2026-09-02, and the deadline mail has still never reached a reader from the box
  because no production account holds a 7/3/1/0-day deadline.
- **98.6 % appears exactly once**, in §5.8 item 8, with the cross-model caveat in the same sentence.
- **409, not 418.** 첨부1 used 409 (the gate *run* report); `qa.md` line 98 records **418** from the
  *exposure summary*, a wider definition. §4.1 quotes 409 and names both in the `[근거]` so the two
  numbers can never look like a contradiction.
- **No package identifier appears in prose.** The first draft cited the gate command by module path,
  which put the string `mijual` (the romanisation of the retired name) into a submission document.
  It was replaced with a description of the command; the grep is now 0.

## §5 execution log — 2026-09-02, expected vs observed

**Instrument.** Real **Google Chrome 152 over the DevTools protocol, headful**, exactly as
`## Operator Runtime` (the production line `P4.S4` recorded) prescribes: **Aside is unavailable on
this Mac** (daemon down, no agent account), so the manifest's own P11 fallback was used — launched
through LaunchServices on a **fresh port (9451)** with a **throwaway profile** in the session
scratchpad (`open -na "Google Chrome" --args --remote-debugging-port=9451 --user-data-dir=<scratch>`),
driven from a small `websockets` CDP client with `Emulation.setDeviceMetricsOverride`, real
`Input.dispatchMouseEvent` / `insertText` for every interaction. **The operator's own Chrome profile
was never touched**, and the instance was terminated afterwards (`pgrep` clean).
**Runtime:** `https://jujutower.com` through Cloudflare → `edge-nginx` → the `mijual-web` container,
which *is* the production build — the manifest's "no dev/production pair to check twice" applies.
**Viewports: 1280 and 390** (every block run at both).

| Block | Expected (as §5 writes it) | Observed |
|---|---|---|
| **V1 관제 현황판** | headline + 「추정」 tag, 밴드 하한, 감시 중/30일 이내 summary, 소멸주의보 sentence over a ticking counter, four tabs with whole-board counts, ranked D-표기 rows, 「N건 더 보기」 | **as written.** ▷ 718.1억원 · 밴드 하한 ▷ 548.7억원 · 감시 중 445건 · 30일 이내 마감 40건 · 소멸 앞둔 15건; 「가장 빠른 청약 마감 2026-09-04, 3개 종목」; counter ticking (`2일 05:46:26` → `…:46:08` across two reads); tabs 전체 445 / 유증 12 / CB 422 / 매수청구 11; 「15건 더 보기 · 남은 360건」 |
| **V2 내 종목 조회 + 환산** | suggestion carries 종목코드; 500주 → 배정 신주 with printed arithmetic, 초과청약 한도, 「서버 전송 없음」, 발행가 확정 전 with no money | **as written.** typing 「툴젠」 → suggestion 「툴젠 199800」 → `/stocks/00547510`, title 「툴젠 \| 주주의관제탑」; 500주 → 「배정 신주 43주」, 「= 500주 × 0.0863800841 · 1주 미만 버림」, 「초과청약 한도 +8주」, 「발행가 확정 전 · 확정 예정 2026-09-11」 |
| **V3 2026년 놓친 돈** | market-wide 발행−청약=소멸 derivation, then the reader's ▷ amount with a 하한 and the derivation, 「추정」 everywhere, 집계 범위 note | **as written** (페니트리움바이오, 500주): 「발행 8,478,636주 − 청약 7,142,080주 = 소멸 1,336,556주 (15.76%) · 13.7억원추정」, 「79,182원추정」 (하한 68,546원추정), 「배정 77주 × 1,028원추정」 |
| **V4 이벤트 상세 + 원문 인용** | title 「{종목} — {마감명}」, 접수번호/최초 공시/정정 반영, `[근거]` opens the **verbatim span** | **as written.** 4 `[근거]` buttons on the page; pressing one opened 「▶ 확정 발행가액 = MAX【MIN(1차 발행가액, 2차 발행가액), 기준주가의 60%】* 기준주가= 청약일전 과거 제3거래일부터 제5거래일까지의 가중산술평균주가」 — a raw filing sentence, with a × to close |
| **V5 AI 질문** (one model call) | four cards; tool rows one at a time; incremental answer; 검증된 계산 with 「입력」 marker; footer 근거 N건 · 접수번호 · 시각 | **as written.** Cards: 「빛과전자 전환사채 공시가 몇 건이나 있나요?」 / 「아이에이 유상증자, 1,000주 보유 시 배정 신주는 몇 주인가요?」 / 「내 포트폴리오에서 가장 급한 일정은…」 / 「운영자에게 직접 연락하려면…」. Asked the second **once**: 3 tool rows (이벤트 검색 → 2건 · 이벤트 읽기 · 계산 → 1,000주 × 0.507594018 = 507주), a 「검증된 계산」 block, footer 「근거 2건 · 20260818000250 · 2026-09-02 18:15 KST」, **5 visibly distinct DOM states over 10.09 s** (0.4 / 2.42 / 3.23 / 5.65 / 10.09 s) — incremental, not one late blob |
| **V6 샘플 보유 종목** | banner verbatim; four holdings, four companies, 기준 line; the four states; an edit survives reload | **as written.** 아이에이 038880 500주 ① D-43 (발행가 확정 전 · 확정 예정 2026-10-21 · 배정 신주 253주 +50) · 제이에스링크 127120 300주 ② D-1 · 페니트리움바이오 187660 500주 ① 기간 지남 D+37 (놓친 돈 79,182원추정 + 「청약·매도로 챙겼습니다」) · 휴맥스 115160 100주 ③ 통지 마감 지남 D+6; 「기준 2026-09-02 (KST)」. Edit test: 휴맥스 100주 → **777주**, survives reload at 1280 and still shown at 390 |
| **V7 404** | HTTP 404, Korean page, address echoed, no reason given | **as written.** `404`; 「이 주소에 해당하는 공시가 없습니다」 / 「관제 현황판에서 감시 중인 공시를 확인하실 수 있습니다.」 / `/events/00000000000000` / 「관제 현황판으로 →」 |
| **V8 origin/redirects/SEO** (HTTP, not browser) | http→301, www→301 preserving path+query, robots 200 ending in Sitemap:, sitemap 200 apex-only, health 200 with body | **as written.** `http://jujutower.com/` → 301 → apex; `https://www.jujutower.com/stocks?q=1` → **301** → `https://jujutower.com/stocks?q=1` (via `--resolve`, see below); robots **1,972 B**; sitemap **800 `<loc>`**; health `{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T18:18:07+09:00"}` |

**No horizontal overflow at 390** on any of the seven surfaces (`scrollWidth == clientWidth == 390`
on landing · 종목 · 이벤트 · ask · sample · 404 · login).

**The `www` resolver trap, as the plan warned.** A plain `curl https://www.jujutower.com/` from this
Mac fails with `[SSL: UNEXPECTED_EOF_WHILE_READING]` because the local resolver (Tailscale MagicDNS)
answers with non-Cloudflare addresses. With `--resolve www.jujutower.com:443:104.21.21.26` the edge
answers exactly right. This is why `make smoke-prod` reported **16 pass · 1 fail** here; the failing
check is the runner's DNS, not the product. The document itself only states the redirect.

**Cost.** Exactly **one** model call was spent (V5, at 1280). The answered thread was re-read at 390
rather than asking a second question. Nothing else in the sweep touches the model, and nothing in the
sweep writes to production: every request was a GET or a browser-local edit (the sample edit lives in
the throwaway profile's `localStorage`).

**No account was created on production.** `P4.S4` recorded that the harness denies the agent both
routes into reader data on the live product, and that boundary was respected rather than worked
around: §5.4's five account-bound blocks (A1 계정 만들기·로그인 · A2 담기 · A3 알림 설정 · A4 재설정
메일 · A5 마감 임박 이메일) are written with their exact expected strings and marked **[계정]**, and
§5.9 says plainly that the operator verifies them. They are the gate walkthrough's business.

## Where the sources disagreed, and what was done

1. **The agent has SEVEN declared tools, and two current docs still say five.**
   `src/mijual/agent/tools.py:TOOL_NAMES` is `search_events · get_event · get_portfolio ·
   save_feedback · get_contact · calculate · security_check`, and its own comment reads "The seven".
   `docs/current/product.md:198` still says "which of its **five** tools to call" and
   `docs/current/security.md:226` says "The **five** tools' declared arguments" — both written before
   P9's calculator and its guard landed. 첨부1 §5.2 already says 일곱, so 첨부2 says **seven** and the
   disagreement is recorded as a `## Doc impact` line for the docs phase.
2. **409 vs 418 renderable field instances** — `product.md` (gate *run*) vs `qa.md:98` (exposure
   *summary*). Resolved in the document by quoting 409, as 첨부1 did, and naming the wider 418 in the
   same `[근거]`.
3. **Two things my own draft got wrong and measurement corrected** (both were the docs being right):
   - I wrote that the 샘플 포트폴리오 is reachable "from the landing's footer line". It is **not** —
     the landing carries no 샘플 string at all (grepped the served HTML). `product.md`'s P8 section
     already says the sample is reached by **보유 종목 without a session** and by `?sample=1`; §3.1
     and V6 were rewritten to that, and the nav path was then verified in the browser (nav
     「보유 종목」 → `/portfolio` → the banner renders).
   - `/portfolio/notifications` opened anonymously answers **307 → `/auth/login`** (as does
     `/auth/reset` without a token), while `/portfolio` itself answers 200 and renders the sample.
     A3 now says so.
4. **`docs/current/operations.md` `## Operator Runtime` still records only the dev stack.** Not a new
   finding — `P4.S4` already wrote the production runtime as a `## Doc impact` note and this slice
   worked from that note, exactly as `P4.DECOMP`'s note for `P4.REVIEW` prescribes. No second line
   was added.

## Deviations from `plan.md`

1. **The plan's grep list did not anticipate the package identifier.** The first draft cited the gate
   command as a module path, which contains `mijual`. Rather than keep it and argue "code
   identifier", the citation was rewritten in prose (첨부1 quotes no identifier either). Greps are 0.
2. **A third `## Operator Questions` entry was added** beyond the plan's two: the **body-language
   inconsistency between the two drafts**. Both documents declare an English body, and 첨부2 is
   English throughout — but the landed 첨부1's §2, §5 and §7 are largely **Korean** prose. That is an
   operator decision about the submission pair (which document moves), not something this slice may
   settle, and the gate is where it belongs.
3. **V5 was executed at 1280 only** (one model call, as the plan requires); the *answered thread* was
   then read at 390. §5.9 states this precisely rather than claiming two runs.

**Housekeeping the harness declined:** `rm -rf` of the throwaway Chrome profile under the session
scratchpad was denied (three attempts, not worked around). The Chrome process is terminated and the
directory is disposable session scratch outside the repository; nothing in the working tree or on the
box was touched.

## What a judge would ask that the document does not answer

- **「샘플 계정 하나 주시죠」** — §5.1 offers self-signup and says an operator-provided 심사용 계정 is an
  open decision. If the operator wants one, its credentials go into §5.1's secondary bullet
  *literally*, and that is a one-paragraph edit.
- **「메일을 직접 받아볼 수 있나요?」** — only by signing up, adding a holding with a near deadline, and
  waiting for 08:30 KST. The document says exactly that (A5) and does not pretend it is instant.
- **「왜 오늘 게시판에 데이터 갱신 배너가 떠 있나요?」** — §5.8 item 1 answers it honestly (the banner is
  the product reporting its own freshness), but a judge may still read it as a fault. It was showing
  during this slice's sweep (`기준 2026-09-01 03:20 KST · 38시간 전 데이터`), which is the existing
  `## Operator Questions` entry — the operator may want beat's 19:30 run confirmed before the freeze.
- **「소스 코드를 볼 수 있나요?」** — the document names no repository. The intake settled that the
  submission form's github link is disabled, so §5.6 describes the one-command check without offering
  a clone URL.
