#!/usr/bin/env python3

"""
mini-casinglebinary development certificate authority

Three sub-commands:

    init      create / verify the root CA
    issue     issue a single certificate
    watch     watch a domains file & issue certs automatically
"""
from pathlib import Path
import os, time, hashlib, typer
from init_ca import init_ca
from issue_cert import issue_cert

app = typer.Typer()
CA_DIR      = Path(os.getenv("MYCA_ROOT",  "/data/rootCA"))
CERTS_DIR   = Path(os.getenv("MYCA_CERTS", "/data/certificates"))

@app.command()
def init(force: bool = typer.Option(False, help="overwrite existing CA")):
    init_ca(CA_DIR, force)

@app.command()
def issue(domain: str,
          san: list[str] = typer.Option(None, "--san", help="extra SANs")):
    issue_cert(domain, san or [], CA_DIR, CERTS_DIR)

@app.command()
def watch(file: Path = typer.Option("/data/DOMAINS", "--file",
                                    help="domain list to track"),
          interval: float = 1.0):
    typer.echo(f"📜  watching {file} …")
    last = ""
    while True:
        if file.exists():
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            if digest != last:
                last = digest
                for line in file.read_text().splitlines():
                    if line.strip():
                        issue_cert(line.strip(), [], CA_DIR, CERTS_DIR)
        time.sleep(interval)

if __name__ == "__main__":
    app()
