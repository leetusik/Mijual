/* R11 (P8.S8) — shared parts + the real rows every 내 종목 조회 card renders.
   Data is transcribed from the R11 handoff's walk (operator runtime, 2026-08-24) and
   from docs/reference/design/grounding/*; nothing here is invented. Where the handoff
   did not carry a value it renders as ⋯ (see Rights card note) — never a made-up one.
   Geometry lives in r11-lookup.css. */
const DS = window.MijualDesignSystem_7ce1bb;
const { RightsChip, DDay, Citation, EstimateMarker, StateBadge } = DS;

const fmt = (n) => n.toLocaleString('ko-KR');
/* finding 10 — 와/과 by the final consonant of the query's last character. */
function josa(q) {
  const c = q.charCodeAt(q.length - 1);
  const hangul = c >= 0xac00 && c <= 0xd7a3;
  const batchim = hangul ? (c - 0xac00) % 28 !== 0 : /[0-9a-zA-Z]$/.test(q) ? null : false;
  return batchim === null ? '와/과' : batchim ? '과' : '와';
}
const noMatchKo = (q) => `‘${q}’${josa(q)} 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요.`;

/* the round's one dated copy exception (Q-E, 2026-08-24) */
const MISSED_PROMPT_KO = '보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다';
const PROVENANCE_KO = '모든 값은 DART 공시에서만 나왔습니다 · 보유량 환산은 공시된 배정비율과의 곱셈이며, 시장 가격을 사용하지 않습니다';
const COVERAGE_BOUNDARY_KO = '놓친 돈은 집계 범위 안에서만 계산됩니다 · 2026년 이전의 유상증자 기록은 집계에 없습니다';
const DISCLAIMER_KO = '실제 손익은 개별 청약·매도 행동에 따라 다릅니다 — 이 값은 소멸된 증서의 이론가치를 보유량 기준으로 환산한 것입니다';
const MISSED_FRAME_KO = '청약도 매도도 하지 않았다면, 2026년 이 종목에서 사라진 가치';

function Bk() { return <i className="bk" aria-hidden="true"></i>; }
function Panel({ children, style, as }) { const T = as || 'section'; return <T className="panel" style={style}>{children}<Bk /></T>; }
function Lab({ children }) { return <div className="lab">{children}</div>; }

/* 크럼 레일 — 「내 종목 조회」 keeps its place, at the size a page label deserves. */
function Rail({ here }) {
  return <nav className="rail"><a href="#">← 관제 현황판</a>{here === false ? null : <span className="here">내 종목 조회</span>}</nav>;
}

/* 종목 아이덴티티 + 검색 + (조건부) 보유량 strip */
function Identity({ name, code, strip }) {
  return <Panel>
    <div className="idp">
      <div className="idbox">
        <h1 className="corp">{name}</h1>
        <p className="idmeta"><span>고유번호 {code}</span><span>DART 공시 기준</span></p>
      </div>
      <form className="idsearch" onSubmit={(e) => e.preventDefault()}>
        <span className="field"><input className="input" defaultValue={name} aria-label="종목명 또는 종목코드" /></span>
        <button className="submit" type="submit">조회</button>
      </form>
    </div>
    {strip}
  </Panel>;
}

/* 보유량 strip — Q-C: only where a number on this page changes with it. */
function Strip({ n, setN, restore, inputRef }) {
  return <div className="strip">
    <label className="striplab" htmlFor="held">보유 주식 수</label>
    <input id="held" ref={inputRef} className="num" inputMode="numeric" value={n ? fmt(n) : ''}
      onChange={(e) => setN(parseInt(e.target.value.replace(/[^0-9]/g, ''), 10) || 0)} />
    <span className="unit">주</span>
    <div className="presets">{[100, 500, 1000].map((v) =>
      <button key={v} className="preset" aria-pressed={n === v} onClick={() => setN(v)}>{fmt(v)}주</button>)}</div>
    {restore ? <button className="restore" onClick={() => setN(restore)}><span>이전 입력 {fmt(restore)}주</span></button> : null}
    <span className="stripcap">서버 전송 없음</span>
  </div>;
}

