# `deploy/edge/` — how `jujutower.conf` reaches the shared edge

`jujutower.com` is served by the **standalone `edge` compose project** on the
Oracle box: pinned `nginx:1.27-alpine`, container `edge-nginx`, sole owner of
`:80` and `:443` for every co-tenant site (changple5, changple.ai, hi2vi,
knowledge, vocky — and now this one). It belongs to no app. Mijual's entire edge
footprint is **one conf file plus one cert pair**.

> **The edge repository is the operator's, and it is not this repo.** It lives at
> `~/projects/personal/edge/` (the tree is the `edge/` directory inside it) and is
> its own git repository. `P4.S4` **copies these files in and applies these edits
> there, and commits nothing in that repo** — the operator commits their own
> repository. Nothing in this folder ever writes to it automatically.

## What lands where

| This repo (authoring home) | The edge repo (live home) |
|---|---|
| `deploy/edge/jujutower.conf` | `conf.d/jujutower.conf` |
| the `validate.sh` diff below | `validate.sh` (`CERT_NAMES`) |
| the `stage.sh` diff below | `stage.sh` (`[2/6]` + `[4/6]`) |
| — | `certs/jujutower.{crt,key}` (staged on the VM by `stage.sh`; **never committed, never local**) |

The cert **source** pair on the box is `/home/opc/jujutower_tls/jujutower.com.crt`
and `.key` (key `600 opc:opc`), mirroring hi2vi's `/home/opc/hi2vi_tls/`. It is a
**Cloudflare Origin CA** certificate for the `jujutower.com` zone — the hi2vi
wildcard does **not** cover this domain, so this is a genuinely new cert
basename, which is exactly why the two scripts need editing at all.

## Step 1 — copy the vhost in

```sh
cp ~/projects/personal/Mijual/deploy/edge/jujutower.conf \
   ~/projects/personal/edge/edge/conf.d/jujutower.conf
```

## Step 2 — apply the two script edits

These are the **exact** diffs, produced and validated against a scratch copy of
the edge tree during `P4.S3` (`./validate.sh` passes over the whole `conf.d/`
tree with them applied — that run is the global-name collision check).

### `validate.sh` — one line, so the local gate mints a dummy pair

```diff
--- a/validate.sh
+++ b/validate.sh
@@ -16,8 +16,10 @@
 cd "$(dirname "$0")"
 
 IMAGE="nginx:1.27-alpine"
-# Exactly the four cert basenames the confs reference under /etc/nginx/certs/.
-CERT_NAMES=(changple5 changple-web hi2vi default)
+# Exactly the five cert basenames the confs reference under /etc/nginx/certs/.
+# `jujutower` is jujutower.com's own Cloudflare Origin CA pair (the hi2vi
+# wildcard does not cover that zone) — added with conf.d/jujutower.conf.
+CERT_NAMES=(changple5 changple-web hi2vi jujutower default)
 
 echo "==> [1/3] dummy certs (generate only if missing — real runs are idempotent)"
 for name in "${CERT_NAMES[@]}"; do
```

### `stage.sh` — the source-cert check, the copy, the count and the pair loop

