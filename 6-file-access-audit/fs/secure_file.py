"""Файл под контролем доступа: каждая операция проверяется по правам и пишется в аудит."""
import os

from audit.audit_logger import log
from storage.models import ROLE_ADMIN, STATUS_ALLOWED, STATUS_DENIED, STATUS_ERROR


class SecureFile:
    def __init__(self, filename, db):
        self.filename = os.path.normpath(filename)  # защита от путей вида ../
        self.db = db

    def _check(self, username, perm):
        # администратор имеет все права автоматически
        if self.db.get_role(username) == ROLE_ADMIN:
            return True
        return self.db.has_permission(username, self.filename, perm)

    def read(self, username):
        if not self._check(username, "read"):
            log(self.db, username, "read", self.filename, STATUS_DENIED)
            raise PermissionError("Нет прав на чтение")

        if not os.path.exists(self.filename):
            log(self.db, username, "read", self.filename, STATUS_DENIED)
            raise FileNotFoundError(f"Файл '{self.filename}' не найден")

        log(self.db, username, "read", self.filename, STATUS_ALLOWED)
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            log(self.db, username, "read", self.filename, STATUS_ERROR)
            raise

    def write(self, username, text):
        if not self._check(username, "write"):
            log(self.db, username, "write", self.filename, STATUS_DENIED)
            raise PermissionError("Нет прав на запись")

        log(self.db, username, "write", self.filename, STATUS_ALLOWED)
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def delete(self, username):
        if not self._check(username, "delete"):
            log(self.db, username, "delete", self.filename, STATUS_DENIED)
            raise PermissionError("Нет прав на удаление")

        if not os.path.exists(self.filename):
            log(self.db, username, "delete", self.filename, STATUS_DENIED)
            raise FileNotFoundError(f"Файл '{self.filename}' не найден")

        try:
            os.remove(self.filename)
            log(self.db, username, "delete", self.filename, STATUS_ALLOWED)
        except Exception:
            log(self.db, username, "delete", self.filename, STATUS_ERROR)
            raise
