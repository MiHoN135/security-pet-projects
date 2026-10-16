"""Тесты системы: регистрация, токены, права доступа, файлы и аудит."""
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from auth.jwt_service import create_token, decode_token
from auth.passwords import hash_password, is_password_strong, verify_password
from cli.handlers import handle_grant, handle_read, handle_signup, handle_write, handle_login
from fs.secure_file import SecureFile
from storage.database import Database


def run(fn, *args):
    buf = StringIO()
    with redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


class SystemTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = Database(os.path.join(self.dir, "t.db"))
        self.old_cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        self.db.conn.close()
        os.chdir(self.old_cwd)

    def test_password_rules(self):
        self.assertTrue(is_password_strong("abc12345"))
        self.assertFalse(is_password_strong("short1"))
        self.assertFalse(is_password_strong("onlyletters"))
        self.assertTrue(verify_password(hash_password("abc12345"), "abc12345"))

    def test_first_user_is_admin(self):
        run(handle_signup, self.db, "admin", "admin123")
        run(handle_signup, self.db, "user1", "user1pass")
        self.assertEqual(self.db.get_role("admin"), "admin")
        self.assertEqual(self.db.get_role("user1"), "user")

    def test_token_roundtrip_and_expiry(self):
        token = create_token("ann", "user")
        self.assertEqual(decode_token(token)["username"], "ann")
        expired = create_token("ann", "user", expires_sec=-10)
        with self.assertRaises(ValueError):
            decode_token(expired)

    def test_grant_and_access(self):
        run(handle_signup, self.db, "admin", "admin123")
        run(handle_signup, self.db, "user1", "user1pass")
        admin_t = create_token("admin", "admin")
        user_t = create_token("user1", "user")
        path = os.path.join(self.dir, "file.txt")
        open(path, "w").close()

        self.assertIn("Нет прав на чтение", run(handle_read, self.db, user_t, path))
        run(handle_grant, self.db, admin_t, "user1", path, "read")
        self.assertIn("Запись выполнена", run(handle_write, self.db, admin_t, path, "Hello"))
        self.assertIn("Hello", run(handle_read, self.db, user_t, path))
        self.assertIn("Нет прав на запись", run(handle_write, self.db, user_t, path, "x"))

    def test_non_admin_cannot_grant(self):
        run(handle_signup, self.db, "admin", "admin123")
        run(handle_signup, self.db, "user1", "user1pass")
        user_t = create_token("user1", "user")
        out = run(handle_grant, self.db, user_t, "user1", "f.txt", "read")
        self.assertIn("Только администратор", out)

    def test_audit_records_denied_and_allowed(self):
        run(handle_signup, self.db, "admin", "admin123")
        path = os.path.join(self.dir, "f.txt")
        open(path, "w").close()
        sf = SecureFile(path, self.db)
        with self.assertRaises(PermissionError):
            sf.read("nobody")
        statuses = [r[4] for r in self.db.fetch_audit(100)]
        self.assertIn("DENIED", statuses)

    def test_path_is_normalized(self):
        sf = SecureFile("dir/../file.txt", self.db)
        self.assertEqual(sf.filename, "file.txt")


if __name__ == "__main__":
    unittest.main()
