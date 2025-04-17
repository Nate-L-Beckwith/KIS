#!/usr/bin/env python3
"""Minimal self‑contained certificate authority CLI.

Usage examples (run inside the container):
  ca init                               initialise root CA if absent
  ca issue example.com --san www.example.com api.example.com
  ca list                               list issued certs & SANs
"""
from __future__ import annotations
import argparse, datetime as dt, os, pathlib, sys, textwrap
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CA_HOME = pathlib.Path(os.getenv("CA_HOME", "/data"))
ROOT_DIR = CA_HOME / "rootCA"
CERTS_DIR = CA_HOME / "certificates"
KEY_BITS = int(os.getenv("CA_BITS", 4096))
ROOT_DAYS = int(os.getenv("CA_ROOT_DAYS", 3650))
LEAF_DAYS = int(os.getenv("CA_LEAF_DAYS", 825))
SIGALG = hashes.SHA256()

# ---------- helpers ----------

def _ensure(p: pathlib.Path):
    p.mkdir(parents=True, exist_ok=True)

def _write(path: pathlib.Path, data: bytes, mode: int = 0o600):
    _ensure(path.parent)
    path.write_bytes(data)
    os.chmod(path, mode)

# ---------- core ops ----------

def init_root(force: bool = False):
    key_path = ROOT_DIR / "rootCA.key"
    crt_path = ROOT_DIR / "rootCA.crt"
    if key_path.exists() and not force:
        print("✔︎ Root CA already exists →", ROOT_DIR)
        return
    print("🆕 Creating new root CA …")
    key = rsa.generate_private_key(65537, KEY_BITS)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "mini‑ca Root")])
    now = dt.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject).issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(days=ROOT_DAYS))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, SIGALG)
    )
    _write(key_path, key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    _write(crt_path, cert.public_bytes(serialization.Encoding.PEM), 0o644)
    print(f"   ‣ key : {key_path}\n   ‣ cert: {crt_path}")


def _load_root():
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.x509 import load_pem_x509_certificate
    key = load_pem_private_key((ROOT_DIR / "rootCA.key").read_bytes(), None)
    cert = load_pem_x509_certificate((ROOT_DIR / "rootCA.crt").read_bytes())
    return key, cert


def issue(cn: str, sans: list[str]):
    if not (ROOT_DIR / "rootCA.key").exists():
        sys.exit("❌  Root CA missing – run 'ca init' first")

    key, ca_cert = _load_root()
    leaf_key = rsa.generate_private_key(65537, KEY_BITS)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = dt.datetime.utcnow()
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=1))
        .not_valid_after(now + dt.timedelta(days=LEAF_DAYS))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(name) for name in sans]),
            critical=False,
        )
    )
    cert = cert_builder.sign(key, SIGALG)

    out_dir = CERTS_DIR / cn.split(".")[0]
    _write(out_dir / f"{cn.split('.')[0]}.key", leaf_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    _write(out_dir / f"{cn.split('.')[0]}.crt", cert.public_bytes(serialization.Encoding.PEM), 0o644)
    print(f"✅  Certificate issued for '{cn}' → {out_dir}")


def list_certs():
    if not CERTS_DIR.exists():
        print("(no leaf certificates yet)")
        return
    for d in sorted(CERTS_DIR.iterdir()):
        crt = next(d.glob("*.crt"), None)
        if not crt:
            continue
        cert = x509.load_pem_x509_certificate(crt.read_bytes())
        sans = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        print(f"• {d.name}: {', '.join(sans) } (expires {cert.not_valid_after.date()})")

# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(prog="ca", formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
            mini‑ca — root CA + leaf issuer in one binary.
            Mount a volume at /data to persist keys & certs.
        """))
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="create root CA if absent")
    sp.add_argument("--force", action="store_true", help="overwrite existing root")

    sp = sub.add_parser("issue", help="issue a certificate")
    sp.add_argument("cn", help="common‑name / primary DNS name")
    sp.add_argument("--san", nargs="+", required=False, default=[], help="extra SubjectAltNames")

    sub.add_parser("list", help="list issued certificates")

    a = p.parse_args()
    if a.cmd == "init":
        init_root(a.force)
    elif a.cmd == "issue":
        issue(a.cn, [a.cn] + a.san)
    else:
        list_certs()

if __name__ == "__main__":
    main()