function Sec({ title, children }) {
  return <section className="sec"><h2 className="eyebrow">{title}</h2>{children}</section>;
}

/* 권리 패널 — on a single-stock page the panel is a deadline, not a company:
   chip + 접수번호 meta on the left, the governing label as the h3 on the right. */
function RightsPanel({ type, rcept, filed, corrected, whenLabel, slot, days, date, win, children, go }) {
  return <Panel as="article">
    <div className="rhead">
      <div className="rid">
        <div className="rchip"><RightsChip type={type} /></div>
        <p className="rmeta"><span>접수번호 {rcept}</span><span>{filed} 공시</span>{corrected ? <span>정정 반영</span> : null}</p>
      </div>
      <div className="rwhen">
        <h3 className="whenlab">{whenLabel}</h3>
        {slot === 'dday' ? <DDay days={days} date={date} /> : null}
        {slot === 'tbd' ? <StateBadge state="tbd" /> : null}
        {win ? <p className="win"><span className="dates">{win.dates}</span>{win.state === 'open' ? <span className="live">{win.phrase}</span> : null}{win.state === 'closed' ? <span className="past">기한 지남</span> : null}</p> : null}
        {slot === 'tbd' ? <p className="win">일정이 공시상 미정</p> : null}
      </div>
    </div>
    {children}
    {go !== false ? <p className="rowfoot"><a className="golink" href="#">상세 보기 →</a></p> : null}
  </Panel>;
}

function Chain({ cells }) {
  return <div className="chain">{cells.map((c, i) =>
    <div className="cell" key={i}>
      {c.lab ? <p className="clab">{c.lab}</p> : null}
      <p className="cval">{c.chip ? <span className="pend">{c.chip}</span> : null}{c.val ? <span className={'v' + (c.ratio ? ' ratio' : '')}>{c.val}</span> : null}{c.note ? <span style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--text-sm)', fontWeight: 400, color: 'var(--ink-2)' }}>{c.note}</span> : null}</p>
      {c.sub ? <p className="clab">{c.sub}</p> : null}
    </div>)}</div>;
}

/* the input prompt — a control, once per page (① block if there is one, else 놓친 돈) */
function Prompt({ onClick }) {
  return <button className="prompt" onClick={onClick}>{MISSED_PROMPT_KO}<span className="arw">→</span></button>;
}

/* ② — one table for the type, one row per filing (findings 6 + 7). */
function CTable({ rows, type }) {
  return <div className="ctab">
    <div className="ctop"><RightsChip type={type || 2} /></div>
    <div className="ctrow cthead"><span>공시</span><span>전환가액</span><span>전환 시 주식수</span><span>오버행</span><span>전환청구 개시</span><span></span></div>
    {rows.map((r) => <div className="ctrow" key={r.rcept}>
      <span className="ctfiled"><span className="ctdate">{r.filed}</span><span className="ctrcept">{r.rcept}</span></span>
      {r.price ? <span className="ctval" data-l="전환가액">{r.price}</span> : <span className="ctmiss" data-l="전환가액">⋯</span>}
      {r.shares ? <span className="ctval" data-l="전환 시 주식수">{r.shares}</span> : <span className="ctmiss" data-l="전환 시 주식수">⋯</span>}
      {r.overhang ? <span className="ctval" data-l="오버행">{r.overhang}</span> : <span className="ctmiss" data-l="오버행">⋯</span>}
      <span className="ctwhen"><span className="dates">{r.open}</span><DDay days={r.days} /></span>
      <a className="golink" href="#">상세 보기 →</a>
    </div>)}
    <p className="ctsrc"><span>DART 공시 API — 전환가액 · 전환 시 주식수 · 오버행</span><span>{rows.length}건</span></p>
  </div>;
}

/* ③ — the two steps, drawn for the first time (finding 8). */
function Steps({ steps }) {
  return <React.Fragment>
    <div className="steps">{steps.map((s, i) => <div className={'step' + (s.past ? ' pastStep' : '')} key={i}>
      <div className="snum"><span>{i + 1}단계</span></div>
      <div className="sbody">
        <div className="sHead"><h4 className="stitle">{s.title}</h4>{s.past ? <span className="past">기한 지남</span> : null}</div>
        {s.win ? <p className="swin">{s.win}</p> : <p className="absent">현재 버전 공시에 없음</p>}
      </div>
    </div>)}</div>
    <p className="sdep">1단계에서 반대의사를 통지한 주주만 행사 가능</p>
  </React.Fragment>;
}

