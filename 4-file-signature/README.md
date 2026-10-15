# Проверка целостности файла: SHA-256 и RSA-PSS

- `calculate_file_hash` — SHA-256 файла (читает блоками, подходит для больших файлов)
- `sign_file` — подпись RSA-PSS хеша файла приватным ключом
- `verify_file` — проверка подписи публичным ключом

CLI:
```bash
pip install cryptography
python3 main.py keygen --out key
python3 main.py hash document.pdf
python3 main.py sign document.pdf --key key.pem          # создаст document.pdf.sig
python3 main.py verify document.pdf --sig document.pdf.sig --pub key.pub.pem
```

Тесты: `python3 test_sign.py`
