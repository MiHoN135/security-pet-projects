"""CLI: python main.py keygen|sign|verify|hash <файл> ..."""
import argparse
import sys

from cryptography.hazmat.primitives import serialization

from sign_impl import SignImpl


def load_private(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("keygen").add_argument("--out", default="key")
    sign = sub.add_parser("sign")
    sign.add_argument("file")
    sign.add_argument("--key", default="key.pem")
    verify = sub.add_parser("verify")
    verify.add_argument("file")
    verify.add_argument("--sig", required=True)
    verify.add_argument("--pub", default="key.pub.pem")
    sub.add_parser("hash").add_argument("file")
    a = p.parse_args(argv)

    if a.cmd == "keygen":
        s = SignImpl()
        s.save_pk(a.out + ".pem")
        s.save_pbk(a.out + ".pub.pem")
        print(f"Ключи сохранены: {a.out}.pem, {a.out}.pub.pem")
    elif a.cmd == "sign":
        s = SignImpl(load_private(a.key))
        with open(a.file + ".sig", "wb") as f:
            f.write(s.sign_file(a.file))
        print(f"Подпись: {a.file}.sig")
    elif a.cmd == "verify":
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        with open(a.pub, "rb") as f:
            pub = load_pem_public_key(f.read())
        s = SignImpl()
        s.public_key = pub
        with open(a.sig, "rb") as f:
            ok = s.verify_file(a.file, f.read())
        print("ПОДПИСЬ ВЕРНА" if ok else "ФАЙЛ ИЗМЕНЁН ИЛИ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА")
        return 0 if ok else 1
    elif a.cmd == "hash":
        print(SignImpl.calculate_file_hash(a.file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
