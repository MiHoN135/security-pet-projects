import os
import tempfile

from sign_impl import SignImpl


def test_sign_and_verify_detects_tampering():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "doc.txt")
    with open(path, "wb") as f:
        f.write(b"contract v1")
    s = SignImpl()
    sig = s.sign_file(path)
    assert s.verify_file(path, sig)
    with open(path, "wb") as f:
        f.write(b"contract v2")
    assert not s.verify_file(path, sig)


def test_hash_is_sha256():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "x")
    with open(path, "wb") as f:
        f.write(b"abc")
    assert SignImpl.calculate_file_hash(path) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


if __name__ == "__main__":
    test_sign_and_verify_detects_tampering()
    test_hash_is_sha256()
    print("OK")
