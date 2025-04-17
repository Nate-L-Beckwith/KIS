from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime, typer

def _load_ca(ca_dir: Path):
    key  = serialization.load_pem_private_key(
        (ca_dir / "rootCA.key").read_bytes(), password=None)
    cert = x509.load_pem_x509_certificate(
        (ca_dir / "rootCA.crt").read_bytes())
    return key, cert

def issue_cert(domain: str, san: list[str],
               ca_dir: Path, certs_dir: Path) -> None:
    ca_key, ca_cert = _load_ca(ca_dir)

    key = rsa.generate_private_key(65537, 2048)
    subj = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domain)
    ])
    alt_names = [x509.DNSName(domain)] + [x509.DNSName(s) for s in san]
    csr = (x509.CertificateSigningRequestBuilder()
           .subject_name(subj)
           .add_extension(x509.SubjectAlternativeName(alt_names), False)
           .sign(key, hashes.SHA256()))

    cert = (x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_cert.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() +
                             datetime.timedelta(days=825))
            .add_extension(x509.SubjectAlternativeName(alt_names), False)
            .sign(ca_key, hashes.SHA256()))

    out_dir = certs_dir / domain
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{domain}.key").write_bytes(
        key.private_bytes(serialization.Encoding.PEM,
                          serialization.PrivateFormat.TraditionalOpenSSL,
                          serialization.NoEncryption()))
    (out_dir / f"{domain}.crt").write_bytes(
        cert.public_bytes(serialization.Encoding.PEM))

    typer.echo(f"✅  certificate for '{domain}' → {out_dir}")