/* 놓친 돈 — two states, and one won figure per section (finding 4). */
function Missed({ rows, n, onPrompt, showPrompt }) {
  const single = rows.length === 1;
  return <Panel>
    <div className="mmhead">
      <p className="frame">{MISSED_FRAME_KO}</p>
      {!single && n ? null : null}
      {showPrompt ? <Prompt onClick={onPrompt} /> : null}
      <p className="mmcap">유상증자 {rows.length}건 · 집계 범위 2026-01-01 ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치 환산</p>
    </div>
    <div className="bkd">
      <div className="brow bhead"><span>유상증자</span><span>증서 매매기간</span><span>소멸 계산 (시장 전체)</span><span className="r">{n ? `${fmt(n)}주 기준` : '보유 주식 수'}</span></div>
      {rows.map((r) => <React.Fragment key={r.rcept}>
        <div className="brow">
          <span className="boff">
            <RightsChip type={1} compact />
            <span className="bofftitle">{r.title}</span>
            <span className="bmeta">접수번호 {r.rcept}<br />확정발행가 {r.price}</span>
            <a className="golink" href="#">상세 보기 →</a>
          </span>
          <span className="bwin"><span className="dates">{r.window}</span><span className="past">기간 지남 · {r.dday}</span><Citation rceptNo={r.rcept} quote={r.quote} /></span>
          <span className="bcalc">
            <span>발행 <span className="v">{r.issued}</span> − 청약 <span className="v">{r.subscribed}</span></span>
            <span>= 소멸 <span className="v lapsed">{r.lapsed}</span> · <EstimateMarker value={r.lapsedValue} color="var(--ink-2)" /></span>
          </span>
          <span className="bmine">
            {n ? <React.Fragment>
              <span className={'v' + (single ? ' big' : '')}><EstimateMarker value={r.mine(n)} color="var(--alert)" /></span>
              {single && r.floor(n) ? <span className="floorline">하한 <EstimateMarker value={r.floor(n)} color="var(--ink-2)" /></span> : null}
              <span className="cap">배정 {r.allot(n)}주 × 「추정」{r.unit}</span>
            </React.Fragment> : <span className="bslot" aria-hidden="true"></span>}
          </span>
        </div>
      </React.Fragment>)}
    </div>
    {n ? <p className="calcfoot">배정 <span className="v">{rows[0].allot(n)}주</span> = {fmt(n)}주 × 배정비율 <span className="v">{rows[0].ratio}</span> (1주 미만 버림) · 증서 1주 이론가치 <EstimateMarker value={rows[0].unit} color="var(--ink-2)" /> = 확정발행가 × 할인율 ÷ (1 − 할인율)</p> : null}
    <p className="disc">{DISCLAIMER_KO}</p>
  </Panel>;
}

function Zero({ pending }) {
  return <Panel><div className="zero">
    <p className="zerolead">이 종목은 2026년 집계 범위에서 놓친 권리가 없습니다</p>
    {pending ? <p className="zerosub">진행 중인 건의 소멸 여부는 청약 종료(<span className="v">{pending}</span>) 후 집계됩니다</p> : null}
  </div></Panel>;
}

/* 진입 페이지의 맥락 (Q-A = b) — the two things this page can honestly say with no query:
   what it watches, and how much of it. Both are already signed; no new copy. */
function WatchPanel({ watching }) {
  return <Panel><div className="empty">
    <div className="watch"><span className="watchlab">감시 대상</span><RightsChip type={1} /><RightsChip type={2} /><RightsChip type={3} /></div>
    <p className="cap">감시 중 {watching}건</p>
  </div></Panel>;
}

function NoRights({ watching }) {
  return <Panel><div className="empty">
    <p className="emptylead">이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다</p>
    <div className="watch"><span className="watchlab">감시 대상</span><RightsChip type={1} /><RightsChip type={2} /><RightsChip type={3} /></div>
    <p className="cap">감시 중 {watching}건</p>
  </div></Panel>;
}

