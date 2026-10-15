# gRPC-мессенджер с аутентификацией

Сервер хранит пользователей в SQLite (пароли — PBKDF2-SHA256 с солью), клиент — консольный.
Сообщения рассылаются всем подключённым пользователям через server-streaming `MessageStream`.

## Структура
- `proto/` — описания `auth.proto` и `messaging.proto`
- `generated/` — код, сгенерированный protoc
- `server/run_server.py` — сервер
- `client/run_client.py` — консольный клиент
- `test_messenger.py` — сквозной тест

## Запуск
```bash
pip install grpcio grpcio-tools
python3 -m grpc_tools.protoc -I proto --python_out=generated --grpc_python_out=generated proto/*.proto
python3 server/run_server.py          # в одном терминале
python3 client/run_client.py          # в другом, повторить для второго пользователя
```
Клиент: `/register`, затем `/login`, потом пишите сообщения.
