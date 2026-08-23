import React, { useEffect, useRef, useState } from 'react';
// Citation affordance — per FIELD, not per card. quote is verbatim, never re-punctuated.
// R10 re-cut (P8.S6): the mono [근거] word stays (the provenance line names it), the target is
// a real one (32px desktop / 44px ≤767px), and the quote opens as an OVERLAY popover instead of
// an inline panel — the row it belongs to does not move, so a reader scanning values never
// loses their place. Close = × in the popover, click outside, or Esc. No 「닫기」 word invented.
const CITE_CSS = `
.mj-cite-wrap{position:relative;display:inline-block;max-width:100%}
.mj-cite{font-family:var(--font-mono);font-size:var(--text-xs);font-weight:500;line-height:1;color:var(--live);background:none;border:0;padding:8px 6px;margin:-8px -2px;min-height:32px;display:inline-flex;align-items:center;cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px}
.mj-cite:hover,.mj-cite-hover .mj-cite{background:var(--live-tint);text-decoration:none}
.mj-cite:focus-visible,.mj-cite-focus .mj-cite{outline:2px solid var(--focus-ring);outline-offset:0;text-decoration:none}
.mj-cite[aria-expanded="true"]{background:var(--live-tint);text-decoration:none}
.mj-pop{position:absolute;z-index:40;top:calc(100% + 6px);left:0;width:380px;max-width:min(380px,calc(100vw - 32px));background:#0e1a15;border:1px solid var(--border-strong);border-left:2px solid var(--live);box-shadow:var(--panel-glow);padding:10px 12px 8px;text-align:left}
.mj-pop .h{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.mj-pop .t{display:block;white-space:pre-wrap;word-break:break-all;max-height:200px;overflow-y:auto;font-size:var(--text-sm);line-height:var(--leading-base);color:var(--ink-1)}
.mj-pop .x{font-family:var(--font-mono);font-size:var(--text-sm);color:var(--ink-3);background:none;border:0;width:28px;height:28px;flex:0 0 28px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer}
.mj-pop .x:hover{color:var(--ink-1)}
.mj-pop .l{font-family:var(--font-mono);font-size:var(--text-xs);color:var(--live);text-decoration:none;display:inline-flex;align-items:center;min-height:32px;margin-top:6px;white-space:nowrap}
@media (max-width:767px){
 .mj-cite{min-height:44px;padding:13px 8px;margin:-8px -4px}
 .mj-pop{left:auto;right:0;width:calc(100vw - 44px);max-width:340px}
 .mj-pop .x{width:44px;height:44px;flex:0 0 44px}
 .mj-pop .l{min-height:44px;width:100%;justify-content:center;border:1px solid var(--border-soft);margin-top:8px}
}
/* the same declarations for a 390px frame rendered inside a wide review card */
.m390 .mj-cite{min-height:44px;padding:13px 8px;margin:-8px -4px}
.m390 .mj-pop{left:auto;right:0;width:320px;max-width:320px}
.m390 .mj-pop .x{width:44px;height:44px;flex:0 0 44px}
.m390 .mj-pop .l{min-height:44px;width:100%;justify-content:center;border:1px solid var(--border-soft);margin-top:8px}
`;
if (typeof document !== 'undefined' && !document.getElementById('mj-cite-css')) {
  const el = document.createElement('style');
  el.id = 'mj-cite-css';
  el.textContent = CITE_CSS;
  document.head.appendChild(el);
}
export function Citation({ rceptNo, quote, label = '근거', defaultExpanded = false }) {
  const [open, setOpen] = useState(defaultExpanded);
  const wrap = useRef(null);
  const url = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + rceptNo;
  useEffect(() => {
    if (!open) return;
    const away = (e) => { if (wrap.current && !wrap.current.contains(e.target)) setOpen(false); };
    const key = (e) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('mousedown', away);
    document.addEventListener('keydown', key);
    return () => { document.removeEventListener('mousedown', away); document.removeEventListener('keydown', key); };
  }, [open]);
  return (
    <span className="mj-cite-wrap" ref={wrap}>
      <button type="button" className="mj-cite" aria-expanded={open} onClick={() => setOpen(!open)}>[{label}]</button>
      {open && (
        <span className="mj-pop" role="dialog">
          <span className="h">
            <span className="t">{quote}</span>
            <button type="button" className="x" aria-label={label} onClick={() => setOpen(false)}>×</button>
          </span>
          <a className="l" href={url} target="_blank" rel="noreferrer">DART 원문 {rceptNo} ↗</a>
        </span>
      )}
    </span>
  );
}