/* 집계 범위 — finding 12: the boundary panel gets its own heading. */
function Coverage() {
  return <section className="sec"><h2 className="eyebrow">집계 범위</h2>
    <Panel><div className="cvg">
      <div className="cvgrows">
        <p className="cvgrow"><RightsChip type={1} compact />2026-01-01부터</p>
        <p className="cvgrow"><RightsChip type={2} compact />2025-06-01부터</p>
      </div>
      <p className="cap">{COVERAGE_BOUNDARY_KO}</p>
    </div></Panel>
  </section>;
}

function Prov() { return <p className="prov">{PROVENANCE_KO}</p>; }

/* 진입 페이지 — Q-A = (b) */
function EntryHead({ q, candidates, noMatch, active }) {
  return <div className="entry">
    <h1 className="h1">내 종목 조회</h1>
    <p className="sub">종목명 하나로 놓친 권리와 진행 중인 권리를 조회합니다</p>
    <form className="entrysearch" onSubmit={(e) => e.preventDefault()}>
      <span className="field">
        <input className="input" defaultValue={q || ''} placeholder="종목명 또는 종목코드 — 예: 계양전기" aria-label="종목명 또는 종목코드" />
        {candidates ? <ul className="cands" role="listbox">{candidates.map((c, i) =>
          <li key={c.code} className={'cand' + (i === active ? ' active' : '')} role="option" aria-selected={i === active}>
            <span className="cn">{c.name}</span><span className="cc">{c.code}</span></li>)}</ul> : null}
      </span>
      <button className="submit" type="submit">조회</button>
    </form>
    {noMatch ? <p className="nomatch" role="status">{noMatchKo(noMatch)}</p> : null}
  </div>;
}

/* ------------------------------------------------------------------ 표본 데이터 */
const KY = { name: '계양전기', code: '00102618', rcept: '20260724000546', filed: '2026-05-08', ratio: '0.2314082845' };
const HANWHA = { name: '한화솔루션', code: '00162461' };
const PJ = { name: '풍전약품', code: '01110474' };
const ASIANA = { name: '아시아나항공', code: '00138792' };
const SEGI = { name: '세기상사', code: '00133618' };

const PJ_ROWS = [
  { rcept: '20250905000550', filed: '2025-09-05', price: null, shares: null, overhang: '8.03%', open: '2026-09-15', days: 22 },
  { rcept: '20250930000508', filed: '2025-09-30', price: '1,182원', shares: null, overhang: '4.29%', open: '2026-10-02', days: 39 },
  { rcept: '20260610000611', filed: '2026-06-10', price: null, shares: null, overhang: '6.79%', open: '2027-06-18', days: 298 },
];
const ASIANA_R2 = [{ rcept: '20251104000252', filed: '2025-11-04', price: null, shares: null, overhang: null, open: '2026-11-13', days: 81 }];
const DD_ROWS = [{ rcept: '20251016000315', filed: '2025-10-16', price: '15,552원', shares: null, overhang: '6.68%', open: '2026-10-24', days: 61 }];

const HANWHA_LAPSE = [{
  rcept: '20260720000067', title: '2026-03-26 결정 유상증자', price: '22,100원',
  window: '2026-07-06 ~ 07-10', dday: 'D+45', issued: '42,165,422주', subscribed: '38,430,497주',
  lapsed: '3,734,925주 (8.86%)', lapsedValue: '206.4억원', ratio: '0.2465120994', unit: '5,525원',
  allot: (n) => fmt(Math.floor(n * 0.2465120994)),
  mine: (n) => fmt(Math.floor(n * 0.2465120994) * 5525) + '원',
  /* 하한 is served, not derivable — it exists for the walked 500주 and for nothing else. */
  floor: (n) => (n === 500 ? '545,181원' : null),
  quote: '- 신주인수권증서 상장예정기간: 2026년 07월 06일 ~ 2026년 07월 10일 (5거래일간)',
}];

const CANDS = [{ name: '계양전기', code: '00102618' }];
