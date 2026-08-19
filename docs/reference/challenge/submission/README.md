# Submission templates — 2026 금융 AI Challenge

Provenance for the two mandatory 양식 files in this folder. Downloaded by `P1.S3` on
**2026-08-19**. Korean section titles are quoted verbatim from the templates; everything
else is English per the project's working-language rule.

## Files

| File | Source URL | Bytes | SHA-256 |
|---|---|---|---|
| `(첨부1) 2026 금융 AI Challenge 공모전 기획서.hwpx` | `https://cfiles.dacon.co.kr/competitions/daker_2026-finance-ai-challenge/(첨부1) 2026 금융 AI Challenge 공모전 기획서.hwpx` | 47,372 | `15ba1f89595f15c7582abec69bf4f06dc99864c5ac778a400d224f38ce95c039` |
| `(첨부2) 2026 금융 AI Challenge 기능명세서.hwpx` | `https://cfiles.dacon.co.kr/competitions/daker_2026-finance-ai-challenge/(첨부2) 2026 금융 AI Challenge 기능명세서.hwpx` | 45,456 | `83be2cd46904d54717d624272f3af88c99b5b06c45cb12490f93688d31604a4b` |

Both URLs are linked as "양식 다운로드" from the `rules` section of the official brief
(`https://daker.ai/api/hackathons/2026-finance-ai-challenge`) and are publicly downloadable
without authentication (HTTP 200, `application/octet-stream`).

**Both must be filled in and converted to PDF before submission** — the rules require PDF,
not `.hwpx`. Re-check both files against the live URLs shortly before submission: the
organizer edits the brief in place (the hackathon record's `updatedAt` was
`2026-08-18T20:21Z`) and posts no notice when it changes.

## Reading `.hwpx` here

`.hwpx` is OWPML: a ZIP whose `Contents/section0.xml` holds the body. Text extracts cleanly
with the stdlib — no Hangul/LibreOffice needed to *read* the structure:

```python
import zipfile, re, html
raw = zipfile.ZipFile(PATH).read('Contents/section0.xml').decode('utf-8')
paras = [''.join(re.findall(r'<hp:t>(.*?)</hp:t>', p, re.S))
         for p in re.findall(r'<hp:p\b.*?</hp:p>', raw, re.S)]
print([html.unescape(re.sub('<[^>]+>', '', p)).strip() for p in paras if p.strip()])
```

*Writing* the filled documents is a separate P4 concern (Hangul, or an .hwpx-capable
converter, then export to PDF). Not solved here.

## Required structure (extracted verbatim)

Both templates open with `팀명` ("등록된 팀명과 동일하게 작성") and `구성원 성명`
("팀장, 팀원 순으로 작성"). `*` marks 필수항목.

### 첨부1 — 공모전 기획서 (7 sections; 1–6 필수, 7 optional)

1. `서비스 명칭*`
2. `아이디어 기획 핵심내용(요약)*` — 개조식 summary of the whole plan
3. `문제 정의 및 제안 배경*` — the concrete problem, plus why this 금융 고객 and 채널
4. `서비스 컨셉 및 차별성*` — core concept and 독창성·차별성 vs existing 금융 앱
5. `활용 데이터 및 생성형 AI 모델 적용 방안*` — data types, collection/use plan, and
   **how the 생성형 AI 모델 is used inside the service and what role it performs**
6. `기대 효과 및 확장 가능성*` — effects, concrete benefits, market/feature expansion,
   applicability beyond finance
7. `(자유타이틀 기재)` — free section for anything else

### 첨부2 — 기능 명세서 (5 sections, all 필수)

1. `MVP 구현 범위*` — scope actually implemented; **미구현 또는 향후 구현 예정 기능은 제외**
2. `주요 기능 목록*` — per working feature: 기능명, 기능 설명, 관련 화면, 구현 상태
3. `사용자 이용 흐름*` — the order a user hits the main features after opening the 배포 URL
4. `AI 및 데이터 처리 방식*` — the AI's role, data used, input/output data, and
   (필요시) whether 개인정보/민감정보 are processed
5. `MVP 검증 방법*` — the procedure a **judge** follows on the deployed URL to verify each
   main feature, plus **테스트 계정, 샘플 입력값, 예상 결과**, browser/runtime restrictions,
   and the MVP's limitations

Section 2's `관련 화면` and section 5's judge-run verification script are load-bearing for
P3: the service has to be verifiable by a stranger, unattended, from the URL alone.
Per the official Q&A there is **no page limit** as long as the given 양식 is preserved, and
시각자료 may be added.
