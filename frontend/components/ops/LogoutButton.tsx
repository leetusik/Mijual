"use client";

import { useState } from "react";
import { opsLogout } from "@/lib/api";
import { OPS_ROOT } from "./routes";
import { LOGOUT_KO } from "./copy";
import styles from "./Ops.module.css";

/**
 * 로그아웃 — immediate, and it leaves through a **fresh document load**.
 *
 * The operator session is a row: `POST /ops/logout` deletes it, so the `mj_ops`
 * cookie is worthless the instant the call returns. The reason this navigates
 * with `location.assign` rather than the client router is the one `P5.S16`
 * recorded for the reader's own 로그아웃 — every panel the client cached was
 * served to a session that no longer exists, and a Back press must not restore
 * one. Landing on `/ops` renders the door, because the session is gone.
 */
export function LogoutButton() {
  const [leaving, setLeaving] = useState(false);

  return (
    <button
      type="button"
      className={styles.logout}
      disabled={leaving}
      onClick={() => {
        setLeaving(true);
        opsLogout()
          .catch(() => {
            /* Idempotent on the server too: the cookie is cleared either way, so
               the honest thing is still to leave. */
          })
          .finally(() => window.location.assign(OPS_ROOT));
      }}
    >
      {LOGOUT_KO}
    </button>
  );
}
