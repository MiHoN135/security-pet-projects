import os
import tempfile

import numpy as np
from PIL import Image

from stego import decode_text, encode_text


def test_round_trip_keeps_image_visually_same():
    d = tempfile.mkdtemp()
    src, dst = os.path.join(d, "a.png"), os.path.join(d, "b.png")
    Image.fromarray(np.random.default_rng(0).integers(0, 256, (64, 64, 3), dtype=np.uint8)).save(src)
    encode_text(src, dst, "Привет, мир!", key=b"k")
    assert decode_text(dst, key=b"k") == "Привет, мир!"
    diff = np.abs(np.array(Image.open(src)).astype(int) - np.array(Image.open(dst)).astype(int))
    assert diff.max() <= 1  # изменился только младший бит


if __name__ == "__main__":
    test_round_trip_keeps_image_visually_same()
    print("OK")
