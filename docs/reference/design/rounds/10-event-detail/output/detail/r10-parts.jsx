/* R10 (P8.S6) — shared parts + the real rows every detail card renders.
   Data is transcribed from the walked pages (operator runtime, 2026-08-23);
   nothing here is invented. Geometry lives in r10-detail.css. */
const DS = window.MijualDesignSystem_7ce1bb;
const { RightsChip, DDay, Citation, EstimateMarker, StateBadge } = DS;
const dart = (n) => 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + n;

function Bk() { return <i className="bk" aria-hidden="true"></i>; }
function Panel({ children, style }) { return <section className="panel" style={style}>{children}<Bk /></section>; }
function Crumb() { return <a className="crumb" href="#">← 관제 현황판</a>; }
function Lab({ children }) { return <div className="lab">{children}</div>; }

/* Header panel — one component for every state the walk found.
   window: {dates, state:'open'|'closed'|'pending', phrase}  ·  slot: 'dday'|'tbd'|'absent' */
function Head({ type, name, rcept, filed, corrected, bodyName, cdLabel, slot, days, date, win, offer, mobile }) {
  return <div className="hd">
    <div className="hid">
      <div className="hchip"><RightsChip type={type} /></div>
      <div className="corpline"><h1 className="corp">{name}</h1><a className="dart" href={dart(rcept)} target="_blank" rel="noreferrer">DART 원문 ↗</a></div>
      {bodyName ? <p className="idnote">공시 본문 표기: <b>{bodyName}</b> — 원문에는 이 이름으로 기재되어 있습니다</p> : null}
      <p className="meta">
        <span>접수번호 {rcept}</span>
        {filed ? <span>최초 공시 {filed}</span> : null}
        {corrected ? <span className="corr">{corrected}</span> : null}
      </p>
    </div>
    {cdLabel ? <div className="cd">
      <p className="cdlab">{cdLabel}</p>
      <div className="ddayslot">
        {slot === 'dday' ? <DDay days={days} date={date} /> : null}
        {slot === 'tbd' ? <StateBadge state="tbd" /> : null}
        {slot === 'absent' ? <span className="absent">현재 버전 공시에 없음</span> : null}
      </div>
      {slot === 'tbd' ? <p className="win">카운트다운 없음 — 일정이 공시상 미정</p> : null}
      {win ? <p className="win">
        <span className="dates">{win.dates}</span>
        {win.state === 'open' ? <span className="live">{win.phrase}</span> : null}
        {win.state === 'closed' ? <span className="past">기한 지남</span> : null}
      </p> : null}
      {offer ? <a className="offer" href="#">보유 종목에 담기 →</a> : null}
    </div> : null}
  </div>;
}

/* 질문 스트립 — placement + hit height only (surface 7 owns the design) */
function QStrip({ chips }) {
  return <div className="qstrip">
    {chips.map((c) => <button key={c} type="button" className="qchip">{c}</button>)}
    <button type="button" className="qchip qask">직접 질문 입력 →</button>
  </div>;
}

/* ① chain — ruled cells, no arrows. cite = a served quote; est = 「추정」 */
function Cell({ label, value, ratio, est, cite, pend }) {
  return <div className="cell">
    {pend ? null : <p className="clab">{label}</p>}
    <p className="cval">
      {pend ? <React.Fragment><span className="pend">발행가 확정 전</span><span className="num" style={{ fontSize: 'var(--text-sm)', fontWeight: 400, color: 'var(--ink-2)' }}>{pend}</span></React.Fragment>
        : est ? <EstimateMarker value={value} />
          : <span className={ratio ? 'num ratio' : 'num'}>{value}</span>}
      {cite ? <Citation rceptNo={cite[0]} quote={cite[1]} /> : null}
    </p>
  </div>;
}
function Chain({ cells, foot, convert }) {
  return <div className="chainwrap">
    <div className="chain">{cells.map((c, i) => <Cell key={i} {...c} />)}</div>
    {(foot || convert) ? <div className="chainfoot">
      <p className="chainnote">{foot}</p>
      {convert ? <a className="convert" href="#">내 보유량으로 환산 →</a> : null}
    </div> : null}
  </div>;
}

