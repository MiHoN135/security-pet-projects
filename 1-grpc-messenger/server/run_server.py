"""Сервер мессенджера: аутентификация (SQLite) + рассылка сообщений через gRPC."""
import hashlib
import os
import queue
import secrets
import sqlite3
import sys
import threading
import time
from concurrent import futures

import grpc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generated import auth_pb2, auth_pb2_grpc, messaging_pb2, messaging_pb2_grpc  # noqa: E402

DB = os.environ.get("MESSENGER_DB", "users.db")


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


class AuthService(auth_pb2_grpc.AuthServicer):
    def __init__(self, db: sqlite3.Connection, lock: threading.Lock, tokens: dict):
        self.db, self.lock, self.tokens = db, lock, tokens

    def Register(self, request, context):
        if not request.username or not request.password:
            return auth_pb2.StatusReply(ok=False, error="Пустой логин или пароль")
        salt = secrets.token_hex(8)
        try:
            with self.lock:
                self.db.execute("INSERT INTO users VALUES (?, ?, ?)",
                                (request.username, salt, _hash(request.password, salt)))
                self.db.commit()
        except sqlite3.IntegrityError:
            return auth_pb2.StatusReply(ok=False, error="Пользователь уже существует")
        return auth_pb2.StatusReply(ok=True)

    def Login(self, request, context):
        with self.lock:
            row = self.db.execute("SELECT salt, pw_hash FROM users WHERE username = ?",
                                  (request.username,)).fetchone()
        if not row or not secrets.compare_digest(_hash(request.password, row[0]), row[1]):
            return auth_pb2.LoginReply(ok=False, error="Неверный логин или пароль")
        token = secrets.token_urlsafe(24)
        self.tokens[token] = request.username
        return auth_pb2.LoginReply(ok=True, token=token)


class MessagingService(messaging_pb2_grpc.MessagingServicer):
    def __init__(self):
        self.subscribers = {}  # user -> Queue
        self.lock = threading.Lock()

    def SendMessage(self, request, context):
        msg = messaging_pb2.Message(sender=request.sender, text=request.text,
                                    clock=int(time.time()))
        with self.lock:
            for q in self.subscribers.values():
                q.put(msg)
        return messaging_pb2.SendReply(ok=True)

    def MessageStream(self, request, context):
        q = queue.Queue()
        with self.lock:
            self.subscribers[request.user] = q
        try:
            while context.is_active():
                try:
                    yield q.get(timeout=1)
                except queue.Empty:
                    continue
        finally:
            with self.lock:
                self.subscribers.pop(request.user, None)


def serve(port: int = 50051, block: bool = True):
    db = sqlite3.connect(DB, check_same_thread=False)
    db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt TEXT, pw_hash TEXT)")
    lock, tokens = threading.Lock(), {}
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
    auth_pb2_grpc.add_AuthServicer_to_server(AuthService(db, lock, tokens), server)
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingService(), server)
    bound = server.add_insecure_port(f"[::]:{port}")
    server.start()
    if block:
        print(f"Сервер запущен на порту {port}")
        server.wait_for_termination()
    return server, bound


if __name__ == "__main__":
    serve()
