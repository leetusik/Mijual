import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { NotificationsView } from "@/components/portfolio";
import { ApiError, getNotifications } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import type { Notifications } from "@/lib/types";
import styles from "@/components/portfolio/Portfolio.module.css";

/**
 * `/portfolio/notifications` — 알림 설정 (R5-5, R5-7).
 *
 * The account menu's second destination (R5-6: "메뉴 구성: 내 포트폴리오 / **알림
 * 설정** / 로그아웃"), on the API's own noun for the same settings and inside the
 * layer's own path — one gate covers the whole 2층, and `isActiveRoute` keeps
 * this inside 내 포트폴리오.
 *
 * The gate is the same one `/portfolio` uses and for the same reason: the service
 * is the authority on whether there is a session, so a `401` — not a second rule
 * here — is what sends a reader to the 로그인 panel. The defaults are served, not
 * assumed: an account that has never saved a setting gets 7일 + 1일 from
 * `portfolio.DEFAULT_LEAD_DAYS`, and an empty selection is a stored setting that
 * means no mail (`P5.S8` note 9).
 *
 * **샘플 모드 never reaches this page**: R5-4 hides 알림 설정 in the sample ("샘플
 * 에서 알림 설정 숨김" — there is no address to send to), and the account menu
 * that links here is not rendered at all while a sample is loaded. A direct visit
 * without a session is the ordinary gate.
 */
export default async function NotificationsPage() {
  const cookie = (await cookies()).toString();
  const headers = cookie ? { cookie } : undefined;

  let notifications: Notifications | null = null;
  try {
    notifications = await getNotifications({ headers });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
  }
  if (notifications === null) redirect(ROUTES.login);

  return (
    // R13 §3's column is the canon's narrower one (620px), stated at a
    // specificity the shared `content` width cannot outrank in either bundle
    // order (`P8.S9`'s lesson). The rail and the `h1` are the view's own — they
    // are the column's first row and its title, not page chrome.
    <main className={`content ${styles.page} ${styles.narrow}`}>
      <NotificationsView notifications={notifications} />
    </main>
  );
}
