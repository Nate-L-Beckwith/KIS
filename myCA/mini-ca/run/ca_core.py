from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

def _rsa(bits: int = 4096): return rsa.generate_private_key(65537, bits)

def new_root_ca(bits: int = 4096, cn: str = "mini‑ca root"):
    key  = _rsa(bits)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), True)
        .sign(key, hashes.SHA256())
    )
    return key, cert

def issue_cert(ca_key, ca_cert, host: str, sans: list[str], days: int, bits=2048):
    key   = _rsa(bits)
    subj  = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, host)])
    cert  = (
        x509.CertificateBuilder()
        .subject_name(subj).issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(h) for h in sans]), False
        )
        .sign(ca_key, hashes.SHA256())
    )
    return key, cert
