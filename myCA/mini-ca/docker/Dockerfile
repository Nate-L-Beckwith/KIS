# ─────────────────────────────────────────────
# 1) builder – grab cryptography wheel once
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY run/ ./run
COPY docker/entry.sh .

RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir cryptography -w /wheels

# ─────────────────────────────────────────────
# 2) runtime  –   single image, multi‑command
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    MYCA_ROOT=/data/rootCA \
    MYCA_CERTS=/data/certificates

# default UID/GID used by container
ARG UID=1001
RUN useradd -u ${UID} -m myca

WORKDIR /opt/myca
COPY --from=builder /wheels /wheels
COPY --from=builder /src/run/*.py ./
COPY --from=builder /src/entry.sh /usr/local/bin/

RUN pip install --no-cache-dir /wheels/* \
 && chmod +x /usr/local/bin/entry.sh \
 && chown -R myca:myca /opt/myca

USER myca
ENTRYPOINT ["entry.sh"]    # see docker/entry.sh
