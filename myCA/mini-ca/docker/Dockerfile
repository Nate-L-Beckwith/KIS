# ──────────────────────────────────────────────────────────────
# 1) builder  – create wheels once (zero net access later)
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update                                                        \
 && apt-get install -y --no-install-recommends ca-certificates            \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY run/ ./run
COPY docker/entry.sh .
COPY requirements.txt .

# build wheels (cryptography + our Python deps)
RUN pip install --upgrade pip                                             \
 && pip wheel --no-cache-dir cryptography           -w /wheels            \
 && pip wheel --no-cache-dir -r requirements.txt   -w /wheels

# ──────────────────────────────────────────────────────────────
# 2) runtime  – single image / multi‑command
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1            \
    MYCA_ROOT=/data/rootCA        \
    MYCA_CERTS=/data/certificates

ARG UID=1001
RUN useradd -u ${UID} -m myca

WORKDIR /opt/myca
COPY --from=builder /wheels /wheels
COPY --from=builder /src/run/*.py ./
COPY --from=builder /src/entry.sh /usr/local/bin/entry.sh

RUN pip install --no-cache-dir /wheels/*      \
 && chmod +x /usr/local/bin/entry.sh          \
 && chown -R myca:myca /opt/myca

RUN ln -s /opt/myca/mini_ca.py /usr/local/bin/mini_ca.py
RUN chmod +x /opt/myca/mini_ca.py
USER myca
ENTRYPOINT ["entry.sh"]
