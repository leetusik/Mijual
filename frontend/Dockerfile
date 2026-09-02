# syntax=docker/dockerfile:1
# 주주의관제탑 — the Next.js image (P4.S1). Context: `frontend/`.
#
# This is the ONLY container the edge nginx ever sees. Every browser request —
# pages and `/api/*` alike — arrives here, and Next's rewrite forwards `/api/*` to
# FastAPI over the project-internal network. That is a landed security decision,
# not a convenience: the API grants no CORS and no preflight, and the CSRF design
# depends on `/api/*` being same-origin (see next.config.ts).
#
# ---------- build ----------
FROM node:22-slim AS build

# Do NOT set NODE_ENV=production in this stage: `npm ci` would skip
# devDependencies (typescript, @types/*) and `next build` would fail.
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# MIJUAL_API_ORIGIN is needed TWICE and this is the first of the two: the Next
# rewrite's destination is resolved at BUILD time (next.config.ts reads
# process.env at config load). The second is a runtime env var on the container,
# because `frontend/lib/api.ts` reads the same variable for server-component
# fetches. compose.prod.yml therefore sets it in `build.args` AND `environment`.
#
# Asserted non-empty on purpose: next.config.ts defaults it to
# `http://localhost:8010`, so a build that forgot the arg would SUCCEED and ship a
# container whose every /api/* call goes to its own empty loopback. Fail here
# instead — the same trap hi2vi hit with NEXT_PUBLIC_APP_URL.
ARG MIJUAL_API_ORIGIN
RUN test -n "$MIJUAL_API_ORIGIN" || { echo "ERROR: MIJUAL_API_ORIGIN build arg required (see compose.prod.yml build.args)" >&2; exit 1; }
ENV MIJUAL_API_ORIGIN=$MIJUAL_API_ORIGIN

# NEXT_PUBLIC_SITE_URL is the product's own public origin — https://jujutower.com,
# apex-only (www 301s to it). It is BUILD-ONLY, unlike MIJUAL_API_ORIGIN above:
# Next inlines NEXT_PUBLIC_* at build time, so the value is baked into the image
# and changing it needs a rebuild, not a restart. That is why it appears in
# compose.prod.yml's build.args and NOT in .env.prod / .env.prod.example — the web
# container has no env_file at all.
#
# Asserted non-empty for the same reason MIJUAL_API_ORIGIN is, and the failure it
# prevents is worse: `metadataBase`, every canonical, every sitemap URL and the OG
# image URL resolve from it, so a build that forgot the arg would ship a site
# telling search engines its pages live somewhere else. lib/seo.ts throws at module
# load in a production build too — this line is the earlier, clearer of the two.
ARG NEXT_PUBLIC_SITE_URL
RUN test -n "$NEXT_PUBLIC_SITE_URL" || { echo "ERROR: NEXT_PUBLIC_SITE_URL build arg required (see compose.prod.yml build.args)" >&2; exit 1; }
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL

# Search-engine ownership verification, both OPTIONAL and both build args for the
# same inlining reason. Unset (or empty) renders NO <meta> at all — never a blank
# content="" — so they are deliberately NOT asserted. Google's property is a
# DNS-TXT domain property held at Cloudflare and needs nothing here; Naver Search
# Advisor would need a token, and whether to register is an operator decision.
ARG NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION=""
ARG NEXT_PUBLIC_NAVER_SITE_VERIFICATION=""
ENV NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION=$NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION \
    NEXT_PUBLIC_NAVER_SITE_VERIFICATION=$NEXT_PUBLIC_NAVER_SITE_VERIFICATION

# Nothing in the app is prerendered (`await connection()` on every reader route),
# so this build needs no running API and makes no request.
RUN npm run build

# ---------- runtime ----------
FROM node:22-slim AS runtime

# Port 3010, not Next's default 3000, so every origin the docs name keeps the same
# number in dev and in production.
ENV NODE_ENV=production \
    PORT=3010 \
    HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1 \
    TZ=Asia/Seoul

WORKDIR /app

# `output: "standalone"` traces exactly the node_modules the server needs into
# .next/standalone; static assets and public/ are copied beside it by contract.
# No `sharp` staging here (unlike hi2vi): this app uses no `next/image` anywhere —
# the wordmark is a plain <img> — so the image optimizer is never reached.
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public

USER node

# Documentation only — compose uses `expose:`, never a published host port.
EXPOSE 3010

# Deliberately probes `/api/health` and NOT `/`: this is the deploy's rollback
# trigger (P4.S3), and a web container that cannot reach its API through the
# rewrite is not a release even though its own pages render. The trade-off is
# accepted knowingly — an API outage will also mark the web container unhealthy,
# which is the honest reading for a product whose every page is server-rendered
# from that API.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3010/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]

CMD ["node", "server.js"]
