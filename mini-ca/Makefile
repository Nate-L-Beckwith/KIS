###############################################################################
# mini‑ca – Makefile
###############################################################################
PROJECT        ?= mini-ca
IMAGE_NAME     ?= minica
VOLUME_NAME    ?= minica-data
SETUP_PROFILE  = --profile setup

COMPOSE        = docker compose -f docker-compose.yml --project-name $(PROJECT)

# (kept) – used by the one‑shot CA bootstrap
COMPOSE_RUN    = $(COMPOSE) $(SETUP_PROFILE) run --rm
COMPOSE_UPD    = $(COMPOSE) up -d

# ───────────── extra helpers for issue/sync ─────────────
CLI_RUN        = $(COMPOSE) run --rm cli
SYNC_RUN       = $(COMPOSE) --profile sync \
                 run --rm -e DOMAIN=$(DOMAIN) cert-sync

# ───────────── existing targets ─────────────
.PHONY: help build init setup up logs clean nuke default \
        issue restart-npm

help:
	@grep -E '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS=":"} {printf "\033[36m%-15s\033[0m%s\n", $$1, $$2}'

build:
	$(COMPOSE) build

## One‑shot root‑CA bootstrap (idempotent)
init: build
	$(COMPOSE_RUN) init

## Build → init (once) → start watcher
setup: init up

## Start / restart long‑running watcher
up: build
	$(COMPOSE_UPD)

logs:
	$(COMPOSE) logs -f minica

clean:
	$(COMPOSE) down --volumes --remove-orphans

nuke: clean
	@echo "🔴  NUKE: removing all artefacts for project '$(PROJECT)' …"
	-@docker rm -f \
	   $$(docker ps -a -q --filter "ancestor=$(IMAGE_NAME)") 2>/dev/null || true
	-@docker volume rm -f $(VOLUME_NAME) 2>/dev/null || true
	-@docker rmi -f $$(docker images -q $(IMAGE_NAME)) 2>/dev/null || true
	-@docker builder prune -f 2>/dev/null || true
	@echo "✅  project '$(PROJECT)' wiped clean"

default: help

# ───────────── new targets ─────────────
## make issue DOMAIN=foo.example.com
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
	@echo "👉  restarting Nginx‑Proxy‑Manager"
	$(COMPOSE) restart -t 5 npm
	@echo "✅  done – open the NPM UI ▶ SSL Certificates"
