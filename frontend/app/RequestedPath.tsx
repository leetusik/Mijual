"use client";

import { usePathname } from "next/navigation";
import styles from "./not-found.module.css";

/**
 * The address the reader asked for, echoed on the not-found surface (R10 §8).
 *
 * A client component because that is the documented way to render the current
 * path on `not-found.tsx`: the file is a Server Component that Next renders both
 * for a segment's own `notFound()` and for any unmatched URL, and it takes no
 * props — "if you need to use Client Component hooks like `usePathname` to
 * display content based on the path, you must fetch data on the client-side
 * instead" (`next/dist/docs/01-app/03-api-reference/03-file-conventions/
 * not-found.md`).
 *
 * It renders the **path only**, never the query string: `?token=…` and friends
 * belong to no screen, least of all one that says something went wrong.
 */
export function RequestedPath() {
  const pathname = usePathname();
  if (!pathname) return null;
  return <p className={styles.path}>{pathname}</p>;
}
