#!/usr/bin/env python3
"""
genenv.py – create / overwrite .env for mini‑ca + NPM
"""
from pathlib import Path
import secrets, socket, re, textwrap

def host_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

def token() -> str:
    return secrets.token_urlsafe(24)

def old(key: str) -> str:
    for line in old_env:
        m = re.match(rf"^{key}=(.+)$", line)
        if m:
            return m.group(1)
    return ""

root      = Path(__file__).resolve().parent
env_file  = root / ".env"
old_env   = env_file.read_text().splitlines() if env_file.exists() else []

host      = input(f"Docker host IP [{host_ip()}]: ").strip() or host_ip()
email     = input(f"Initial NPM admin email [{old('INITIAL_ADMIN_EMAIL') or 'admin@example.com'}]: ").strip() or \
            (old('INITIAL_ADMIN_EMAIL') or "admin@npm")

env_file.write_text(textwrap.dedent(f"""\
    TZ=America/New_York
    DOCKERHOST={host}

    # MariaDB
    DB_MYSQL_HOST=db
    DB_MYSQL_PORT=3306
    DB_MYSQL_USER=npm
    DB_MYSQL_NAME=npm
    MYSQL_ROOT_PASSWORD={token()}
    NPM_DB_PASSWORD={token()}

    # NPM
    NPM_CONTAINER_NAME=npm
    INITIAL_ADMIN_EMAIL={email}
    NPM_INITIAL_PASSWORD={token()}

    NPM_PORT={host}:80:80
    NPM_UI_PORT={host}:81:81
    NPM_S_PORTS={host}:443:443
    """))
print("✅  .env written")
