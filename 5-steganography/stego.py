"""LSB-стеганография: текст прячется в младших битах пикселей PNG; опционально XOR-шифр ключом."""
import sys

import numpy as np
from PIL import Image

MARK = b"\x00STG"  # признак конца сообщения, чтобы декодер знал, где остановиться


def _xor(data: bytes, key: bytes) -> bytes:
    if not key:
        return data
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encode_text(src: str, dst: str, text: str, key: bytes = b"") -> None:
    img = np.array(Image.open(src).convert("RGB"))
    payload = _xor(text.encode("utf-8"), key) + MARK
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    flat = img.reshape(-1)
    if bits.size > flat.size:
        raise ValueError("Сообщение не помещается в изображение")
    flat[:bits.size] = (flat[:bits.size] & 0xFE) | bits  # меняем только младший бит
    Image.fromarray(img).save(dst, "PNG")  # PNG без потерь, иначе JPEG сотрёт биты


def decode_text(path: str, key: bytes = b"") -> str:
    flat = np.array(Image.open(path).convert("RGB")).reshape(-1)
    raw = np.packbits(flat & 1).tobytes()
    end = raw.find(MARK)
    if end == -1:
        raise ValueError("Скрытое сообщение не найдено")
    return _xor(raw[:end], key).decode("utf-8")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "encode":
        encode_text(sys.argv[2], sys.argv[3], sys.argv[4])
        print("Сохранено:", sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == "decode":
        print(decode_text(sys.argv[2]))
    else:
        print("Использование: stego.py encode <вход.png> <выход.png> <текст> | decode <файл.png>")
