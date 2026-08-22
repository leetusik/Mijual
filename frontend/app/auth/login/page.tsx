import { redirect } from "next/navigation";
import { AuthPanel } from "@/components/auth";
import { ROUTES } from "@/lib/routes";
import { readAuthState } from "@/lib/session.server";

/**
 * `/auth/login` — R5-1's one panel with its two modes.
 *
 * The path is the chrome's own (`lib/routes.ts`: the nav's 로그인 slot has
 * pointed here since `P5.S11`, and `/auth/…` is fixed by the backend's
 * `mijual.web.auth.RESET_PATH`), so this file finally gives that link a page.
 *
 * ## An already-authenticated visit redirects to 내 포트폴리오
 *
 * R5 draws four auth states — idle · 확인 중 · 오류 · **로그인됨** — and the
 * fourth is not a rendering of this panel: 로그인됨 *is* the 2층. There is no
 * signed logged-in variant of the auth screen, and inventing one (a "이미
 * 로그인되어 있습니다" line, a 로그아웃 button beside the form) would be writing
 * copy and a control the round does not have. So a reader who already has a
 * session is sent where the panel would have sent them, and the redirect is what
 * makes the chrome's slot behave for `P5.S16` too.
 *
 * Reading the session is a server-side read that forwards the request's own
 * cookie (`P5.S10` note 13 — `credentials` does nothing in Node), and it opts
 * this route into request-time rendering, which a session-dependent page must be.
 */
export default async function LoginPage() {
  const auth = await readAuthState();
  if (auth.authenticated) redirect(ROUTES.portfolio);

  return <AuthPanel />;
}
