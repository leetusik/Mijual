/* R12 (P8.S10) — shared parts + every string the auth surfaces and the conversion
   moments render. Copy is transcribed from `frontend/components/auth/copy.ts` (which is
   itself transcribed from the landed R5 record); the four A_NEW_* strings are this
   round's dated exceptions (2026-08-24) and are listed in result.md with their reasons.
   Geometry lives in r12-auth.css. Names are prefixed `A` so this file can load beside
   ../lookup/r11-parts.jsx in the Offers card. */

/* ---------------------------------------------------------------- 서명된 카피 (R5) */
const A_LOGIN = '로그인';
const A_SIGNUP = '계정 만들기';
const A_LOGIN_INTRO = '가입한 이메일과 비밀번호로 로그인합니다.';
const A_SIGNUP_INTRO = '이메일과 비밀번호만으로 만듭니다 — 만들어지면 바로 로그인됩니다.';
const A_EMAIL = '이메일';
const A_PW = '비밀번호';
const A_PENDING = '확인 중…';
const A_LOGOUT = '로그아웃되었습니다';
const A_ERR_CRED = '이메일 또는 비밀번호가 일치하지 않습니다.';
const A_ERR_TAKEN = '이미 가입된 이메일입니다 — 로그인해 주세요.';
const A_ERR_SHORT = '비밀번호는 8자 이상이어야 합니다.';
const A_RESET = '비밀번호 재설정';
const A_RESET_SENT = '재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.';
const A_SAMPLE = '샘플 포트폴리오로 둘러보기';
const A_SAMPLE_SUB = '가입 없이, 실제 공시 4건으로 구성된 예시 포트폴리오를 엽니다 — 클릭 한 번.';
const A_CONV_SESSION = '이 보유량은 탭을 닫으면 사라집니다';
const A_CONV_BODY = '계정에 저장하면 마감이 다가올 때 이메일로 알립니다.';
const A_CONV_CTA = '저장하고 알림 받기';
const A_DISMISS = '닫기';
const A_DEADLINE = '이 마감 알림 받기 →';
const A_ADD = '보유 종목에 담기 →';

/* ------------------------------------------------- 신규 카피 4건 (2026-08-24 예외) */
/* Q-C — R5-1's own rule ("비밀번호 8자 이상(다른 규칙 없음)") stated as the field's
   constraint instead of only as a post-submit error. One token, mono, no sentence. */
const A_NEW_RULE = '8자 이상';
/* Q-A = (b) — noValidate, so the browser's English bubble is gone and these two lines
   answer in the error slot the round already owns. (c) was the handoff's default and
   fails on 계정 만들기: an empty address there maps to `invalid_email`, which has no
   signed Korean, so the reader would meet a submit that does nothing at all. */
const A_NEW_EMPTY = '이메일과 비밀번호를 입력해 주세요.';
const A_NEW_EMAIL = '이메일 주소 형식이 올바르지 않습니다.';
/* finding 3 — `invalid_reset_token` was a recorded gap in copy.ts (an expired or spent
   link answered with no line at all). One sentence, and it names the way out. */
const A_NEW_TOKEN = '이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.';

const A_MIN = 8;
const A_EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

/* ------------------------------------------------------------------------- 파트 */
function ABk() { return <i className="bk" aria-hidden="true"></i>; }
function APanel({ children, style }) { return <section className="panel" style={style}>{children}<ABk /></section>; }
function ALab({ children }) { return <div className="lab">{children}</div>; }
function ACase({ label, children }) { return <div className="case"><ALab>{label}</ALab>{children}</div>; }

function ARail() { return <nav className="arail"><a href="#">← 관제 현황판</a></nav>; }

function AField({ id, label, rule, type, value, focus, onChange, inputRef, autoComplete }) {
  return <div className="afield">
    <div className="alrow">
      <label className="albl" htmlFor={id}>{label}</label>
      {rule ? <span className="arule">{rule}</span> : null}
    </div>
    <input id={id} ref={inputRef} className={'ainput' + (focus ? ' f' : '')} type={type} autoComplete={autoComplete}
      value={value === undefined ? '' : value} onChange={onChange || (() => {})} />
  </div>;
}

function ASample() {
  return <section className="asample">
    <a className="aslink" href="#">{A_SAMPLE}</a>
    <p className="assub">{A_SAMPLE_SUB}</p>
  </section>;
}

/* 로그인 / 계정 만들기 — one panel, two modes, four states. Every state is a prop, so
   the card can draw the ones the walk could not reach without credentials. */
