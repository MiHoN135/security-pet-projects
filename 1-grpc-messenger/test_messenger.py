"""Сквозная проверка: регистрация, вход, неверный пароль, доставка сообщения подписчику."""
import os
import sys
import tempfile
import threading
import time

os.environ["MESSENGER_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))
sys.path.insert(0, os.path.dirname(__file__))

import grpc  # noqa: E402
import run_server  # noqa: E402
from generated import auth_pb2, auth_pb2_grpc, messaging_pb2, messaging_pb2_grpc  # noqa: E402


def test_end_to_end():
    server, port = run_server.serve(port=0, block=False)
    ch = grpc.insecure_channel(f"localhost:{port}")
    auth = auth_pb2_grpc.AuthStub(ch)
    chat = messaging_pb2_grpc.MessagingStub(ch)

    assert auth.Register(auth_pb2.AuthRequest(username="ann", password="pw")).ok
    assert not auth.Register(auth_pb2.AuthRequest(username="ann", password="pw")).ok
    assert not auth.Login(auth_pb2.AuthRequest(username="ann", password="bad")).ok
    assert auth.Login(auth_pb2.AuthRequest(username="ann", password="pw")).token

    got = []
    stream = chat.MessageStream(messaging_pb2.StreamRequest(user="ann"))
    threading.Thread(target=lambda: got.append(next(stream)), daemon=True).start()
    time.sleep(0.3)
    chat.SendMessage(messaging_pb2.SendRequest(sender="bob", text="привет"))
    for _ in range(50):
        if got:
            break
        time.sleep(0.1)
    assert got and got[0].text == "привет" and got[0].sender == "bob"
    server.stop(0)


if __name__ == "__main__":
    test_end_to_end()
    print("OK")
