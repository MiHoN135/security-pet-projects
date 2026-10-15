import os
import tempfile
import time
import json

from dlp import DLPService

RULES = os.path.join(os.path.dirname(__file__), "rules.json")


def test_block_and_allow():
    svc = DLPService(RULES, reload_interval=999)
    assert svc.check("Привет!").allowed
    r = svc.check("1234-5678-9012-3456")
    assert not r.allowed and r.reason == "Обнаружен номер кредитной карты"
    r = svc.check("Мой паспорт 1234 №567890")
    assert not r.allowed and r.reason == "Обнаружен номер паспорта"
    assert svc.check("+71234567890").allowed  # warn не блокирует


def test_hot_reload():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump([], f)
    svc = DLPService(f.name, reload_interval=0.1)
    assert svc.check("1234-5678-9012-3456").allowed
    time.sleep(0.05)
    with open(f.name, "w", encoding="utf-8") as fh:
        json.dump(json.load(open(RULES, encoding="utf-8")), fh)
    os.utime(f.name, (time.time() + 5, time.time() + 5))
    time.sleep(0.4)
    assert not svc.check("1234-5678-9012-3456").allowed


if __name__ == "__main__":
    test_block_and_allow()
    test_hot_reload()
    print("OK")
