from totp import code_at, generate_secret, verify

# Тестовый вектор RFC 6238 (SHA-1): секрет "12345678901234567890", T=59 -> 8 цифр 94287082, 6 цифр 287082
RFC_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


def test_rfc6238_vector():
    assert code_at(RFC_SECRET, 59) == "287082"


def test_verify_accepts_current_and_neighbour_window():
    s = generate_secret()
    assert verify(s, code_at(s, 1000), now=1000)
    assert verify(s, code_at(s, 1000 + 30), now=1000)  # соседний интервал
    assert not verify(s, code_at(s, 1000 + 300), now=1000)


def test_rejects_bad_input():
    s = generate_secret()
    assert not verify(s, "abc123", now=1000)
    assert not verify(s, "12345", now=1000)


if __name__ == "__main__":
    test_rfc6238_vector()
    test_verify_accepts_current_and_neighbour_window()
    test_rejects_bad_input()
    print("OK")
