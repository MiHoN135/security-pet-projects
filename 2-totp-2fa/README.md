# TOTP: двухфакторная аутентификация

Реализация RFC 6238 на стандартной библиотеке Python: секрет в base32, код на 6 цифр, смена каждые 30 секунд, окно проверки ±1 интервал.

- `totp.py` — `generate_secret`, `code_at`, `verify`, `provisioning_uri` (URI для QR-кода в Google Authenticator или Яндекс.Ключе)
- `test_totp.py` — проверка по тестовому вектору RFC 6238

```bash
python3 test_totp.py
```
