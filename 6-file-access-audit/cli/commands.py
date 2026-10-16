"""Имена команд консоли. Enum защищает от опечаток в строках."""
from enum import Enum


class Command(str, Enum):
    HELP = "help"
    SIGNUP = "signup"
    LOGIN = "login"
    WHOAMI = "whoami"
    CREATE_FILE = "create_file"
    GRANT = "grant"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    AUDIT = "audit_show"
    EXIT = "exit"
