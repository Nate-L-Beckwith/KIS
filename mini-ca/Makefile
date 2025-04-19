# mini-ca/Makefile
COMPOSE = docker compose -f docker-compose.yml

build:
	$(COMPOSE) build

setup:
	$(COMPOSE) --profile setup up --build

up:
	$(COMPOSE) up -d

cert:
	$(COMPOSE) --profile cli run --rm cli issue $(DOMAIN) $(addprefix --san ,$(SAN))

clean:
	$(COMPOSE) down --volumes --remove-orphans
	docker volume rm -f minica-data 2>/dev/null || true