```diff
--- a/stage.sh
+++ b/stage.sh
@@ -61,6 +61,15 @@
 c=$(openssl x509 -in "$HI.crt" -pubkey -noout | openssl sha256 | awk '{print $NF}')
 k=$(openssl pkey -in "$HI.key" -pubout | openssl sha256 | awk '{print $NF}')
 [ "$c" = "$k" ] && echo "    ok   hi2vi crt/key pair matches" || { echo "FATAL: hi2vi crt/key mismatch" >&2; exit 1; }
+JT=/home/opc/jujutower_tls/jujutower.com
+san_jt=$(openssl x509 -in "$JT.crt" -noout -ext subjectAltName)
+echo "    jujutower origin: $(openssl x509 -in "$JT.crt" -noout -subject -enddate | tr '\n' ' ')"
+echo "$san_jt" | grep -qE 'DNS:jujutower\.com([,[:space:]]|$)' || { echo "FATAL: jujutower cert misses jujutower.com" >&2; exit 1; }
+echo "    ok   covers jujutower.com"
+if echo "$san_jt" | grep -qE 'DNS:(\*|www)\.jujutower\.com'; then echo "    note www/wildcard jujutower.com IS in SAN (www alias available)"; else echo "    note www/wildcard jujutower.com NOT in SAN (www alias would need a new cert)"; fi
+c=$(openssl x509 -in "$JT.crt" -pubkey -noout | openssl sha256 | awk '{print $NF}')
+k=$(openssl pkey -in "$JT.key" -pubout | openssl sha256 | awk '{print $NF}')
+[ "$c" = "$k" ] && echo "    ok   jujutower crt/key pair matches" || { echo "FATAL: jujutower crt/key mismatch" >&2; exit 1; }
 REMOTE
 
 # ── [3/6] rsync the tree (certs excluded, no --delete) ───────────────────────
@@ -69,31 +78,35 @@
 rsync -av -e 'ssh -o BatchMode=yes' --exclude='/certs/*' --exclude='.DS_Store' ./ "$HOST:$REMOTE/"
 echo "    ok   tree synced (local dummy certs never shipped)"
 
-# ── [4/6] stage the 8 real cert paths on the VM ──────────────────────────────
-echo "==> [4/6] stage 8 cert paths into $REMOTE/certs (perms + pair-match verified)"
+# ── [4/6] stage the 10 real cert paths on the VM ─────────────────────────────
+echo "==> [4/6] stage 10 cert paths into $REMOTE/certs (perms + pair-match verified)"
 ssh_vm bash -s <<'REMOTE'
 set -euo pipefail
 cd /home/opc/edge && mkdir -p certs
 C5=/etc/changple5/tls/cloudflare-origin; HI=/home/opc/hi2vi_tls/hi2vi.com
+JT=/home/opc/jujutower_tls/jujutower.com
 for d in changple5 changple-web; do sudo -n cp "$C5.crt" "certs/$d.crt"; sudo -n cp "$C5.key" "certs/$d.key"; done
 cp "$HI.crt" certs/hi2vi.crt; cp "$HI.key" certs/hi2vi.key
+cp "$JT.crt" certs/jujutower.crt; cp "$JT.key" certs/jujutower.key
 if [ ! -f certs/default.crt ] || [ ! -f certs/default.key ]; then
   openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=default.invalid" -keyout certs/default.key -out certs/default.crt >/dev/null 2>&1
 fi
 sudo -n chown opc:opc certs/*.crt certs/*.key
 chmod 644 certs/*.crt; chmod 600 certs/*.key
 n=$(ls certs/*.crt certs/*.key 2>/dev/null | wc -l | tr -d ' ')
-[ "$n" -eq 8 ] || { echo "FATAL: expected 8 cert files, found $n" >&2; exit 1; }
+[ "$n" -eq 10 ] || { echo "FATAL: expected 10 cert files, found $n" >&2; exit 1; }
 scrt=$(sudo -n sha256sum "$C5.crt" | awk '{print $1}'); hcrt=$(sha256sum "$HI.crt" | awk '{print $1}')
+jcrt=$(sha256sum "$JT.crt" | awk '{print $1}')
 [ "$(sha256sum certs/changple5.crt|awk '{print $1}')"   = "$scrt" ] || { echo "FATAL: changple5.crt != source"   >&2; exit 1; }
 [ "$(sha256sum certs/changple-web.crt|awk '{print $1}')" = "$scrt" ] || { echo "FATAL: changple-web.crt != source" >&2; exit 1; }
 [ "$(sha256sum certs/hi2vi.crt|awk '{print $1}')"        = "$hcrt" ] || { echo "FATAL: hi2vi.crt != source"        >&2; exit 1; }
-for name in changple5 changple-web hi2vi default; do
+[ "$(sha256sum certs/jujutower.crt|awk '{print $1}')"    = "$jcrt" ] || { echo "FATAL: jujutower.crt != source"    >&2; exit 1; }
+for name in changple5 changple-web hi2vi jujutower default; do
   c=$(openssl x509 -in "certs/$name.crt" -pubkey -noout | openssl sha256 | awk '{print $NF}')
   k=$(openssl pkey  -in "certs/$name.key" -pubout | openssl sha256 | awk '{print $NF}')
   [ "$c" = "$k" ] || { echo "FATAL: staged $name crt/key mismatch" >&2; exit 1; }
 done
-echo "    ok   8 files staged (644 crt / 600 key, opc:opc), sha256 + pair-match verified"
+echo "    ok   10 files staged (644 crt / 600 key, opc:opc), sha256 + pair-match verified"
 REMOTE
 
 # ── [5/6] on-VM validate.sh ──────────────────────────────────────────────────
```

Two things about `stage.sh` worth knowing before running it:

- Its `[2/6]` and `[4/6]` blocks read the jujutower pair **without `sudo`**
  (like hi2vi's, unlike changple5's under `/etc/`), so `/home/opc/jujutower_tls/`
  must be readable by `opc`. Put it there, not under `/etc/`.
