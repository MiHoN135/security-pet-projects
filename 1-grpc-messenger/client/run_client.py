"""Консольный клиент: /register, /login, затем сообщения. Входящие печатаются фоновым потоком."""
import os
import sys
import threading
import time

import grpc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generated import auth_pb2, auth_pb2_grpc, messaging_pb2, messaging_pb2_grpc  # noqa: E402


def run(address: str = "localhost:50051"):
    channel = grpc.insecure_channel(address)
    auth = auth_pb2_grpc.AuthStub(channel)
    chat = messaging_pb2_grpc.MessagingStub(channel)
    user = None
    print("Команды: /register  /login  /quit")
    while user is None:
        cmd = input("> ").strip()
        if cmd == "/quit":
            return
        if cmd not in ("/register", "/login"):
            print("Неизвестная команда")
            continue
        login = input("Логин: ").strip()
        password = input("Пароль: ")
        if cmd == "/register":
            r = auth.Register(auth_pb2.AuthRequest(username=login, password=password))
            print("Зарегистрирован, теперь /login" if r.ok else f"Ошибка: {r.error}")
        else:
            r = auth.Login(auth_pb2.AuthRequest(username=login, password=password))
            if r.ok:
                user = login
                print(f"Вход выполнен: {login}")
            else:
                print(f"Ошибка: {r.error}")

    def listen():
        for m in chat.MessageStream(messaging_pb2.StreamRequest(user=user)):
            print(f"\n[{time.strftime('%H:%M:%S', time.localtime(m.clock))}] {m.sender}: {m.text}\n> ",
                  end="")

    threading.Thread(target=listen, daemon=True).start()
    while True:
        text = input("> ")
        if text == "/quit":
            return
        if text:
            chat.SendMessage(messaging_pb2.SendRequest(sender=user, text=text))


if __name__ == "__main__":
    run()
