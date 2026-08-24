/* R13 (P8.S12) — shared parts + every string 보유 종목 and 알림 설정 render.
   Copy is transcribed from `frontend/components/portfolio/copy.ts` (itself transcribed
   from the landed R5/R5-3…R5-8 record) and, for the offer band, from R12's
   `../account/r12-parts.jsx`. **This round mints no Korean** — see result.md §Copy.
   Data is the live sample payload walked for the R13 handoff (SSR markup of
   `/portfolio`, anonymous = 샘플 모드, 2026-08-24) plus P7's browser-measured geometry;
   values the walk did not carry render as ⋯ (R11's convention), never invented.
   Geometry lives in r13-portfolio.css. Names are prefixed `P`/`p`. */

const DSP = window.MijualDesignSystem_7ce1bb;
const { RightsChip: PChip, DDay: PDDay, EstimateMarker: PEst, StateBadge: PState } = DSP;

const pf = (n) => n.toLocaleString('ko-KR');

/* ------------------------------------------------------------- 서명된 카피 (R5) */
const P_COL_STOCK = '종목';
const P_COL_SHARES = '보유량';
const P_RIGHTS_SECTION = '진행 중인 권리';
const P_EDIT = '수정';
const P_DELETE = '삭제';
const P_SAVE = '저장';
const P_CANCEL = '취소';
const P_UNDO = '되돌리기';
const P_UNIT = '주';
const P_HOLDING_LABEL = '보유 주식 수';
const P_HOLDING_CAPTION = '계정에 저장 · 마감 알림의 기준';
const P_ADD_SECTION = '종목 추가';
const P_ADD_SUBMIT = '담기';
const P_KEEP = '담기';
const P_DISCARD = '담지 않기';
const P_SEARCH_PLACEHOLDER = '종목명 또는 종목코드';
const P_MIGRATE_LABEL = '계정 이전';
const P_EMPTY_TITLE = '보유 종목이 비어 있습니다';
const P_EMPTY_BODY = '종목과 보유량을 등록하면, 진행 중인 권리와 마감을 여기서 지켜보고 이메일로 알립니다.';
const pCarryOver = (stock, shares) => `조회에서 입력한 ${stock} ${shares}주가 이 세션에 남아 있습니다`;
const P_UPCOMING = '다가오는 마감';
const P_PAST = '지나간 마감';
const pReference = (date) => `기준 ${date} (KST)`;
const pPastPeriod = (dday) => `기간 지남 · ${dday}`;
const pPastNotice = (dday) => `통지 마감 지남 · ${dday}`;
const pPerHolding = (shares) => `${shares}주 기준`;
const P_MISSED_DETAIL = '놓친 돈 상세 →';
const P_CLAIM_CHECK = '청약·매도로 챙겼습니다';
const P_MISSED_LABEL = '놓친 돈';
const P_CLAIMED_LABEL = '챙긴 돈';
const P_CLAIM_CAP_ACCOUNT = '본인 표시 · 계정에 저장';
const P_CLAIM_CAP_LOCAL = '본인 표시';
const P_STEP_DEPENDENCY = '1단계에서 반대의사를 통지한 주주만 행사 가능';
const P_SAMPLE_BANNER = '샘플 보유 종목 — 구성 예시입니다. 종목·공시·마감은 실제, 계정·보유량은 예시입니다.';
const P_NOTIFY_TITLE = '마감 임박 이메일';
const P_ADDRESS_LABEL = '수신 주소';
const P_CHANGE = '변경';
const P_LEAD_DAYS = [{ days: 7, label: '7일 전' }, { days: 3, label: '3일 전' }, { days: 1, label: '1일 전' }, { days: 0, label: '당일' }];
const P_KAKAO = 'KakaoTalk';
const P_PLANNED = '예정';
const P_KAKAO_NOTE = '준비되면 이 자리에서 켤 수 있습니다';
const P_LOGOUT = '로그아웃';
const P_DELETE_ACCOUNT = '계정 삭제';
const P_DELETE_ACCOUNT_NOTE = '계정을 삭제하면 이메일 주소를 즉시 지웁니다 — 남는 것이 없습니다.';
const P_PORTFOLIO_LABEL = '보유 종목';
/* R12에서 물려받은 오류 줄 (finding 13): `invalid_email`이 P8.S11 이후 매핑을 갖는다 */
const P_ERR_EMAIL = '이메일 주소 형식이 올바르지 않습니다.';
/* R12의 전환 제안 밴드 — 문장은 R12의 것, 그대로. Q-E: 샘플 표면에서는 리드 줄
   「이 보유량은 탭을 닫으면 사라집니다」를 쓰지 않는다 — 샘플 편집은 localStorage에
   남으므로 그 문장은 여기서 거짓이다 (Q-D: 영구 편집 수용). 밴드는 리드 없이 본문 +
   CTA + 닫기로 선다. 새 카피 없음. */
