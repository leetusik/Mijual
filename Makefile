# Mijual dev stack.
#
#   make stack-up      start Postgres (docker), the API and the frontend
#   make stack-down    stop the API and the frontend (Postgres stays up)
#   make stack-status  what is running, and the URLs to open
#
# The frontend binds 0.0.0.0, so the app is reachable both at
# http://127.0.0.1:3000 and over Tailscale at http://<tailscale-ip>:3000.
# Login works on both: MIJUAL_COOKIE_SECURE defaults off in dev, and the
# session cookie is host-scoped while /api/* is same-origin via the Next
# rewrite. The API itself stays on 127.0.0.1 — remote traffic reaches it
# only through the frontend proxy.
#
# The API runs with a root logging config on purpose: without one, the
# per-turn agent-spend ▷ ledger line is recorded nowhere (operations doc,
# "invisible under a default uvicorn").

SHELL := /bin/bash
VENV  := .venv/bin
STACK := var/stack

API_HOST := 127.0.0.1
API_PORT := 8000
WEB_PORT := 3000

API_PID := $(STACK)/api.pid
WEB_PID := $(STACK)/web.pid
API_LOG := $(STACK)/api.log
WEB_LOG := $(STACK)/web.log

.PHONY: stack-up stack-down stack-status db-up db-ensure api-up web-up

stack-up: db-up db-ensure api-up web-up stack-status

db-up:
	docker compose up -d postgres

# Additive and idempotent: create_all only creates missing tables (the
# serving process deliberately creates none at startup), ensure_columns
# closes the additive-column gap. Safe to run on every stack-up.
db-ensure:
	@$(VENV)/python -c "\
	from mijual.config import load_settings; \
	from mijual.db import make_engine, create_all; \
	from mijual.db.schema_sync import ensure_columns; \
	from mijual.db.models import Base; \
	e = make_engine(load_settings().database_url); \
	create_all(e); \
	added = ensure_columns(e, Base); \
	print('schema ok' + (f' (+{len(added)} columns)' if added else ''))"

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
		nohup npm --prefix frontend run dev -- -H 0.0.0.0 -p $(WEB_PORT) \
			> $(WEB_LOG) 2>&1 < /dev/null & echo $$! > $(WEB_PID); \
		echo "web starting (pid $$(cat $(WEB_PID)), log $(WEB_LOG))"; \
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
	@ts=$$(command -v tailscale || echo /Applications/Tailscale.app/Contents/MacOS/Tailscale); \
	ts_ip=$$($$ts ip -4 2>/dev/null | head -1); \
	if [ -n "$$ts_ip" ]; then echo "tailscale:  http://$$ts_ip:$(WEB_PORT)"; \
	else echo "tailscale:  (not up)"; fi