/* ② fact strip — API tier: no per-cell [근거], one mono source row */
function Facts({ items, rcept }) {
  return <div className="facts">
    <div className="fgrid">{items.map((it, i) => <div className="fcell" key={i}>
      <p className="clab">{it.l}</p>
      <p className="cval"><span className="num">{it.v}</span></p>
      {it.s ? <p className="fsub">{it.s}</p> : null}
    </div>)}</div>
    <div className="fsrc"><span>DART 공시 API</span><a href={dart(rcept)} target="_blank" rel="noreferrer">{rcept} ↗</a></div>
  </div>;
}

function Sec({ t, children, src }) { return <div className="sec"><h2 className="eyebrow">{t}</h2>{children}{src ? <SecSrc rcept={src} /> : null}</div>; }
/* Section-level source: for rows whose value IS the filing's own words, a [근거] would
   only re-print what is already on screen. One mono 원문 link closes the section instead. */
function SecSrc({ rcept }) { return <p className="secsrc"><a href={dart(rcept)} target="_blank" rel="noreferrer">DART 원문{' '}{rcept}{' '}↗</a></p>; }
function Row({ label, cite, children, sub }) {
  return <div className="row">
    <p className="rlab">{label}</p>
    <div className="rval">{children}{cite ? <Citation rceptNo={cite[0]} quote={cite[1]} /> : null}{sub ? <p className="sub">{sub}</p> : null}</div>
  </div>;
}
function Prov() { return <p className="prov">모든 값은 DART 공시에서만 나왔습니다 · 각 항목의 [근거]가 원문 구절과 접수번호로 연결됩니다</p>; }

/* ③ steps */
function Step({ n, title, win, past, children }) {
  return <div className={past ? 'step pastStep' : 'step'}>
    <div className="snum"><span>{n}</span></div>
    <div className="sbody">
      <div className="sHead">
        <h3 className="stitle">{title}</h3>
        <span className="swin">{win}</span>
        {past ? <span className="past">기한 지남</span> : null}
      </div>
      <p className="sdep">{children}</p>
    </div>
  </div>;
}

/* old → new pair — the one grammar for 정정 diff and 철회 evidence */
function Pair({ label, before, after, deleted }) {
  return <div className="move">
    {label ? <p className="mlab">{label}</p> : null}
    <div className="mpair">
      <div className="mside"><p className="mtag">정정 전</p><p className="mval">{before}</p></div>
      <div className="mside after"><p className="mtag">정정 후</p>{deleted ? <p className="mdel">(정정 후 본문에서 삭제됨)</p> : <p className="mval">{after}</p>}</div>
    </div>
  </div>;
}

/* 정정 band + story, with the open/closed states of 「정정 이력」 */
function Band({ text, open, onToggle, children }) {
  return <React.Fragment>
    <div className="band">
      <h2 className="bandTxt">{text}</h2>
      <button type="button" className="hist" aria-expanded={!!open} onClick={onToggle}>
        {open ? '접기' : '정정 이력'}{open ? <span className="mark" aria-hidden="true">×</span> : null}
      </button>
    </div>
    {open ? <div className="story">{children}</div> : null}
  </React.Fragment>;
}
function Rail({ rows }) {
  return <ol className="rail">{rows.map((r) => <li key={r.rcept} className={r.cur ? 'rrow rcur' : 'rrow'}>
    <span className="rmark" aria-hidden="true"></span>
    <span className="rdate">{r.dt}</span>
    <span className="rkind">{r.kind}</span>
    <a className="rlink" href={dart(r.rcept)} target="_blank" rel="noreferrer">{r.rcept} ↗</a>
    {r.cur ? <span className="rbadge">현재 읽는 버전</span> : null}
  </li>)}</ol>;
}

