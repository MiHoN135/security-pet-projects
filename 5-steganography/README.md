# Стеганография: LSB в PNG

Текст записывается в младший бит каждого байта цветового канала. Визуально картинка не меняется (отличие не больше 1 единицы в канале). Перед записью текст можно зашифровать XOR-ключом.

PNG обязателен: JPEG с потерями стирает младшие биты.

```bash
pip install pillow numpy
python3 stego.py encode image.png encoded.png "секретный текст"
python3 stego.py decode encoded.png
python3 test_stego.py
```
