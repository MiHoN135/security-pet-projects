"""TOTP (RFC 6238) на стандартной библиотеке: генерация секрета, код, проверка, QR-URI."""
import base64
import hmac
import secrets
import struct
import time
from typing import Optional
from urllib.parse import quote

STEP = 30  # секунд на один код
DIGITS = 6


def generate_secret() -> str:
    # 160 бит, base32 без паддинга — формат, который понимают Google Authenticator и Яндекс.Ключ
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def code_at(secret: str, timestamp: float) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    counter = struct.pack(">Q", int(timestamp) // STEP)
    digest = hmac.new(key, counter, "sha1").digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(value % 10 ** DIGITS).zfill(DIGITS)


def verify(secret: str, code: str, window: int = 1, now: Optional[float] = None) -> bool:
    # window=1 допускает соседние 30-секундные интервалы (сдвиг часов)
    now = time.time() if now is None else now
    if not (code.isdigit() and len(code) == DIGITS):
        return False
    return any(
        hmac.compare_digest(code_at(secret, now + i * STEP), code)
        for i in range(-window, window + 1)
    )


def provisioning_uri(secret: str, user: str, issuer: str = "Messenger") -> str:
    label = quote(f"{issuer}:{user}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}"
