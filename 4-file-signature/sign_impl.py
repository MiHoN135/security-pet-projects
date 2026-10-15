"""Проверка целостности файла: SHA-256 хеш и подпись RSA-PSS."""
import hashlib
from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class SignImpl:
    def __init__(self, private_key: Optional[rsa.RSAPrivateKey] = None):
        self.private_key = private_key or rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

    def save_pk(self, path: str, password: Optional[bytes] = None) -> None:
        enc = (serialization.BestAvailableEncryption(password) if password
               else serialization.NoEncryption())
        with open(path, "wb") as f:
            f.write(self.private_key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, enc))

    def save_pbk(self, path: str) -> None:
        with open(path, "wb") as f:
            f.write(self.public_key.public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

    @staticmethod
    def calculate_file_hash(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def sign_file(self, path: str) -> bytes:
        # подписываем хеш файла, а не весь файл: так подпись быстрая для любого размера
        return self.private_key.sign(_digest_of(path), _pss(), hashes.SHA256())

    def verify_file(self, path: str, signature: bytes) -> bool:
        try:
            self.public_key.verify(signature, _digest_of(path), _pss(), hashes.SHA256())
            return True
        except InvalidSignature:
            return False


def _pss():
    return padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)


def _digest_of(path: str) -> bytes:
    return bytes.fromhex(SignImpl.calculate_file_hash(path))
