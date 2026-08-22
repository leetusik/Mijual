/**
 * 갈 곳 — turning the agent's destination **kinds** into this app's own routes.
 *
 * The server deliberately serves no href: `mijual.agent.loop._links` composes
 * `{kind, rcept_no?}` from the filings the turn actually read, and its docstring
 * says why — "Serving a filing number and a destination kind keeps one owner for
 * every route and makes it impossible for the agent to point at a page that does
 * not exist." That owner is `lib/routes.ts` (and `lib/api.ts`'s `dartUrl` for
 * DART), so this module is the single mapping and no component builds a path.
 *
 * ⚠ `mijual.agent.copy.BOARD_POINTER_HREF` (`"/board"`) is a **dead route** —
 * `ROUTES.board` is `"/"` and there is no `app/board/` (P6 note 20's nit). It is
 * never read here and must never be rendered: a `board` link resolves through
 * `ROUTES` like every other one.
 *
 * An unrecognised kind is **dropped rather than rendered**: a 갈 곳 link that
 * cannot be routed would be a link to nowhere, which is worse than the missing
 * destination a reviewer can see. The kinds are a closed set on the server.
 */

import { dartUrl } from "@/lib/api";
import type { AskLink } from "@/lib/ask";
import { ROUTES, eventPath } from "@/lib/routes";
import {
  BOARD_LABEL_KO,
  EVENT_DETAIL_KO,
  STOCKS_LABEL_KO,
  dartSourceLabel,
} from "./copy";

export type ResolvedLink = {
  key: string;
  href: string;
  label: string;
  /** DART is another site; everything else is this app. */
  external: boolean;
};

export function resolveLink(link: AskLink): ResolvedLink | null {
  switch (link.kind) {
    case "dart":
      return link.rcept_no
        ? {
            key: `dart:${link.rcept_no}`,
            href: dartUrl(link.rcept_no),
            label: dartSourceLabel(link.rcept_no),
            external: true,
          }
        : null;
    case "event":
      return link.rcept_no
        ? {
            key: `event:${link.rcept_no}`,
            href: eventPath(link.rcept_no),
            label: EVENT_DETAIL_KO,
            external: false,
          }
        : null;
    case "board":
      return { key: "board", href: ROUTES.board, label: BOARD_LABEL_KO, external: false };
    case "stocks":
      return { key: "stocks", href: ROUTES.stocks, label: STOCKS_LABEL_KO, external: false };
    default:
      return null;
  }
}

export function resolveLinks(links: readonly AskLink[]): ResolvedLink[] {
  const seen = new Set<string>();
  const resolved: ResolvedLink[] = [];
  for (const link of links) {
    const item = resolveLink(link);
    if (!item || seen.has(item.key)) continue;
    seen.add(item.key);
    resolved.push(item);
  }
  return resolved;
}
