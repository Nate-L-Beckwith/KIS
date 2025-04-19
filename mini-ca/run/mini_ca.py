#!/usr/bin/env python
from pathlib import Path
import typer

from init_ca import init_ca
from issue_cert import issue_cert
from watch import watch_file

APP = typer.Typer(add_completion=False)
CA_DIR     = Path("/data/rootCA")
CERTS_DIR  = Path("/data/certificates")


@APP.command()
def init(force: bool = typer.Option(
         False, help="Overwrite existing CA if it exists")):
    """Initialise or recreate the root CA."""
    init_ca(CA_DIR, force)


@APP.command()
def issue(domain: str,
          san: list[str] = typer.Option(None, "--san", help="extra SANs")):
    """Issue a certificate for *DOMAIN*."""
    issue_cert(domain, san or [], CA_DIR, CERTS_DIR)


@APP.command()
def watch(file: Path = typer.Option("/data/DOMAINS", "--file",
                                    help="domain list file to watch")):
    """Watch *file* and issue certs for new domains."""
    watch_file(file, CA_DIR, CERTS_DIR)


if __name__ == "__main__":
    APP()
