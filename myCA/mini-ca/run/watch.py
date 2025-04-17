import hashlib, time, subprocess, shlex
from pathlib import Path

def _finger(s: str) -> str: return hashlib.sha1(s.encode()).hexdigest()

def _clean(p: Path):
    return [l.strip() for l in p.read_text().splitlines()
            if l.strip() and not l.lstrip().startswith("#")]

def loop(dom_file: Path, certs_dir: Path, root_dir: Path, days: int, sleep=12*3600):
    last = ""
    while True:
        if dom_file.exists():
            data = "\n".join(_clean(dom_file))
            h = _finger(data)
            if h != last:
                for host in data.splitlines():
                    cmd = f'python -m mini_ca issue {shlex.quote(host)}'
                    subprocess.run(shlex.split(cmd), check=True)
                last = h
        time.sleep(sleep)
