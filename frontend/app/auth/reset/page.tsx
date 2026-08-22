import { redirect } from "next/navigation";
import { connection } from "next/server";
import { ResetConfirmPanel } from "@/components/auth";
import { ROUTES } from "@/lib/routes";

/**
 * `/auth/reset?token=…` — the page the emailed 재설정 link lands on.
 *
 * Neither the path nor the parameter is this slice's choice:
 * `mijual.web.auth.RESET_PATH` already builds the link as
 * `{MIJUAL_APP_BASE_URL}/auth/reset?token=…` and mails it (through the dev
 * console transport until P4 plugs in a real `Mailer`), so the page reads `?token=`
 * rather than a path segment.
 *
 * **A visit with no token is not a surface.** The token *is* the credential, and
 * R5 signs no copy for a reset page without one — so the reader goes to the panel
 * they can act on, which is also where a fresh link is requested. A redirect
 * writes no Korean; a "링크가 올바르지 않습니다" page would.
 *
 * The token is handed to a client component and **never rendered**: it is a
 * credential, and it leaves this app only in the body of `POST /auth/reset/confirm`.
 *
 * `connection()` marks the route request-time, so `next build` prerenders no page
 * that would otherwise bake a `searchParams` read into a static shell.
 */
export default async function ResetPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string | string[] }>;
}) {
  await connection();
  const params = await searchParams;
  const raw = Array.isArray(params.token) ? params.token[0] : params.token;
  const token = raw?.trim() ?? "";

  if (token === "") redirect(ROUTES.login);

  return <ResetConfirmPanel token={token} />;
}
