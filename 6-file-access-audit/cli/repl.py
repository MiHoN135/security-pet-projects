"""Интерактивная консоль: читает команду, вызывает обработчик с аргументами из строки."""
from cli.commands import Command
from cli.handlers import (handle_audit, handle_create_file, handle_delete, handle_grant,
                          handle_login, handle_read, handle_signup, handle_whoami, handle_write)
from cli.help_text import HELP_TEXT


class REPL:
    def __init__(self, db):
        self.db = db
        self.handlers = {
            Command.SIGNUP: handle_signup,
            Command.LOGIN: handle_login,
            Command.WHOAMI: handle_whoami,
            Command.CREATE_FILE: handle_create_file,
            Command.GRANT: handle_grant,
            Command.READ: handle_read,
            Command.WRITE: handle_write,
            Command.DELETE: handle_delete,
            Command.AUDIT: handle_audit,
        }

    def run(self):
        print("Система аудита доступа к файлам. Введите 'help'.")
        while True:
            try:
                raw = input("cmd> ").strip()
                if not raw:
                    continue

                parts = raw.split()
                cmd = parts[0]
                args = parts[1:]

                if cmd == Command.HELP:
                    print(HELP_TEXT)
                    continue

                if cmd == Command.EXIT:
                    print("Выход.")
                    break

                handler = self.handlers.get(cmd)
                if not handler:
                    print("Неизвестная команда. Введите 'help'.")
                    continue

                handler(self.db, *args)
            except TypeError as e:
                print(f"Неверное количество аргументов: {e}. Введите 'help'.")
            except Exception as e:
                print(f"Ошибка выполнения команды: {e}")
