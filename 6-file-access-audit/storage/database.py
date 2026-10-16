"""SQLite-хранилище: пользователи, права доступа, журнал аудита."""
import sqlite3
from pathlib import Path

from auth.passwords import hash_password, verify_password


class Database:
    def __init__(self, path: str = "audit.db"):
        self.path = path
        # создаём каталог под БД, если его нет
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row  # доступ к колонкам по имени
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS permissions (username TEXT, filename TEXT, perm TEXT, "
                    "PRIMARY KEY (username, filename, perm))")
        cur.execute("CREATE TABLE IF NOT EXISTS audit (ts TEXT, username TEXT, action TEXT, "
                    "filename TEXT, status TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS groups (group_name TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS group_members (username TEXT, group_name TEXT, "
                    "PRIMARY KEY (username, group_name))")
        self.conn.commit()

    def has_admin(self) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE role='admin'")
            return cur.fetchone() is not None
        except Exception as e:
            print(f"Ошибка проверки наличия администратора: {e}")
            return False

    def create_user(self, username, password, role):
        try:
            cur = self.conn.cursor()
            # Проверяем, не существует ли уже пользователь
            cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if cur.fetchone():
                raise ValueError(f"Пользователь '{username}' уже существует")

            cur.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (username, hash_password(password), role),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def authenticate(self, username, password):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT password, role FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            if not row:
                return None
            if verify_password(row["password"], password):
                return row["role"]
            return None
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return None

    def grant(self, username, filename, perm):
        try:
            cur = self.conn.cursor()
            # Проверяем существование пользователя
            cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if not cur.fetchone():
                raise ValueError(f"Пользователь '{username}' не существует")

            cur.execute("INSERT OR REPLACE INTO permissions VALUES (?, ?, ?)", (username, filename, perm))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def has_permission(self, username, filename, perm) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1 FROM permissions WHERE username=? AND filename=? AND perm=?",
                        (username, filename, perm))
            return cur.fetchone() is not None
        except Exception as e:
            print(f"Ошибка проверки прав: {e}")
            return False

    def get_role(self, username):
        cur = self.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return row["role"] if row else None

    def fetch_audit(self, limit=20):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM audit ORDER BY ts DESC LIMIT ?", (limit,))
        return cur.fetchall()
