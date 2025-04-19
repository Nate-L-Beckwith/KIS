# ──────────────── settings ─────────────────
COMPOSE      = docker compose -f docker-compose.yml
PROJECT_NAME = mini-ca
IMAGE_NAME   = minica
VOLUME_NAME  = minica-data

# ──────────────── targets ──────────────────
.PHONY: build up setup clean nuke

## Build (or rebuild) every service image
build:
	$(COMPOSE) build

## Start the long‑running watcher in the background
up: build
	$(COMPOSE) up -d

## One‑shot setup: build everything & run the init container only
setup:
	docker compose --profile setup up --build -d

## Stop containers, remove network + volume, but keep the images
clean:
	$(COMPOSE) down --volumes --remove-orphans
	-@docker volume rm -f $(VOLUME_NAME) 2>/dev/null || true

## *** DANGER *** – wipe absolutely everything related to this project
##   • containers / networks / named volume
##   • the minica image (all tags)
##   • dangling layers & build cache for the image
nuke:
	@echo "🔴 NUKE: removing *all* $(IMAGE_NAME) containers, images, volume and cache …"

	# 1. Stop/remove the compose stack (if it exists)
	-$(COMPOSE) down --volumes --remove-orphans

	# 2. Force‑remove stray containers that still use the image
	-@docker rm -f $$(docker ps -a -q --filter "ancestor=$(IMAGE_NAME)") 2>/dev/null || true

	# 3. Remove the named volume (if it’s still hanging around)
	-@docker volume rm -f $(VOLUME_NAME) 2>/dev/null || true

	# 4. Remove *all* local tags of the image
	-@docker rmi -f $$(docker images -q $(IMAGE_NAME)) 2>/dev/null || true

	# 5. Clear the build cache (optional but tidy)
	-@docker builder prune -f 2>/dev/null || true

	@echo "✅  $(PROJECT_NAME) completely nuked"
# default target (shown by plain `make`)
default: build
