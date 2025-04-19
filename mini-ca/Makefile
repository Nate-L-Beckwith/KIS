PROJECT  ?= mini-ca
COMPOSE   = docker compose -f docker-compose.yml --project-name $(PROJECT)

CLI_RUN   = $(COMPOSE) run --rm --profile cli cli           # profile *before* sub‑command
SYNC_RUN  = $(COMPOSE) --profile sync run --rm -e DOMAIN=$(DOMAIN) cert-sync

.PHONY: issue restart-npm

issue:
ifndef DOMAIN
	$(error ❌  DOMAIN variable not set – use ‘make issue DOMAIN=…’)
endif
	@echo "👉  issuing $(DOMAIN)"
	$(CLI_RUN) issue $(DOMAIN)
	@echo "👉  copying into NPM"
	$(SYNC_RUN)
	@$(MAKE) restart-npm

restart-npm:
	@$(COMPOSE) restart -t 5 npm
	@echo "✅  cert imported – check NPM ▶ SSL Certificates"