function AAuth(p) {
  const signup = p.mode === 'signup';
  const label = signup ? A_SIGNUP : A_LOGIN;
  const id = p.id || 'a';
  return <div className="acol">
    {p.bare ? null : <ARail />}
    <APanel>
      <div className="ap">
        {p.flash ? <p className="flash" role="status">{A_LOGOUT}</p> : null}
        <div className="ahead">
          <h1 className="ah1">{label}</h1>
          <p className="aintro">{signup ? A_SIGNUP_INTRO : A_LOGIN_INTRO}</p>
        </div>
        <form className="aform" noValidate onSubmit={p.onSubmit || ((e) => e.preventDefault())}>
          <AField id={id + '-em'} label={A_EMAIL} type="email" autoComplete="email"
            value={p.email} focus={p.focus === 'email'} onChange={p.onEmail} inputRef={p.emailRef} />
          <AField id={id + '-pw'} label={A_PW} rule={signup ? A_NEW_RULE : null} type="password"
            autoComplete={signup ? 'new-password' : 'current-password'}
            value={p.pw} focus={p.focus === 'pw'} onChange={p.onPw} />
          <button className={'asubmit' + (p.focus === 'submit' ? ' foc' : '')} type="submit" disabled={!!p.pending}>
            {p.pending ? A_PENDING : label}
          </button>
        </form>
        {p.line ? <p className={'aline' + (p.soft ? ' soft' : '')} role="status">{p.line}</p> : null}
        <div className="aquiet">
          <button className={'aq' + (p.hov === 'mode' ? ' hov' : '')} type="button" onClick={p.onMode}>
            {signup ? A_LOGIN : A_SIGNUP}
          </button>
          {signup ? null : <button
            className={'aq' + (p.hov === 'reset' ? ' hov' : '') + (p.focus === 'reset' ? ' foc' : '')}
            type="button" disabled={!!p.pending} onClick={p.onReset}>{A_RESET}</button>}
        </div>
      </div>
    </APanel>
    {p.bare ? null : <ASample />}
  </div>;
}

/* 인터랙티브 한 벌 — 모드 전환 · 타이핑 · 제출(확인 중… → 오류) · 재설정(주소 없으면
   이메일 칸으로 포커스, 있으면 보냈습니다). 카드의 나머지는 정적 상태 그림이다. */
function AAuthLive() {
  const [mode, setMode] = React.useState('login');
  const [email, setEmail] = React.useState('');
  const [pw, setPw] = React.useState('');
  const [pending, setPending] = React.useState(false);
  const [line, setLine] = React.useState(null);
  const [soft, setSoft] = React.useState(false);
  const emailRef = React.useRef(null);
  const say = (text, isSoft) => { setLine(text); setSoft(!!isSoft); };

  function onSubmit(e) {
    e.preventDefault();
    const signup = mode === 'signup';
    if (!email.trim() || !pw) return say(A_NEW_EMPTY);
    if (!A_EMAIL_RE.test(email.trim())) return say(A_NEW_EMAIL);
    if (signup && pw.length < A_MIN) return say(A_ERR_SHORT);
    say(null);
    setPending(true);
    window.setTimeout(() => { setPending(false); say(signup ? A_ERR_TAKEN : A_ERR_CRED); }, 900);
  }

  function onReset() {
    if (!email.trim()) { if (emailRef.current) emailRef.current.focus(); return; }
    setPending(true);
    window.setTimeout(() => { setPending(false); say(A_RESET_SENT, true); }, 700);
  }

  return <AAuth id="live" mode={mode} email={email} pw={pw} pending={pending} line={line} soft={soft}
    emailRef={emailRef}
    onEmail={(e) => { setEmail(e.target.value); setLine(null); }}
    onPw={(e) => { setPw(e.target.value); setLine(null); }}
    onSubmit={onSubmit} onReset={onReset}
    onMode={() => { setMode(mode === 'signup' ? 'login' : 'signup'); setLine(null); }} />;
}

/* 비밀번호 재설정 (토큰 페이지) — one field, the same four states, no 이메일 칸: the link
   IS the credential, and asking for the address again would imply it could be a
   different one. */
function AReset(p) {
  const id = p.id || 'r';
  return <div className="acol">
    {p.bare ? null : <ARail />}
    <APanel>
      <div className="ap">
        <div className="ahead">
          <h1 className="ah1">{A_RESET}</h1>
        </div>
        <form className="aform" noValidate onSubmit={(e) => e.preventDefault()}>
          <AField id={id + '-pw'} label={A_PW} rule={A_NEW_RULE} type="password" autoComplete="new-password"
            value={p.pw} focus={p.focus === 'pw'} />
          <button className="asubmit" type="submit" disabled={!!p.pending}>{p.pending ? A_PENDING : A_RESET}</button>
        </form>
        {p.line ? <p className={'aline' + (p.soft ? ' soft' : '')} role="status">{p.line}</p> : null}
        {p.back ? <div className="aquiet"><button className="aq" type="button">{A_LOGIN}</button></div> : null}
      </div>
    </APanel>
  </div>;
}

/* 전환 제안 ① — the offer band. inset surface, no brackets: one tier below the panels
   whose number it answers. 닫기 hides it for the page; the session flag has already made
   it a once-per-session offer either way. */
function AOffer({ onDismiss }) {
  return <div className="aoffer">
    <div className="aohead">
      <p className="aolead">{A_CONV_SESSION}</p>
      <button className="aodismiss" type="button" onClick={onDismiss}>{A_DISMISS}</button>
    </div>
    <p className="aobody">{A_CONV_BODY}</p>
    <a className="aocta" href="#">{A_CONV_CTA}</a>
  </div>;
}

/* nav (R8) — shown only for the hierarchy: 로그인 is the quietest of the three moments. */
function ANav({ signedIn }) {
  return <div className="abar">
    <a className="brand" href="#"><img className="wm" src="../assets/mijual-logo-ring-white.png" alt="미주알" /></a>
    <nav className="links"><a href="#">AI 질문</a><a href="#">보유 종목</a></nav>
    <div className="util">{signedIn
      ? <span className="mono" style={{ fontSize: 'var(--text-sm)', color: 'rgba(255,255,255,.82)' }}>reader@example.com ▾</span>
      : <a className="login" href="#">{A_LOGIN}</a>}</div>
  </div>;
}
