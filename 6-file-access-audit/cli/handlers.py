"""Обработчики команд: проверяют аргументы, токен и права, пишут в аудит."""
from audit.audit_logger import log
from auth.jwt_service import create_token, decode_token
from auth.passwords import is_password_strong
from fs.secure_file import SecureFile
from storage.models import ROLE_ADMIN, ROLE_USER, STATUS_ALLOWED, STATUS_DENIED, STATUS_ERROR


def _token_data(token):
    try:
        return decode_token(token)
    except ValueError as e:
        print(f"Невалидный токен: {e}")
        return None


def handle_signup(db, username, password):
    if len(username) == 0 or len(password) == 0:
        print("Имя пользователя и пароль не могут быть пустыми")
        return

    if not is_password_strong(password):
        print("Пароль должен быть не менее 8 символов и содержать буквы и цифры")
        log(db, username, "signup", "-", STATUS_DENIED)
        return

    # первый зарегистрированный пользователь становится администратором
    if not db.has_admin():
        print("[BOOTSTRAP] Создание первого администратора")
        role = ROLE_ADMIN
    else:
        role = ROLE_USER

    try:
        db.create_user(username, password, role)
        log(db, username, "signup", "-", STATUS_ALLOWED)
        print(f"Пользователь '{username}' создан (роль: {role})")
    except Exception as e:
        log(db, username, "signup", "-", STATUS_ERROR)
        print("Ошибка создания пользователя:", e)


def handle_login(db, username, password):
    if len(username) == 0 or len(password) == 0:
        print("Имя пользователя и пароль не могут быть пустыми")
        return

    role = db.authenticate(username, password)
    if not role:
        log(db, username, "login", "-", STATUS_DENIED)
        print("Ошибка авторизации")
        return

    log(db, username, "login", "-", STATUS_ALLOWED)
    token = create_token(username, role)
    print("JWT token:")
    print(token)


def handle_whoami(db, token):
    data = _token_data(token)
    if data:
        print(f"Пользователь: {data['username']}, роль: {data['role']}")


def handle_create_file(db, token, filename):
    if len(filename) == 0:
        print("Имя файла не может быть пустым")
        return

    data = _token_data(token)
    if not data:
        return

    if data["role"] != ROLE_ADMIN:
        log(db, data["username"], "create_file", filename, STATUS_DENIED)
        print("Только администратор может создавать файлы")
        return

    try:
        with open(filename, "w", encoding="utf-8") as f:
            pass  # создаём пустой файл
        log(db, data["username"], "create_file", filename, STATUS_ALLOWED)
        print(f"Файл '{filename}' создан")
    except Exception as e:
        log(db, data["username"], "create_file", filename, STATUS_ERROR)
        print(f"Ошибка создания файла: {e}")


def handle_grant(db, token, user, filename, perm):
    if len(user) == 0 or len(filename) == 0 or len(perm) == 0:
        print("Все параметры (user, filename, perm) обязательны")
        return

    if perm not in ["read", "write", "delete"]:
        print("Разрешение должно быть одно из: read, write, delete")
        return

    data = _token_data(token)
    if not data:
        return

    if data["role"] != ROLE_ADMIN:
        log(db, data["username"], "grant", filename, STATUS_DENIED)
        print("Только администратор может выдавать права")
        return

    try:
        db.grant(user, filename, perm)
        log(db, data["username"], "grant", filename, STATUS_ALLOWED)
        print("Право выдано")
    except Exception as e:
        log(db, data["username"], "grant", filename, STATUS_ERROR)
        print(f"Ошибка выдачи прав: {e}")


def handle_read(db, token, filename):
    if len(filename) == 0:
        print("Имя файла не может быть пустым")
        return

    try:
        data = decode_token(token)
        sf = SecureFile(filename, db)
        content = sf.read(data["username"])
        print("=== file content ===")
        print(content)
    except ValueError as e:
        print(f"Ошибка токена: {e}")
    except PermissionError:
        print("Нет прав на чтение")
    except FileNotFoundError:
        print("Файл не найден")
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")


def handle_write(db, token, filename, *text_parts):
    if len(filename) == 0:
        print("Имя файла не может быть пустым")
        return

    if len(text_parts) == 0:
        print("Текст для записи не может быть пустым")
        return

    text = " ".join(text_parts)
    try:
        data = decode_token(token)
        sf = SecureFile(filename, db)
        sf.write(data["username"], text)
        print("Запись выполнена")
    except ValueError as e:
        print(f"Ошибка токена: {e}")
    except PermissionError:
        print("Нет прав на запись")
    except Exception as e:
        print(f"Ошибка записи: {e}")


def handle_delete(db, token, filename):
    if len(filename) == 0:
        print("Имя файла не может быть пустым")
        return

    try:
        data = decode_token(token)
        SecureFile(filename, db).delete(data["username"])
        print("Файл удалён")
    except ValueError as e:
        print(f"Ошибка токена: {e}")
    except PermissionError:
        print("Нет прав на удаление")
    except FileNotFoundError:
        print("Файл не найден")
    except Exception as e:
        print(f"Ошибка удаления файла: {e}")


def handle_audit(db):
    rows = db.fetch_audit(20)
    if not rows:
        print("Журнал аудита пуст")
        return

    print("=== Последние 20 записей аудита ===")
    print("Время (UTC) | Пользователь | Действие | Файл | Статус")
    print("-" * 60)
    for r in rows:
        print(f"{r[0][:19]} | {r[1]:10} | {r[2]:10} | {r[3]:15} | {r[4]}")
