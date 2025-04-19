###############################################################################
# mini‑ca – Makefile
###############################################################################
PROJECT        ?= mini-ca
IMAGE_NAME     ?= minica
VOLUME_NAME    ?= minica-data
SETUP_PROFILE  = --profile setup

COMPOSE        = docker compose -f docker-compose.yml --project-name $(PROJECT)

COMPOSE_RUN    = $(COMPOSE) $(SETUP_PROFILE) run --rm
COMPOSE_UPD    = $(COMPOSE) up -d

.PHONY: help build init setup up logs clean nuke default

help:
	@grep -E '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS=":"} {printf "\033[36m%-10s\033[0m\n", $$1}'

build:
	$(COMPOSE) build

## One‑shot root‑CA bootstrap (idempotent)
init: build
	$(COMPOSE_RUN) init

setup: init up

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
