HELP_TEXT = """
Доступные команды:

Аутентификация
  signup <username> <password>      - создать пользователя
  login <username> <password>       - войти и получить JWT
  whoami <token>                    - показать пользователя по токену

Файлы
  create_file <token> <file>        - создать файл (admin)
  read <token> <file>               - читать файл
  write <token> <file> <text>       - писать в файл
  delete <token> <file>             - удалить файл

Права
  grant <token> <user> <file> <perm>
    perm = read | write | delete

Аудит
  audit_show                        - показать журнал аудита

Выход
  exit

Примеры:
  signup admin admin123
  login admin admin123
  create_file <token> file.txt
  grant <token> user1 file.txt read
  read <token> file.txt
  write <token> file.txt Hello World
  audit_show
"""
