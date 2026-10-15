"""Простой DLP: проверка сообщений по правилам из rules.json, правила перечитываются на лету."""
import json
import os
import re
import threading
import time
from dataclasses import dataclass


@dataclass
class DLPResult:
    allowed: bool
    reason: str = ""


class DLPService:
    def __init__(self, rules_path: str, reload_interval: float = 5.0):
        self.rules_path = rules_path
        self.rules = self.load_rules(rules_path)
        self._mtime = os.path.getmtime(rules_path)
        # фоновое обновление: изменили rules.json — правила применятся без перезапуска сервера
        threading.Thread(target=self.watch_config, args=(reload_interval,), daemon=True).start()

    @staticmethod
    def load_rules(path: str) -> list:
        with open(path, encoding="utf-8") as f:
            return [
                {**r, "compiled": re.compile(r["pattern"])} for r in json.load(f)
            ]

    def check(self, message: str) -> DLPResult:
        for rule in self.rules:
            if rule["compiled"].search(message):
                if rule["action"] == "block":
                    return DLPResult(False, rule["reason"])
                # action=warn: сообщение проходит, но событие фиксируется в логе
                print(f"[DLP warn] {rule['reason']}")
        return DLPResult(True)

    def watch_config(self, interval: float):
        while True:
            time.sleep(interval)
            try:
                mtime = os.path.getmtime(self.rules_path)
                if mtime != self._mtime:
                    self.rules = self.load_rules(self.rules_path)
                    self._mtime = mtime
            except (OSError, ValueError, KeyError, re.error) as e:
                # битый файл не должен ронять сервер: оставляем прежние правила
                print(f"[DLP] не удалось перечитать правила: {e}")
