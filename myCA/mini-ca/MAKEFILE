IMAGE := minica:latest
CTX   := $(CURDIR)

build:
	docker build -f docker/Dockerfile -t $(IMAGE) .

shell: build
	docker run --rm -it -v mini-data:/data $(IMAGE) sh

init: build
	docker run --rm -v mini-data:/data $(IMAGE) init

issue: build
	@if [ -z "$$D" ]; then echo "Use:  make issue D=host.example"; exit 1; fi
	docker run --rm -v mini-data:/data $(IMAGE) issue $$D

watch: build
	docker run --rm -v mini-data:/data $(IMAGE) watch

.PHONY: build shell init issue watch