const P_CONV_BODY = '계정에 저장하면 마감이 다가올 때 이메일로 알립니다.';
const P_CONV_CTA = '저장하고 알림 받기';
const P_DISMISS = '닫기';

/* ---------------------------------------------------------- 표본 데이터 (실측 walk) */
const P_REF = '2026-08-24';

/* 보유 종목 4건. `rights.next`는 서버가 이미 직렬화한 카운트다운 — 아래 D-day 행과
   같은 값이다 (P5.S8 `_rights_summary`). 종목코드는 walk가 싣지 않아 렌더하지 않는다. */
const P_HOLDINGS = [
  { code: '00102618', name: '계양전기', shares: 500, next: { type: 1, label: '증서 매매 마감', days: 1, date: '2026-08-25' } },
  { code: '00113058', name: '대동기어', shares: 300, next: { type: 2, label: '전환청구 개시', days: 61, date: '2026-10-24' } },
  { code: '00162461', name: '한화솔루션', shares: 500, next: null },
  { code: '00133618', name: '세기상사', shares: 100, next: null },
];

/* 다가오는 마감 — D-day 오름차순 (서버 순서) */
const P_UPCOMING_ROWS = [
  {
    id: 'ky-r1', type: 1, name: '계양전기', label: '증서 매매 마감', days: 1, date: '2026-08-25',
    cells: [
      { lab: '보유', val: '500주' },
      { lab: '배정비율 (1주당)', val: '0.2314082845', ratio: true },
      { lab: '배정 신주', val: '115주', sub: '= 500주 × 0.2314082845 · 1주 미만 버림' },
      { lab: '환산액', chip: '발행가 확정 전', sub: '확정 예정일 ⋯' },
    ],
  },
  {
    id: 'dd-r2', type: 2, name: '대동기어', label: '전환청구 개시', days: 61, date: '2026-10-24',
    cells: [
      { lab: '전환가액', val: '15,552원' },
      { lab: '전환 시 주식수', val: '⋯' },
      { lab: '오버행', val: '6.68%' },
    ],
  },
];

/* 지나간 마감 — 최근순. ① 소멸 금액은 lib/holding.ts의 곱셈 한 자리에서 나온 값이고
   조회 breakdown과 같은 수치다 (수치 불일치 금지). alert 색은 금액에만, 칩에는 없다. */
const P_PAST_ROWS = [
  {
    id: 'hs-r1', type: 1, name: '한화솔루션', label: '증서 매매 마감', dday: 'D+45', date: '2026-07-10',
    money: { value: '679,575원', basis: pPerHolding('500'), cap: '배정 123주 × 「추정」5,525원' }, claimKey: true,
  },
  {
    id: 'dd-r1', type: 1, name: '대동기어', label: '증서 매매 마감', dday: 'D+47', date: '2026-07-08',
    money: { value: '446,720원', basis: pPerHolding('300'), cap: null }, claimKey: true,
  },
  { id: 'sg-r3', type: 3, name: '세기상사', label: '반대의사 통지 마감', dday: 'D+49', date: '2026-07-06', notice: true, dependency: true },
];

/* --------------------------------------------------------------------------- 파트 */
function PBk() { return <i className="bk" aria-hidden="true"></i>; }
function PPanel({ children, as, style }) { const T = as || 'section'; return <T className="panel" style={style}>{children}<PBk /></T>; }
function PLab({ children }) { return <div className="lab">{children}</div>; }
function PSec({ title, children }) { return <section className="psec"><h2 className="peyebrow">{title}</h2>{children}</section>; }

