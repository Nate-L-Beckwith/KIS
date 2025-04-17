from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime, typer

def init_ca(ca_dir: Path, force: bool = False) -> None:
    key_file  = ca_dir / "rootCA.key"
    cert_file = ca_dir / "rootCA.crt"

    if key_file.exists() and not force:
        typer.echo("✅  root CA already present")
        return

    ca_dir.mkdir(parents=True, exist_ok=True)

    key = rsa.generate_private_key(65537, 4096)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "mini-ca"),
        x509.NameAttribute(NameOID.COMMON_NAME,       "mini-ca root"),
    ])
    cert = (x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() +
                             datetime.timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None),
                           critical=True)
            .sign(key, hashes.SHA256()))

    for path, blob, priv in (
            (key_file,  key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()), True),
            (cert_file, cert.public_bytes(serialization.Encoding.PEM), False)):
        path.write_bytes(blob)
        if priv:
            path.chmod(0o600)

    typer.echo(f"🎉  new root CA written to {ca_dir}")
    typer.echo(f"🔑  private key: {key_file}")
    typer.echo(f"📜  certificate: {cert_file}")

