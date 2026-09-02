# Mijual dev stack.
#
#   make stack-up      start Postgres (docker), the API and the frontend
#   make stack-down    stop the API and the frontend (Postgres stays up)
#   make stack-status  what is running, and the URLs to open
#   make smoke-prod    smoke the LIVE origin (https://jujutower.com), read-only
#
# The frontend binds 0.0.0.0, so the app is reachable both at
# http://127.0.0.1:3010 and over Tailscale at http://<tailscale-ip>:3010.
# Login works on both: MIJUAL_COOKIE_SECURE defaults off in dev, and the
# session cookie is host-scoped while /api/* is same-origin via the Next
# rewrite. The API itself stays on 127.0.0.1 — remote traffic reaches it
# only through the frontend proxy.
#
# Reachable is not the same as working: `next dev` serves /_next/* and its
# HMR socket only to hosts on `allowedDevOrigins` (see frontend/next.config.ts,
# P7.S1) and 403s the rest, which leaves the page rendered but never hydrated.
# 127.0.0.1 and **.ts.net are named in the config; the tailnet IP is not stable
# across machines, so web-up looks it up here and passes it in through
# MIJUAL_DEV_ORIGINS. Started the dev server some other way? Set that variable
# yourself, or the Tailscale origin will silently stop hydrating.
#
# The API runs with a root logging config on purpose: without one, the
# per-turn agent-spend ▷ ledger line is recorded nowhere (operations doc,
# "invisible under a default uvicorn").

SHELL := /bin/bash
VENV  := .venv/bin
STACK := var/stack

API_HOST := 127.0.0.1
API_PORT := 8010
WEB_PORT := 3010

# This machine's Tailscale IPv4, empty when the daemon is down. Used twice:
# to print the remote URL, and to let `next dev` accept that origin (P7.S1).
TS_BIN := $(shell command -v tailscale || echo /Applications/Tailscale.app/Contents/MacOS/Tailscale)
TS_IP  := $(shell $(TS_BIN) ip -4 2>/dev/null | head -1)

API_PID := $(STACK)/api.pid
WEB_PID := $(STACK)/web.pid
API_LOG := $(STACK)/api.log
WEB_LOG := $(STACK)/web.log

.PHONY: stack-up stack-down stack-status db-up db-ensure api-up web-up smoke-prod

stack-up: db-up db-ensure api-up web-up stack-status

db-up:
	docker compose up -d postgres

# Additive and idempotent: create_all only creates missing tables (the
# serving process deliberately creates none at startup), ensure_columns
# closes the additive-column gap. Safe to run on every stack-up.
#
# P4.S1 moved the body into `mijual.db.__main__` so the production compose
# one-shot (`mijual-schema` in compose.prod.yml) runs the SAME code path
# instead of a second copy of it. This target now delegates.
db-ensure:
	@$(VENV)/python -m mijual.db ensure

api-up:
	@mkdir -p $(STACK)
	@if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		echo "api already running (pid $$(cat $(API_PID)))"; \
	else \
		nohup $(VENV)/python -c "\
	import logging, uvicorn; \
	logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'); \
	uvicorn.run('mijual.web.app:app', host='$(API_HOST)', port=$(API_PORT), log_config=None)" \
			> $(API_LOG) 2>&1 < /dev/null & echo $$! > $(API_PID); \
		echo "api starting (pid $$(cat $(API_PID)), log $(API_LOG))"; \
	fi

web-up:
	@mkdir -p $(STACK)
	@if [ -f $(WEB_PID) ] && kill -0 $$(cat $(WEB_PID)) 2>/dev/null; then \
		echo "web already running (pid $$(cat $(WEB_PID)))"; \
	else \
		MIJUAL_DEV_ORIGINS="$(TS_IP)" \
		nohup npm --prefix frontend run dev -- -H 0.0.0.0 -p $(WEB_PORT) \
			> $(WEB_LOG) 2>&1 < /dev/null & echo $$! > $(WEB_PID); \
		echo "web starting (pid $$(cat $(WEB_PID)), log $(WEB_LOG))"; \
		if [ -n "$(TS_IP)" ]; then \
			echo "  dev origins: 127.0.0.1, [::1], **.ts.net, $(TS_IP)"; \
		else \
			echo "  dev origins: 127.0.0.1, [::1], **.ts.net (tailscale down — its IP is not allowed)"; \
		fi; \
	fi

stack-down:
	@for pidfile in $(WEB_PID) $(API_PID); do \
		if [ -f $$pidfile ]; then \
			pid=$$(cat $$pidfile); \
			if kill -0 $$pid 2>/dev/null; then \
				pkill -TERM -P $$pid 2>/dev/null; kill -TERM $$pid 2>/dev/null; \
				echo "stopped pid $$pid ($$pidfile)"; \
			fi; \
			rm -f $$pidfile; \
		fi; \
	done
	@-lsof -ti :$(WEB_PORT) 2>/dev/null | xargs kill -TERM 2>/dev/null || true
	@-lsof -ti :$(API_PORT) -sTCP:LISTEN 2>/dev/null | xargs kill -TERM 2>/dev/null || true
	@echo "postgres left running — 'docker compose stop postgres' if you want it down too"

stack-status:
	@echo "── mijual dev stack ─────────────────────────────"
	@docker compose ps postgres --format '{{.Name}}: {{.Status}}' 2>/dev/null || echo "postgres: docker not reachable"
	@if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		echo "api: running (pid $$(cat $(API_PID))) — http://$(API_HOST):$(API_PORT)"; \
	else echo "api: stopped"; fi
	@if [ -f $(WEB_PID) ] && kill -0 $$(cat $(WEB_PID)) 2>/dev/null; then \
		echo "web: running (pid $$(cat $(WEB_PID)))"; \
	else echo "web: stopped"; fi
	@echo "open:  http://127.0.0.1:$(WEB_PORT)"
	@if [ -n "$(TS_IP)" ]; then echo "tailscale:  http://$(TS_IP):$(WEB_PORT)"; \
	else echo "tailscale:  (not up)"; fi

# The production smoke suite: every check goes through Cloudflare -> the shared
# edge nginx -> the mijual-web container -> (for /api/*) Next's rewrite ->
# FastAPI, against the LIVE origin. Read-only and free — no POST /api/ask, no
# account, no writes — so it is safe to run at any time, including right after a
# deploy (runbook R6) and before one. Stdlib only, so it needs no venv.
#
#   make smoke-prod                       # the whole suite
#   make smoke-prod ARGS="--light"        # only the two probe checks
#   make smoke-prod ARGS="--no-cotenants" # skip the neighbouring sites
#   make smoke-prod ARGS="--base https://jujutower.com"
#
# Non-zero exit on any failed check; the same script the uptime probe runs.
smoke-prod:
	@python3 scripts/smoke_production.py $(ARGS)