- Its `[6/6]` "no live change" assertions check **`changple5-nginx-1`'s**
  `StartedAt` and the 80/443 port owner — **not** `edge-nginx`'s. It *reports*
  `edge-nginx`'s state but does not assert it. So record `edge-nginx`'s
  `StartedAt` yourself before you start (the runbook's R2 does) and check it
  again at the end.

## Step 3 — the standing loop

Run from the edge checkout, in this order. Nothing else applies a change.

```sh
cd ~/projects/personal/edge/edge
./validate.sh          # LOCAL gate: dummy certs + compose config + nginx -t over the WHOLE tree
bash stage.sh          # operator-run: rsync (no --delete) + stage the REAL certs on the VM + on-VM validate
ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'   # nginx -t hard gate, then nginx -s reload
```

**`deploy.sh` never runs `up`, `restart` or `--force-recreate`.** Recreating
`edge-nginx` drops its shared-network attachment and cascades into every
co-tenant site on the box. A failed `nginx -t` reloads nothing at all, so the
edge keeps serving its last known-good config — which is why `validate.sh` over
the *whole* tree is the gate that matters: a duplicate global name in one file
fails `nginx -t` for every site.

## Step 4 — verify (before Cloudflare, then after)

**Against the origin directly**, bypassing Cloudflare — this is what proves the
vhost works before any DNS record goes proxied:

```sh
curl -sI --resolve jujutower.com:80:140.245.64.173  http://jujutower.com/          # → 301 to https
curl -skI --resolve jujutower.com:443:140.245.64.173 https://jujutower.com/api/health   # → 200 + JSON
```

**The no-harm assertions** — run all three; any failure is a stop-and-fix:

```sh
curl -sI https://hi2vi.com/ https://vocky.hi2vi.com/ https://changple.ai/ | grep -E '^HTTP'   # all 200
ssh oracle-cloud "docker inspect -f '{{.State.StartedAt}}' edge-nginx"    # UNCHANGED from the R2 baseline
ssh oracle-cloud 'docker ps --format "{{.Names}} {{.Ports}}" | grep -E "0.0.0.0:(80|443)->"'  # still edge-nginx
```

Then, and only then, the Cloudflare cut-over — `deploy/runbook.md` **R5**, whose
order (Full (Strict) **before** the record goes proxied) is what avoids the 526
and the redirect loop.

## The `www.jujutower.com` alias

**ENABLED** — operator decision, 2026-09-02 (`P4.S4`, dispatch 3). `www` exists
only to **301 to the canonical apex**; the apex serves the product and stays the
one indexable address (`P4.S5`'s `metadataBase`, canonicals and sitemap are
apex-only and depend on that).

What it took, and what it did *not*:

- **No new certificate.** The Origin CA pair was minted with
  `subjectAltName = DNS:*.jujutower.com, DNS:jujutower.com`, so the wildcard
  already covered www. Both server blocks load the same
  `/etc/nginx/certs/jujutower.{crt,key}` — **one** `CERT_NAMES` basename, so
  neither `validate.sh` nor `stage.sh` needed a further edit for the alias.
- **In `jujutower.conf`:** `www.jujutower.com` added to the `:80`
  `server_name`, and the previously-commented www `:443` server block
  uncommented (it is a bare `return 301 https://jujutower.com$request_uri;`).
- **Applied the normal way** — `./validate.sh` → `bash stage.sh` → on-VM
  `bash deploy.sh` (`nginx -t` → `nginx -s reload`). `edge-nginx` was not
  recreated; its `StartedAt` stayed `2026-07-02T19:22:12.325478595Z`.

Proof at the origin (grey, bypassing Cloudflare):

```bash
curl -skI --resolve www.jujutower.com:443:140.245.64.173 'https://www.jujutower.com/x?y=1'
#   -> HTTP/2 301, location: https://jujutower.com/x?y=1     (path + query preserved)
curl -sI  --resolve www.jujutower.com:80:140.245.64.173  'http://www.jujutower.com/x?y=1'
#   -> 301 -> https://www.jujutower.com/x?y=1  (the :80 block keeps $host)
#      then the line above -> the apex. Two hops, both permanent.
```

**The DNS half is separate and is not in this repo.** `www` needs a **proxied**
Cloudflare record pointing at the box (`A 140.245.64.173`, or a proxied
`CNAME jujutower.com`). While the record still points anywhere else, the vhost
above is correct and simply unreachable and Cloudflare answers from the old
origin — at the time of writing, a **525** (origin TLS handshake failed) from
the record Cloudflare imported from Namecheap.