function PBanner() { return <p className="pban">{P_SAMPLE_BANNER}</p>; }

/* 보유 종목 — 4열, 내용과 무관한 트랙. 편집은 보유량 셀 + 액션 열의 제자리 교체다. */
function PHoldings({ rows, mode, editing, undo, onEdit, onCancel, onSave, onDelete, onUndo, busy }) {
  const [digits, setDigits] = React.useState('');
  React.useEffect(() => {
    const row = rows.find((r) => r.code === editing);
    if (row) setDigits(String(row.shares));
  }, [editing, rows]);
  return <PPanel>
    <ul className="phold">
      <li className="phrow phhead" aria-hidden="true"><span>{P_COL_STOCK}</span><span>{P_COL_SHARES}</span><span>{P_RIGHTS_SECTION}</span><span></span></li>
      {rows.map((row) => {
        const open = editing === row.code;
        return <li className="phrow" key={row.code}>
          <div className="phstock"><p className="phname">{row.name}</p></div>
          {open
            ? <div className="pedit">
                <input className="penum f" aria-label={P_HOLDING_LABEL} inputMode="numeric" value={digits}
                  onChange={(e) => setDigits(e.target.value.replace(/[^0-9]/g, ''))} autoFocus />
                {mode === 'account' ? <span className="pclaimcap">{P_HOLDING_CAPTION}</span> : null}
              </div>
            : <p className="phval mono">{pf(row.shares)}<span className="u">{P_UNIT}</span></p>}
          <div className="phrights">
            {row.next
              ? <React.Fragment>
                  <PChip type={row.next.type} compact />
                  <span className="prlab">{row.next.label}</span>
                  <span className="phdday">
                    {row.next.days === null ? <PState state="tbd" /> : <PDDay days={row.next.days} date={row.next.date} />}
                  </span>
                </React.Fragment>
              : <span className="pslot" aria-hidden="true"></span>}
          </div>
          <div className="pacts">
            {open
              ? <React.Fragment>
                  <button className="pact pri" type="button" disabled={busy} onClick={() => onSave && onSave(row, digits)}>{P_SAVE}</button>
                  <button className="pact" type="button" onClick={onCancel}>{P_CANCEL}</button>
                </React.Fragment>
              : <React.Fragment>
                  <button className="pact" type="button" disabled={busy} onClick={() => onEdit && onEdit(row.code)}>{P_EDIT}</button>
                  <button className="pact" type="button" disabled={busy} onClick={() => onDelete && onDelete(row)}>{P_DELETE}</button>
                </React.Fragment>}
          </div>
        </li>;
      })}
      {undo
        ? <li className="pundo">
            <span className="pundoname">{undo.name} <span className="mono">{pf(undo.shares)}</span>{P_UNIT}</span>
            <button className="pact" type="button" onClick={onUndo}>{P_UNDO}</button>
          </li>
        : null}
    </ul>
  </PPanel>;
}

/* 종목 추가 — 계정 모드에만. R4 서명 프리미티브(모노 우측정렬 · 프리셋 칩) 그대로. */
function PAdd({ value, shares, note, preselect }) {
  const [n, setN] = React.useState(shares === undefined ? 500 : shares);
  return <PPanel>
    <div className="padd">
      <div className="pafield">
        <label className="palbl" htmlFor="padd-q">{P_COL_STOCK}</label>
        <input id="padd-q" className={'painput' + (preselect ? ' f' : '')} placeholder={P_SEARCH_PLACEHOLDER} defaultValue={value || ''} />
      </div>
      <div className="pafield">
        <label className="palbl" htmlFor="padd-n">{P_HOLDING_LABEL}</label>
        <div className="psharesrow">
          <input id="padd-n" className="pnum" inputMode="numeric" value={n ? pf(n) : ''}
            onChange={(e) => setN(parseInt(e.target.value.replace(/[^0-9]/g, ''), 10) || 0)} />
          <span className="punit">{P_UNIT}</span>
          <div className="ppresets">{[100, 500, 1000].map((v) =>
            <button key={v} className="ppreset" type="button" aria-pressed={n === v} onClick={() => setN(v)}>{pf(v)}{P_UNIT}</button>)}</div>
        </div>
      </div>
      <button className="pasubmit" type="button">{P_ADD_SUBMIT}</button>
    </div>
    {note ? <p className="paline">{note}</p> : null}
    <p className="pafoot">{P_HOLDING_CAPTION}</p>
  </PPanel>;
}

