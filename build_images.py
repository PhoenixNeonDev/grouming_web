#!/usr/bin/env python3
"""
Пересборка фотографий в index.html.

Когда делать: если вы заменили фото в папке images/ своими.
Что делает: сжимает каждое фото и встраивает его в index.html (data-URI),
чтобы страница оставалась одним самодостаточным файлом.

Запуск из корня проекта:
    python3 build_images.py
Требуется Pillow:  pip install pillow
"""
import base64
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('Нужен Pillow: pip install pillow')

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, 'index.html')
IMG_DIR = os.path.join(ROOT, 'images')

# ключ в HTML -> (файл, ширина, высота, качество JPEG)
MAP = {
    'hero':     ('hero.jpg',     1160, 648, 80),
    'before1':  ('before1.jpg',   900, 491, 78),
    'after1':   ('after1.jpg',    900, 491, 78),
    'before2':  ('before2.jpg',   900, 491, 78),
    'after2':   ('after2.jpg',    900, 491, 78),
    'before3':  ('before3.jpg',   900, 491, 78),
    'after3':   ('after3.jpg',    900, 491, 78),
    'master1':  ('master1.jpg',   620, 620, 78),
    'master2':  ('master2.jpg',   620, 620, 78),
    'master3':  ('master3.jpg',   620, 620, 78),
}

# как ключ называется в HTML: %%IMG_HERO%%, %%IMG_BEFORE_1%% и т. д.
def token(key: str) -> str:
    m = re.match(r'([a-z]+)(\d*)$', key)
    name, num = m.group(1), m.group(2)
    return f'%%IMG_{name.upper()}{"_" + num if num else ""}%%'


def to_data_uri(path, w, h, q):
    im = Image.open(path).convert('RGB')
    im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
    data = buf.getvalue()
    print(f'  {os.path.basename(path):<14} {w}x{h}  {len(data) / 1024:5.0f} KB')
    return 'data:image/jpeg;base64,' + base64.b64encode(data).decode()


def main():
    if not os.path.exists(HTML):
        sys.exit('Не найден index.html — запускайте скрипт из корня проекта.')
    html = open(HTML, encoding='utf-8').read()

    print('Встраиваю фото:')
    replaced = 0
    for key, (fname, w, h, q) in MAP.items():
        path = os.path.join(IMG_DIR, fname)
        if not os.path.exists(path):
            print(f'  {fname:<14} ПРОПУЩЕН: файл не найден')
            continue
        uri = to_data_uri(path, w, h, q)
        tok = token(key)
        # заменяем либо плейсхолдер (первая сборка), либо уже встроенное фото
        pattern = re.compile(re.escape(tok) + r'|data:image/jpeg;base64,[A-Za-z0-9+/=]+')
        html, n = pattern.subn(lambda _m, u=uri: u, html, count=_count_of(html, key))
        replaced += n

    open(HTML, 'w', encoding='utf-8').write(html)
    left = re.findall(r'%%\w+%%', html)
    if left:
        print('НЕ ЗАМЕНЕНО:', left)
    print(f'Готово. Обновлено вхождений: {replaced}. Размер index.html: '
          f'{os.path.getsize(HTML) / 1024:.0f} KB')


def _count_of(html, key):
    """Сколько вхождений нужно заменить для этого ключа (по плейсхолдерам или по одному на ключ)."""
    return 1 if token(key) in html else 1 if key not in ('before1', 'after1') else 1


if __name__ == '__main__':
    main()
