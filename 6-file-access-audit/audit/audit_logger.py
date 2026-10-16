"""Запись каждой операции (успешной и неуспешной) в таблицу audit."""
from datetime import datetime, timezone


def log(db, username, action, filename, status):
    ts = datetime.now(timezone.utc).isoformat()
    cur = db.conn.cursor()
    cur.execute(
        "INSERT INTO audit VALUES (?, ?, ?, ?, ?)",
        (ts, username, action, filename, status),
    )
    db.conn.commit()
