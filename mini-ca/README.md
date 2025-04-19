# 🔐 mini‑ca
*A zero‑dependency Certificate Authority in a single Docker image*
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

</div>

---

## Contents <!-- omit in toc -->

1. [Highlights](#highlights)
2. [Quick start](#quick-start)
3. [Repository layout](#repository-layout)
4. [Docker stack](#docker-stack)
5. [Command‑line interface](#command‑line-interface)
6. [Live domain‑watch](#live-domain‑watch)
7. [Make targets](#make-targets)
8. [Clean ↔ Rebuild matrix](#clean↔rebuild-matrix)
9. [💣 `make nuke` – full reset](#make nuke--full-reset)
10. [Configuration](#configuration)
11. [Best practices & CI notes](#best-practices--ci-notes)
12. [Troubleshooting](#troubleshooting)

---

## Highlights

| ✔︎ | Feature |
|----|---------|
| **One‑shot root CA** – `entry-init.sh` generates *rootCA.key + rootCA.crt* (10 yrs). |
| **Offline image** – wheels baked at build‑time, **no outbound net** in production. |
| **Idempotent bootstrap** – safe re‑runs; add `--force` to rotate keys. |
| **Leaf certs on demand** – `issue <domain> [--san alt …]` drops key / cert / chain in its own dir. |
| **Wildcard + unlimited SANs** – `*.example.dev` & friends. |
| **Continuous watcher** – tails `/data/DOMAINS` → auto‑issues as lines appear. |
| **Named volume** – everything under **`minica-data`** survives container churn. |
| **Profiles** – *init* (bootstrap) · *minica* (watch) · *cli* (ad‑hoc). |
| **Friendly Makefile** – `help • build • init • setup • up • logs • clean • nuke`. |
| **Colourised logs** – success lines start with `✅`. |
| **Complete wipe** – `make nuke` kills containers, volume, images **and** BuildKit cache. |

---

## Quick start

```bash
git clone https://github.com/your-org/mini-ca.git
cd mini-ca

# 1️⃣  build image + bootstrap root CA (+ volume)
make init                # => docker compose --profile setup run …

# 2️⃣  bring up the live watcher in the background
make up                  # => docker compose up -d

# 3️⃣  mint a certificate whenever you need one
docker compose run --rm cli issue blog.acme.test --san www.blog.acme.test
```
--san flag is optional
If omitted, the tool automatically sets SAN =DOMAIN.
Use --san (or --san=…) only when you need additional names.

Result inside the volume:

```tree
/data/
├─ rootCA/
│  ├─ rootCA.key
│  └─ rootCA.crt
└─ certificates/
   └─ blog.acme.test/
      ├─ blog.acme.test.key
      ├─ blog.acme.test.crt
      └─ chain.pem              # root + leaf
```

> **Trust chain:** import *rootCA.crt* into your OS / browser once – every leaf cert is then trusted.

---

##  Repository layout

```text
mini-ca/
├─ docker/
│  ├─ Dockerfile         # multi‑stage, wheels baked
│  ├─ entry.sh           # default entrypoint (watch / cli)
│  └─ entry-init.sh      # one‑shot CA bootstrap
├─ run/                  # pure‑Python CA logic (Typer CLI)
│  ├─ mini_ca.py         # main CLI
│  ├─ init_ca.py
│  ├─ issue_cert.py
│  ├─ watch.py
│  └─ ...
├─ docker-compose.yml    # production bundle (profiles)
├─ Makefile              # convenience wrapper
├─ requirements.txt      # runtime deps (wheel‑cached)
└─ README.md             # <— this file
```

---

##  Docker stack

| Service   | Profile(s) | Role                      | Entrypoint       | Restart |
|-----------|------------|---------------------------|------------------|---------|
| **init**  | `setup`    | one‑shot root CA bootstrap| `entry-init.sh`  | *no*    |
| **cli**   | `cli`      | ad‑hoc CA commands        | `entry.sh`       | *no*    |
| **minica**| *(default)*| live domain watcher       | `entry.sh`       | `unless-stopped` |

All services mount **`minica-data`** → `/data`.

---

##  Command‑line interface

```bash
mini_ca.py init   [--force]
mini_ca.py issue  DOMAIN [--san ALT …]
mini_ca.py watch  [--file /data/DOMAINS]
```

* **init** – create / rotate the root CA.
* **issue** – write key + cert + chain for *DOMAIN*.
* **watch** – monitor a file and issue for every new line.

One‑shot example (no compose):

```bash
docker run --rm -v minica-data:/data minica \
       mini_ca.py issue "*.wild.dev" --san api.wild.dev
```

---

##  Live domain‑watch

1. `make up` – starts **minica** which tails `/data/DOMAINS`.
2. Append hostnames – every line triggers `issue`.

```bash
echo "store.acme.dev" | docker compose exec -T cli \
        sh -c 'cat >>/data/DOMAINS'
```

Watcher logs show:

```text
✅  Certificate issued for 'store.acme.dev'
```

---

##  Make targets

| Target  | Description |
|---------|-------------|
| **help**  | Colourised target list (default). |
| **build** | `docker compose build` (all services). |
| **init**  | Build then run the *init* profile once (creates volume & root CA). |
| **setup** | Convenience: **init + up** – great for a fresh clone. |
| **up**    | Start (or restart) the watcher. |
| **logs**  | Follow watcher logs (`docker compose logs -f minica`). |
| **clean** | Stop stack **and** delete volume `minica-data` (images kept). |
| **nuke**  | Full wipe – containers, volume, **all** `minica:*` images, BuildKit cache. |

Environment overrides:

```bash
PROJECT=my‑lab make up     # custom compose project‑name
UID=$(id -u) make build    # bake image with matching uid
WATCH=0 make up            # skip starting the watcher
```

---

##  Clean↔Rebuild matrix

| Need | Command |
|------|---------|
| Stop stack, keep data            | `make clean` *(edit Makefile to drop volume rm if desired)* |
| Delete data & start fresh        | `make clean && make init && make up` or simply `make setup` |
| Rotate root CA (new trust chain) | `docker compose run --rm cli init --force` *(after `make clean`)* |
| Hard‑reset **everything**        | `make nuke` |

---

##  make nuke – full reset

```bash
make nuke
# 🔴  NUKE: removing all artefacts for project 'mini-ca' …
# …
# ✅  project 'mini-ca' wiped clean
```

Performed steps

1. `docker compose down --volumes`.
2. `docker rm -f` any stray container using the `minica` image.
3. `docker volume rm -f minica-data`.
4. `docker rmi -f $(docker images -q minica)`.
5. `docker builder prune -f`.

You’re back to zero – run `make setup` to start again.

---

##  Configuration

| Variable (env / build‑arg) | Default | Usage |
|----------------------------|---------|-------|
| `MYCA_ROOT`                | `/data/rootCA`        | root CA folder |
| `MYCA_CERTS`               | `/data/certificates`  | leaf cert store |
| `UID` (build‑arg)          | `1001`                | runtime user id |

Override via `docker compose build --build-arg UID=$(id -u)` or editing `docker-compose.yml`.

---

##  Best practices & CI notes

| Tip | Why |
|-----|-----|
| **Back up** `/data/rootCA/rootCA.key` & `rootCA.crt` before rolling to prod. | Losing the key breaks the trust chain forever. |
| Use *two* compose projects in CI: one for **init** (outputs artefacts) and one for tests. | Isolates state. |
| Mount `minica-data` **read‑only** in consumer services. | Prevents accidental writes. |
| Prefer `mini_ca.py issue … --days 1` *(if you add TTL flag)* for short‑lived CI certs. | Avoids long‑term clutter. |

---

##  Troubleshooting

| Symptom | Likely cause / fix |
|---------|-------------------|
| `Permission denied: '/data/DOMAINS'` | Volume created as root – run `make clean`, then `make init` to re‑chown. |
| `FileNotFoundError rootCA.key` | Skipped bootstrap – run `make init` (or `make setup`). |
| Terminal “hangs” after `run cli watch` | That command is interactive; add `-d` or use the `minica` watcher service + `make logs`. |
| Docker disk space bloat | `make nuke` removes images, volume, & cache layers. |

---

###  License

Released under the [MIT License](LICENSE).
