# ---------- builder: install wheels ----------
    FROM python:3.12-slim AS build
    WORKDIR /build
    RUN apt-get update -qq && apt-get install -y --no-install-recommends ca-certificates \
        && apt-get clean && rm -rf /var/lib/apt/lists/*
    COPY ca.py ./
    RUN pip install --upgrade pip && \
        pip wheel --no-cache-dir cryptography -w /wheels
    
    # ---------- runtime: tiny final image ----------
    FROM python:3.12-slim
    ENV PYTHONUNBUFFERED=1 \
        CA_HOME=/data
    WORKDIR /opt/ca
    
    # non‑root runtime UID/GID 1001
    RUN useradd -u 1001 -m ca
    
    COPY --from=build /wheels /wheels
    COPY ca.py ./
    RUN pip install --no-cache-dir /wheels/* && chmod 755 ca.py && \
        ln -s /opt/ca/ca.py /usr/local/bin/ca
    
    # entrypoint: pass args straight to CLI
    USER ca
    ENTRYPOINT ["ca"]