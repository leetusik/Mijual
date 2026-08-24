/* R14 parts — AI 질문 (P8.S14). 모든 문자열의 출처:
   `frontend/components/ask/copy.ts` (R6 서명분 전사) · 서버가 실어 오는 verbatim
   (도구 행 · 인용문 · 필드 korean_name — `grounding/samples/r1-live-healthy.json`) ·
   그리고 이 라운드가 서명한 신규 한국어 11건 (A_SEND + A_PRESETS의 D1–D9 + 없음).
   신규는 전부 `result.md` §Copy에 날짜·근거와 함께 등재된다. */

/* ── R6 서명 문자열 (copy.ts에서 전사, 변경 없음) ───────────────────── */
const A_INTRO = "검증을 통과한 공시에 대해서만 답합니다. 모든 답에는 원문 인용이 붙습니다. 계산은 하지 않습니다 — 계산은 내 종목 조회가 합니다.";
const A_ANON = "완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)";
const A_PROMISE = "검증된 필드만 근거로 답합니다 — 모든 답에 원문 인용";
const A_ASK_ABOUT = "이 공시에 대해 질문";
const A_FREE = "직접 질문 입력 →";      /* R6-2 — 이제 스트립의 자유 입력 칩 전용 */
const A_PREP = "답변 준비 중…";
const A_STOP = "중지";
const A_DISC = "연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.";
const A_RETRY = "재시도";
const A_REASK = "다시 질문";
const A_EVENT = "이벤트 상세";
const A_LOOKUP = "내 종목 조회";
const A_PAGE_LINK = "AI 질문 페이지 →";
const A_SCOPE_ALL = "범위: 전체 공시";

/* ── 이 라운드가 서명한 신규 한국어 ─────────────────────────────────── */
const A_SEND = "보내기";              /* Q-C · 운영자가 이 세션에서 정한 문자열 */

/* ── 범위 · 서식 ────────────────────────────────────────────────────── */
const A_NAME = "계양전기";
const A_RCEPT = "20260724000546";
const A_RCEPT_OLD = "20260611000483";
const A_SCOPE = `범위: ${A_NAME} · ${A_RCEPT}`;
const A_dart = (r) => `DART 원문 ${r} ↗`;
const A_ev = (n) => `근거 ${n}건`;
const A_STAMP = "2026-08-24 14:02 (KST)";

/* ── 서버 verbatim (샘플에서 전사 — 재구성 금지) ─────────────────────── */
const Q_FORFEITED = '4) 일반공모 청약: 상기 우리사주조합 청약, 구주주 청약 및 초과청약 결과 발생한 실권주 및 단수주(이하 "일반공모 배정분")는 "대표주관회사"가 다음 각호와 같이 일반에게 공모하되';
const Q_EXCESS = "3) 초과청약 : 우리사주조합 청약 및 구주주(신주인수권증서 보유자) 청약 이후 발생한 실권주가 있는 경우, 실권주를 구주주(신주인수권증서 보유자)가 초과청약(초과청약비율 : 배정 신주 1주당 0.2주)한 주식수에 비례하여 배정하며";
const Q_ISSUE = "▶ 확정 발행가액 = MAX【MIN(1차 발행가액, 2차 발행가액), 기준주가의 60%】 5) 최종 발행가액은 구주주청약일 초일 전 제3거래일에 결정되어 금융감독원 전자공시시스템에 2026년 09월 01일에 공시될 예정이며";
const Q_WARRANT = "3) 신주인수권증서 상장예정기간 : 2026년 08월 19일~ 2026년 08월 25일";
const A_TOOL_ROW = "이벤트 검색 「계양전기」 → 1건 · ① 유상증자 · 20260724000546";