/* ---------------------------------------------------------------- real rows */
const KY = {
  type: 1, name: '계양전기', rcept: '20260724000546', filed: '2026-05-08', corrected: '정정 반영',
  cdLabel: '신주인수권증서 매매 마감', slot: 'dday', days: 2, date: '2026-08-25',
  win: { dates: '2026-08-19 ~ 2026-08-25', state: 'open', phrase: '거래 가능 · 마감 D-2' }, offer: true,
};
const HANWHA = {
  type: 1, name: '한화솔루션', rcept: '20260720000067', filed: '2026-04-27', corrected: '정정 반영',
  cdLabel: '신주인수권증서 매매 마감', slot: 'dday', days: -44, date: '2026-07-10',
  win: { dates: '2026-07-06 ~ 2026-07-10', state: 'closed' },
};
const KN = {
  type: 1, name: '경남제약', rcept: '20260623000409', filed: '2026-05-21',
  cdLabel: '신주인수권증서 매매 마감', slot: 'tbd',
};
const ASIANA = {
  type: 3, name: '아시아나항공', rcept: '20260713000482', filed: '2026-05-13', corrected: '정정 반영',
  cdLabel: '반대의사 통지 마감', slot: 'absent',
};
const DD = {
  type: 2, name: '대동기어', rcept: '20251016000315', filed: '2025-10-16',
  cdLabel: '전환청구 개시', slot: 'dday', days: 62, date: '2026-10-24',
  win: { dates: '2026-10-24 ~ 2030-09-24', state: 'pending' },
};
const SEGI = {
  type: 3, name: '세기상사', rcept: '20260713000345', filed: '2026-05-21', corrected: '정정 3회 반영',
  cdLabel: '반대의사 통지 마감', slot: 'dday', days: -48, date: '2026-07-06',
  win: { dates: '2026-06-22 ~ 2026-07-06', state: 'closed' },
};
const Q_R1 = ['신주인수권증서 매매기간', '배정비율', '발행가액 산정방법', '초과청약 비율', '청약 취급처'];
const Q_R2 = ['전환가액', '오버행', '리픽싱 조건', '콜·풋 스케줄', '보호예수 해제일'];
const Q_R3 = ['반대의사 통지', '매수청구 행사', '통지 방법', '접수처', '정정 이력'];

const CITE_KY_WINDOW = ['20260724000546', '3) 신주인수권증서 상장예정기간 : 2026년 08월 19일~ 2026년 08월 25일'];
const CITE_KY_DISCOUNT = ['20260724000546', '▶ 확정 발행가액 = MAX【MIN(1차 발행가액, 2차 발행가액), 기준주가의 60%】 5) 최종 발행가액은 구주주청약일 초일 전 제3거래일에 결정되어 금융감독원 전자공시시스템에 2026년 09월 01일에 공시될 예정이며'];
const CITE_KY_EXCESS = ['20260724000546', '3) 초과청약 : 우리사주조합 청약 및 구주주(신주인수권증서 보유자) 청약 이후 발생한 실권주가 있는 경우, 실권주를 구주주(신주인수권증서 보유자)가 초과청약(초과청약비율 : 배정 신주 1주당 0.2주)한 주식수에 비례하여 배정하며'];
const CITE_HANWHA_PRICE = ['20260720000067', '확정 발행가액 : 22,100원 (1차 발행가액과 2차 발행가액 중 낮은 가액)'];
const CITE_DD_LOCKUP = ['20251016000315', '사모 발행(발행일로부터 1년간 전환 및 권면분할 금지)'];
const CITE_SEGI_NOTICE = ['20260713000345', '- 합병반대의사 통지 접수기간 : 2026년 06월 22일 ~ 2026년 07월 06일 - 합병승인을 위한 주주총회 예정일자 : 2026년 07월 07일 - 주식매수청구권 행사기간 : 2026년 07월 07일 ~ 2026년 07월 27일라. 접수장소 -존속회사: 서울특별시 중구 퇴계로 212 (충무로 4가)'];
const CITE_SSAM = ['20260805000454', '이에 당사는 대표주관회사와 협의하여 유상증자 기간의 장기화에 따른 회사 주권의 상장 규정에 의거한 관리종목 지정 우려로 기존 주주 및 신규 투자자에게 혼란을 초래할 우려가 있다고 판단하여, 부득이하게 금번 유상증자를 철회하기로 결정하였습니다'];

Object.assign(window, {
  DS, RightsChip, DDay, Citation, EstimateMarker, StateBadge, dart,
  Bk, Panel, Crumb, Lab, Head, QStrip, Cell, Chain, Facts, Sec, SecSrc, Row, Prov, Step, Pair, Band, Rail,
  KY, HANWHA, KN, ASIANA, DD, SEGI, Q_R1, Q_R2, Q_R3,
  CITE_KY_WINDOW, CITE_KY_DISCOUNT, CITE_KY_EXCESS, CITE_HANWHA_PRICE, CITE_DD_LOCKUP, CITE_SEGI_NOTICE, CITE_SSAM,
});
