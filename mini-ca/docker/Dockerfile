#################################################################
# 1) Builder stage – fetch wheels once (no compilation later)   #
#################################################################
FROM python:3.12-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY run/                 ./run
COPY docker/entry.sh      .
COPY docker/entry-init.sh .
COPY requirements.txt     .

# Build wheels for cryptography + other deps
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir cryptography -w /wheels \
 && pip wheel --no-cache-dir -r requirements.txt -w /wheels

#################################################################
# 2) Runtime stage – single image, multiple entrypoints         #
#################################################################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    MYCA_ROOT=/data/rootCA \
    MYCA_CERTS=/data/certificates

ARG UID=1001
RUN useradd -u ${UID} -m myca

WORKDIR /opt/myca
COPY --from=builder /wheels /wheels
COPY --from=builder /src/run/*.py ./
COPY --from=builder /src/entry.sh /usr/local/bin/entry.sh
COPY --from=builder /src/entry-init.sh /usr/local/bin/entry-init.sh

RUN pip install --no-cache-dir /wheels/* \
 && chmod +x /usr/local/bin/entry.sh /usr/local/bin/entry-init.sh \
 && ln -s /opt/myca/mini_ca.py /usr/local/bin/mini_ca.py \
 && chmod +x /opt/myca/mini_ca.py \
 && chown -R myca:myca /opt/myca

USER myca
ENTRYPOINT ["entry.sh"]