/* ── 프리셋: 칩 라벨은 서빙된 korean_name, 보내는 질문은 R14 서명 문장 (Q-D) ── */
const A_PRESETS = [
  { k: "warrant_trading_period", label: "신주인수권증서 상장·매매기간", q: "신주인수권증서는 언제부터 언제까지 매매할 수 있나요?", sign: "R14-D1" },
  { k: "subscription_agents", label: "청약 취급처 (대상자별 증권사 + 청약일)", q: "청약은 어느 증권사에서 언제 받나요?", sign: "R14-D2" },
  { k: "forfeited_share_method", label: "실권주 처리 방식", q: "실권주는 어떻게 처리되나요?", sign: "R6" },
  { k: "excess_subscription", label: "초과청약 조건 (비율)", q: "초과청약은 어떤 조건으로 할 수 있나요?", sign: "R14-D3" },
  { k: "issue_price_formula", label: "발행가액 산정방법 (1·2차·확정 산식)", q: "발행가액은 어떻게 산정되나요?", sign: "R14-D4" },
  { k: "refixing_terms", label: "리픽싱 세부 조건", q: "리픽싱 조건은 어떻게 되나요?", sign: "R14-D5" },
  { k: "option_schedule", label: "콜·풋 세부 스케줄", q: "콜옵션과 풋옵션 스케줄은 어떻게 되나요?", sign: "R14-D6" },
  { k: "lockup_release", label: "보호예수 / 전매제한 해제일", q: "보호예수는 언제 해제되나요?", sign: "R14-D7" },
  { k: "dissent_notice_procedure", label: "반대의사 통지 방법·절차", q: "반대의사는 어떻게 통지하나요?", sign: "R14-D8" },
  { k: "appraisal_price", label: "매수예정가격 (서빙된 korean_name)", q: "주식매수청구 가격은 얼마인가요?", sign: "R14-D9" },
];
/* 계양전기 20260724000546이 실제로 서빙하는 다섯 필드, 페이지의 읽기 순서대로. */
const A_EVENT_PRESETS = ["warrant_trading_period", "subscription_agents", "forfeited_share_method", "excess_subscription", "issue_price_formula"]
  .map((k) => A_PRESETS.find((p) => p.k === k));

/* ── 턴 데이터 ──────────────────────────────────────────────────────── */
const A_TURN = {
  q: "실권주는 어떻게 처리되나요?",
  tools: [A_TOOL_ROW],
  sen: [
    { t: "우리사주조합과 구주주 청약, 초과청약 후에 발생한 실권주와 단수주는 일반공모로 넘어갑니다", c: [1] },
    { t: "일반공모 후에도 남는 청약 미달 주식은 대표주관회사가 자기 계산으로 인수합니다", c: [1] },
    { t: "구주주라면 청약 한도주식수 1주당 0.2주(20%) 비율로 초과청약할 수 있습니다", c: [2] },
  ],
  chips: { 1: { rcept: A_RCEPT, quote: Q_FORFEITED }, 2: { rcept: A_RCEPT, quote: Q_EXCESS } },
  foot: { n: 2, ev: [A_RCEPT], stamp: A_STAMP },
};
const A_TURN_PARTIAL = {
  q: A_TURN.q,
  tools: A_TURN.tools,
  sen: [A_TURN.sen[0], { t: "일반공모 후에도 남는 청약 미달 주식은 대표주관", c: [] }],
  chips: A_TURN.chips,
};
const A_TURN_REFUSAL = {
  q: "계양전기 유상증자로 받을 수 있는 돈이 얼마인가요?",
  tools: [],
  sen: [
    { t: "확정 발행가액은 아직 공시되지 않았습니다 — 2026-09-01에 공시될 예정입니다", c: [1] },
    { t: "확정 전 금액은 해설하지 않습니다.", c: [] },
  ],
  chips: { 1: { rcept: A_RCEPT, quote: Q_ISSUE } },
  links: [{ label: A_dart(A_RCEPT), ext: true }, { label: A_EVENT }, { label: A_LOOKUP }],
};

/* ── 부품 ───────────────────────────────────────────────────────────── */
function ALab({ children }) { return <p className="lab">{children}</p>; }