/* 이월 (R5-3) · 이전 (R5-4) — 같은 티어, 같은 약속: 제안일 뿐이고 담지 않기는
   브라우저의 값을 지우지 않는다. */
function PCarry({ variant, entries }) {
  return <div className="pcarry">
    {variant === 'migrate' ? <p className="pcarrylab">{P_MIGRATE_LABEL}</p> : null}
    <ul className="pcarrylist">{entries.map((e) =>
      <li className="pcarryrow" key={e.code}>
        {variant === 'session'
          ? pCarryOver(e.name, pf(e.shares))
          : <React.Fragment>{e.name} <span className="mono">{pf(e.shares)}</span>{P_UNIT}</React.Fragment>}
      </li>)}</ul>
    <div className="pcarryacts">
      <button className="pact pri" type="button">{P_KEEP}</button>
      <button className="pact" type="button">{P_DISCARD}</button>
    </div>
  </div>;
}

function PEmpty() {
  return <PPanel><div className="pempty">
    <p className="pemptytitle">{P_EMPTY_TITLE}</p>
    <p className="pemptybody">{P_EMPTY_BODY}</p>
  </div></PPanel>;
}

/* ------------------------------------------------------------------- D-day 목록 */
function PCells({ cells }) {
  return <div className="pdcells">{cells.map((c, i) =>
    <div className="pdcell" key={i}>
      <p className="pdclab">{c.lab}</p>
      <p className="pdcval">
        {c.chip ? <span className="pdpend">{c.chip}</span> : null}
        {c.val ? <span className={'v' + (c.ratio ? ' ratio' : '')}>{c.val}</span> : null}
      </p>
      {c.sub ? <p className="pdclab">{c.sub}</p> : null}
    </div>)}</div>;
}

function PDRow({ row, past, claimed, onClaim, caption }) {
  const money = row.money;
  return <li className="pdrow">
    <span className="pdchip"><PChip type={row.type} compact /></span>
    <p className="pdname">{row.name}</p>
    <p className="pdlab">{row.label}</p>
    <div className="pdday">
      {past
        ? <React.Fragment>
            <span className="ppastchip">{row.notice ? pPastNotice(row.dday) : pPastPeriod(row.dday)}</span>
            <p className="ppastdate">{row.date}</p>
          </React.Fragment>
        : <PDDay days={row.days} date={row.date} />}
    </div>
    {row.cells ? <PCells cells={row.cells} /> : null}
    {row.dependency ? <p className="pdep">{P_STEP_DEPENDENCY}</p> : null}
    {money
      ? <React.Fragment>
          <div className="pdmoney">
            <p className="pmlead">
              <span className={'pmlabel' + (claimed ? ' claimed' : '')}>{claimed ? P_CLAIMED_LABEL : P_MISSED_LABEL}</span>
              <span className="pmbasis">{money.basis}</span>
              {claimed ? null : <a className="pgo" href="#">{P_MISSED_DETAIL}</a>}
            </p>
            <span className="pmval"><PEst value={money.value} color={claimed ? 'var(--live)' : 'var(--alert)'} /></span>
            {money.cap ? <p className="pclaimcap">{money.cap}</p> : null}
          </div>
          <div className="pdfoot">
            {row.claimKey
              ? <label className="pclaimlab">
                  <input type="checkbox" checked={!!claimed} onChange={(e) => onClaim && onClaim(row, e.target.checked)} />
                  {P_CLAIM_CHECK}
                </label>
              : null}
          </div>
          {row.claimKey ? <p className="pclaimcap pdcap">{caption === 'account' ? P_CLAIM_CAP_ACCOUNT : P_CLAIM_CAP_LOCAL}</p> : null}
        </React.Fragment>
      : null}
  </li>;
}

/* 두 섹션 + 앵커 한 줄. 앵커는 블록의 것 (finding 3): 지나간 D+n도 같은 기준일로
   계산된 값이므로 한 번만, 섹션 밖에 선다. */
