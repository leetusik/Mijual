/* R9 board — shared row data + row/panel parts for the P8.S4 cards.
   Data is the grounding snapshot (board-snapshot.md, anchor 2026-08-20 KST):
   the real events the record names, in the board's rank (key date asc, ties by rcept_no
   asc), anchored to the walk runtime 2026-08-23 KST — so these are the rows the
   operator actually walked. Sources: grounding/board-snapshot.md and the pinned
   samples (풍전약품 r2-corpname-trap, 대동기어 r2-option-schedule, 경남제약
   r1-tbd-schedule). Nothing here is invented; the ranked window is 15 rows and the
   record names 13, so two rows are simply not drawn. */
const { RightsChip, DDay, StateBadge } = window.MijualDesignSystem_7ce1bb;

const R9_ROWS = [
  { t: 1, c: '계양전기', l: '신주인수권증서 매매 마감', d: '2026-08-25', dd: 2, r: '20260724000546', sub: '청약 2026-09-04', pend: true },
  { t: 1, c: 'SG', l: '신주인수권증서 매매 마감', d: '2026-08-25', dd: 2, r: '20260720000128', sub: '청약 2026-09-04', pend: true },
  { t: 1, c: '퓨쳐켐', l: '신주인수권증서 매매 마감', d: '2026-08-25', dd: 2, r: '20260714000389', sub: '청약 2026-09-04', pend: true },
  { t: 2, c: '라온텍', l: '전환청구 개시', d: '2026-08-26', dd: 3, r: '20250818000222' },
  { t: 3, c: '휴맥스', l: '반대의사 통지 마감', d: '2026-08-27', dd: 4, r: '20260811000467' },
  { t: 1, c: 'HLB제약', l: '신주인수권증서 매매 마감', d: '2026-09-01', dd: 9, r: '20260803000211', sub: '청약 2026-09-11', pend: true },
  { t: 1, c: '툴젠', l: '신주인수권증서 매매 마감', d: '2026-09-07', dd: 15, r: '20260806000329', sub: '청약 2026-09-17' },
  { t: 3, c: '알에프텍', l: '반대의사 통지 마감', d: '2026-09-22', dd: 30, r: '20260804000294' },
  { t: 2, c: '풍전약품', l: '전환청구 개시', d: '2026-10-02', dd: 40, r: '20250930000508' },
  { t: 3, c: '미래에셋비전스팩7호', l: '반대의사 통지 마감', d: '2026-10-06', dd: 44, r: '20260512000669' },
  { t: 3, c: '로젠', l: '반대의사 통지 마감', d: '2026-10-16', dd: 54, r: '20260730000215' },
  { t: 2, c: '대동기어', l: '전환청구 개시', d: '2026-10-24', dd: 62, r: '20251016000315' },
  { t: 3, c: 'IBKS제24호스팩', l: '반대의사 통지 마감', d: '2026-11-02', dd: 71, r: '20260619000664' },
];

/** ② 전환청구 진행 중 — 개시일이 walk 기준일(2026-08-23) 앞에 있는 실제 이벤트. 「종료」가 아니라 열려 있는 창이다. */
const R9_OPEN_NOW = [
  { t: 2, c: '삼성제약', l: '전환청구 개시', d: '2026-08-21', dd: -2, r: '20250820000220' },
  { t: 2, c: '트리니티항공', l: '전환청구 개시', d: '2026-08-22', dd: -1, r: '20250808000003' },
  { t: 2, c: '위츠', l: '전환청구 개시', d: '2026-08-22', dd: -1, r: '20250814003928' },
  { t: 2, c: '에어레인', l: '전환청구 개시', d: '2026-08-22', dd: -1, r: '20250826000420' },
];

/** 일정 추후결정 — 날짜가 근처에 없다 (R3). 그라운딩 팩이 이름을 담은 실제 이벤트는 경남제약 하나. */
const R9_TBD = [
  { t: 1, c: '경남제약', l: '신주인수권증서 매매 마감', dd: null, r: '20260623000409', pend: true },
];

const dart = (r) => 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + r;

function R9Row({ e, state }) {
  const cls = ['row', state === 'hover' ? 'hover' : '', state === 'focus' ? 'focus' : '', state === 'changed' ? 'changed' : ''].filter(Boolean).join(' ');
  return (
    <li className={cls}>
      <span className="top">
        <RightsChip type={e.t} compact />
        <span className="corpCell">
          <a className="corp" href="#">{e.c}</a>
          <a className="dart" href={dart(e.r)} target="_blank" rel="noreferrer" aria-label={e.c + ' DART 원문'}>↗</a>
        </span>
      </span>
      <span className="rmeta">
        <span className="when">
          <span className="wlabel">{e.l}</span>
          {e.d ? <span className="wdate">{e.d}</span> : null}
        </span>
        <span className="extras">
          {e.sub ? <span className="sub">{e.sub}</span> : null}
          {e.pend ? <span className="pend">발행가 확정 전</span> : null}
        </span>
      </span>
      <span className="rail">{e.dd === null ? <StateBadge state="tbd" /> : <DDay days={e.dd} showDate={false} />}</span>
    </li>
  );
}

function R9Rows({ rows, extras = true, states = {} }) {
  return (
    <ol className="rows" data-extras={extras ? 'yes' : 'none'}>
      {rows.map((e) => <R9Row key={e.r} e={e} state={states[e.c]} />)}
    </ol>
  );
}

const R9_TABS = [['전체', 488], ['유상증자 신주인수권', 50], ['전환사채 오버행', 422], ['주식매수청구권', 16]];

function R9Tabs({ active = 0, hover = -1 }) {
  return (
    <div className="tabs" role="group">
      {R9_TABS.map(([n, k], i) => (
        <button key={n} type="button" aria-pressed={i === active} className={['tab', i === active ? 'on' : '', i === hover ? 'hover-demo' : ''].filter(Boolean).join(' ')} style={i === hover ? { color: 'var(--ink-1)', borderBottomColor: 'var(--border-strong)' } : null}>
          {n} <span className="k">{k}</span>
        </button>
      ))}
    </div>
  );
}

/** The line that makes the numbers legible (walk 2/3) + the D-day ladder (walk 7). */
function R9Meta({ total = 386, shown = 15, legend = true }) {
  return (
    <div className="meta">
      <span>탭 숫자는 감시 중 전체 건수입니다 · 아래 목록은 카운트다운 <b className="mono">{total}건</b> 중 <b className="mono">{shown}건</b></span>
      {legend ? (
        <span className="legend"><span className="lg0">D-DAY</span><span className="lg1">D-7 이내</span><span className="lg2">D-30 이내</span><span className="lg3">30일 초과</span></span>
      ) : null}
    </div>
  );
}

function R9Fresh({ stamp = '기준 2026-08-23 16:25 KST', stale = false, updated = false }) {
  return (
    <span className="fresh">
      <span className={stale ? 'stamp stale' : 'stamp'}>{stamp}</span>
      {updated ? <span className="upd">갱신됨</span> : null}
    </span>
  );
}

/** The window footer: what one click adds, what is left, and the way back. */
function R9More({ step = 15, rest = 371, collapse = false }) {
  return (
    <div className="more">
      <button type="button" className="btn">{step}건 더 보기</button>
      <span className="rest">남은 {rest}건</span>
      {collapse ? <button type="button" className="flat">처음 15건으로 접기</button> : null}
    </div>
  );
}

Object.assign(window, { R9_ROWS, R9_OPEN_NOW, R9_TBD, R9Row, R9Rows, R9Tabs, R9Meta, R9Fresh, R9More, R9_TABS, dart });