function ACite({ n, chip, open }) {
  const [on, setOn] = React.useState(!!open);
  return <span>
    <button type="button" className="achip" aria-expanded={on} onClick={() => setOn(!on)}>{n}</button>
    {on ? <span className="aqp">
      {chip.quote ? <span className="aqt">{chip.quote}</span> : null}
      <a className={chip.quote ? "aql" : "aql solo"} href={"https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + chip.rcept} target="_blank" rel="noopener noreferrer">{A_dart(chip.rcept)}</a>
    </span> : null}
  </span>;
}

/* Q-E — 한 단락. 문장은 인라인 span이고 문장 사이 간격은 CSS의 0.25em 하나뿐. */
function AProse({ turn, caret, openChip }) {
  return <p className="aprose">
    {turn.sen.map((s, i) => <span key={i} className="asen">
      {s.t}
      {s.c.map((n) => <ACite key={n} n={n} chip={turn.chips[n]} open={openChip === n && i === turn.sen.findIndex((x) => x.c.includes(n))} />)}
    </span>)}
    {caret ? <span className="acaret" aria-hidden="true"></span> : null}
  </p>;
}

function AAnswer({ turn, caret, stopped, footer, openChip }) {
  return <div className="aa" data-dim={stopped ? "true" : "false"}>
    {turn.tools.map((row, i) => <p key={i} className="atool">{row}</p>)}
    <AProse turn={turn} caret={caret} openChip={openChip} />
    {turn.links ? <p className="alinks">{turn.links.map((l) => <a key={l.label} className="alink" href="#" target={l.ext ? "_blank" : undefined} rel={l.ext ? "noopener noreferrer" : undefined}>{l.label}</a>)}</p> : null}
    {stopped ? <p className="astop">
      <span className="astopt">{A_DISC}</span>
      <button type="button" className="areask" style={{ marginLeft: "auto" }}>{A_RETRY}</button>
    </p> : null}
    {footer ? <p className="afoot">
      <span className="afacts">{[A_ev(turn.foot.n), ...turn.foot.ev, turn.foot.stamp].join(" · ")}</span>
      <span className="alinks"><a className="alink" href="#">{A_EVENT}</a></span>
      <button type="button" className="areask">{A_REASK}</button>
    </p> : null}
  </div>;
}

function ATurn({ turn, ...rest }) {
  return <div className="aturn"><p className="aq">{turn.q}</p><AAnswer turn={turn} {...rest} /></div>;
}

/* 한 버튼 · 세 텍스트. state: 'idle' | 'empty' | 'pending' | 'streaming' */
function AComposer({ state, text }) {
  const label = state === "pending" ? A_PREP : state === "streaming" ? A_STOP : A_SEND;
  return <form className="acom" onSubmit={(e) => e.preventDefault()}>
    <input className="ain" defaultValue={text || ""} aria-label="AI 질문" />
    <button type="button" className="asend" disabled={state === "empty" || state === "pending"}>{label}</button>
  </form>;
}

function AHeader({ scope }) {
  return <div className="ahd">
    <p className="ascope"><span className="ascopet">{scope === null ? A_SCOPE_ALL : A_SCOPE}</span>{scope === null ? null : <button type="button" className="axc">×</button>}</p>
    <span className="aacts">
      <button type="button" className="aicon" aria-label={A_PAGE_LINK}>↗</button>
      <button type="button" className="aicon" aria-label="닫기">×</button>
    </span>
  </div>;
}

function AIntro() {
  return <div className="aintro"><p className="aintrot">{A_INTRO}</p><p className="aanon">{A_ANON}</p></div>;
}

function AWidget({ scope, state, children }) {
  return <div className="aw">
    <AHeader scope={scope === undefined ? A_SCOPE : scope} />
    <div className="ath">{children}</div>
    <AComposer state={state} />
  </div>;
}

/* 질문 스트립 — 칩은 라벨, 보내는 것은 서명된 문장 (Q-D). free=false면 자유 입력
   칩 없음 (/ask에서는 컴포저가 바로 아래에 있다). */
function AStrip({ presets, free, onPick, heading }) {
  return <div className="astrip">
    <p className="ash">{heading === undefined ? A_ASK_ABOUT : heading}</p>
    <div className="arow">
      {(presets || A_EVENT_PRESETS).map((p) => <button key={p.k} type="button" className="ac" title={p.q} onClick={() => onPick && onPick(p)}>{p.label}</button>)}
      {free === false ? null : <button type="button" className="ac afree">{A_FREE}</button>}
    </div>
  </div>;
}

function ARail({ scope }) {
  return <aside className="arail panel">
    <span className="bk"></span>
    <p className="ascope"><span className="ascopet">{scope === null ? A_SCOPE_ALL : A_SCOPE}</span>{scope === null ? null : <button type="button" className="axc">×</button>}</p>
    <p className="apromise">{A_PROMISE}</p>
    <p className="aintrot">{A_INTRO}</p>
    <p className="aanon">{A_ANON}</p>
  </aside>;
}

/* 런처 — DOM 순서가 마크의 사양이다 (개정 ⑧): 링 위 반쪽(뒤) → 행성+밴드 → 링 아래 반쪽(앞). */
function ALauncher({ open }) {
  return <button type="button" className="alauncher" data-open={open ? "true" : "false"} aria-label="AI 질문" aria-expanded={!!open}>
    <span className="atail"></span>
    <span className="amark">
      <span className="aring aringb"></span>
      <span className="aplanet"><span className="aband"></span></span>
      <span className="aring aringf"></span>
    </span>
    <span className="aclose"></span>
  </button>;
}

Object.assign(window, {
  A_INTRO, A_ANON, A_PROMISE, A_ASK_ABOUT, A_FREE, A_SEND, A_PREP, A_STOP, A_DISC, A_RETRY, A_REASK,
  A_EVENT, A_LOOKUP, A_PAGE_LINK, A_SCOPE_ALL, A_SCOPE, A_NAME, A_RCEPT, A_RCEPT_OLD, A_STAMP,
  A_dart, A_ev, Q_FORFEITED, Q_EXCESS, Q_ISSUE, Q_WARRANT, A_TOOL_ROW,
  A_PRESETS, A_EVENT_PRESETS, A_TURN, A_TURN_PARTIAL, A_TURN_REFUSAL,
  ALab, ACite, AProse, AAnswer, ATurn, AComposer, AHeader, AIntro, AWidget, AStrip, ARail, ALauncher,
});