function PDeadlines({ reference, upcoming, past, claims, onClaim, caption }) {
  const is = (id) => !!(claims && claims[id]);
  return <div className="pdblock">
    <p className="pdanchor">{pReference(reference)}</p>
    {upcoming.length ? <PSec title={P_UPCOMING}><PPanel><ul className="pdrows">
      {upcoming.map((row) => <PDRow key={row.id} row={row} past={false} caption={caption} />)}
    </ul></PPanel></PSec> : null}
    {past.length ? <PSec title={P_PAST}><PPanel><ul className="pdrows">
      {past.map((row) => <PDRow key={row.id} row={row} past claimed={is(row.id)} onClaim={onClaim} caption={caption} />)}
    </ul></PPanel></PSec> : null}
  </div>;
}

/* R12의 전환 제안 밴드 — ../account/r12-auth.css의 `.aoffer` 그대로. 데이터 패널보다
   한 티어 아래(inset, 브래킷 없음), 게이트 아님, 닫기 있음, 숫자 위에 서지 않는다. */
function POffer({ onDismiss }) {
  return <div className="aoffer">
    <div className="aohead">
      <p className="aobody">{P_CONV_BODY}</p>
      <button className="aodismiss" type="button" onClick={onDismiss}>{P_DISMISS}</button>
    </div>
    <a className="aocta" href="#">{P_CONV_CTA}</a>
  </div>;
}

/* ----------------------------------------------------------------------- 알림 설정 */
function PNotify(p) {
  const [lead, setLead] = React.useState(p.lead || [7, 1]);
  const editing = !!p.editing;
  const toggle = (d) => setLead(lead.includes(d) ? lead.filter((x) => x !== d) : [...lead, d]);
  return <div className="pncol">
    {p.bare ? null : <nav className="pnrail"><a href="#">{'← ' + P_PORTFOLIO_LABEL}</a></nav>}
    <PPanel>
      <div className="pnp">
        <h1 className="pnh1">{P_NOTIFY_TITLE}</h1>
        <div className="pnrow">
          <span className="pnlab">{P_ADDRESS_LABEL}</span>
          {editing
            ? <React.Fragment>
                <input className={'pnemail' + (p.focus ? ' f' : '')} type="email" defaultValue={p.draft || p.address} />
                <span className="pacts">
                  <button className="pact pri" type="button" disabled={!!p.busy}>{P_SAVE}</button>
                  <button className="pact" type="button">{P_CANCEL}</button>
                </span>
              </React.Fragment>
            : <React.Fragment>
                <span className="pnval mono">{p.address}</span>
                <button className="pact" type="button" disabled={!!p.busy}>{P_CHANGE}</button>
              </React.Fragment>}
          {p.error ? <p className="pnerr" role="status">{P_ERR_EMAIL}</p> : null}
        </div>
        <div className="pchips">{P_LEAD_DAYS.map((c) =>
          <button key={c.days} className="pchip" type="button" aria-pressed={lead.includes(c.days)}
            disabled={!!p.busy} onClick={() => toggle(c.days)}>{c.label}</button>)}</div>
        <div className="pnrow">
          <span className="pnlab">{P_KAKAO}</span>
          <span className="pnnote">{P_KAKAO_NOTE}</span>
          <span className="pplanned">{'「' + P_PLANNED + '」'}</span>
        </div>
        <div className="pnrow">
          <span className="pnlab"></span><span></span>
          <button className="pact wide" type="button" disabled={!!p.busy}>{P_LOGOUT}</button>
        </div>
        <div className="pnrow">
          <span className="pnlab"></span><span></span>
          <span className="pacts">
            <button className={'pact wide' + (p.armed ? ' armed' : '')} type="button" disabled={!!p.busy}>{P_DELETE_ACCOUNT}</button>
            {p.armed ? <button className="pact wide" type="button">{P_CANCEL}</button> : null}
          </span>
        </div>
        {/* 삭제가 무엇을 하는지는 무장된 다음에만 말한다 — 물을 생각이 없는 독자에게 상시로
            삭제의 결과를 읽힐 이유가 없고, 무장한 독자는 두 번째 누름 전에 이것을 읽는다. */}
        {p.armed ? <p className="pnfoot">{P_DELETE_ACCOUNT_NOTE}</p> : null}
      </div>
    </PPanel>
  </div>;
}
