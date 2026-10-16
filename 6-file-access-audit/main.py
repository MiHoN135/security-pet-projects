"""Точка входа: python main.py [путь_к_БД]"""
import sys

from cli.repl import REPL
from storage.database import Database


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else "audit.db"
    REPL(Database(db_path)).run()


if __name__ == "__main__":
    main()
