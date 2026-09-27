# Публикация сайта на PythonAnywhere (бесплатно)

Netlify не подходит для этого сайта: Django-админка сохраняет тексты, фото
и файлы в базу данных и на диск, а Netlify — это хостинг статики и
serverless-функций без постоянного хранилища. На **PythonAnywhere**
бесплатный аккаунт даёт постоянное хранилище файлов и базы данных, поэтому
всё, что учитель загрузит через `/admin/`, никуда не пропадёт. Домен вида
`имя-пользователя.pythonanywhere.com` выдаётся бесплатно.

## Шаг 1. Выложить код на GitHub

Если репозитория ещё нет — создайте пустой на https://github.com/new
(без README), затем из папки проекта:

```bash
git remote add origin https://github.com/<ваш-логин>/<название-репо>.git
git branch -M main
git push -u origin main
```

## Шаг 2. Завести аккаунт на PythonAnywhere

1. Зарегистрируйтесь на https://www.pythonanywhere.com/ (тариф **Beginner**, бесплатно).
2. Откройте вкладку **Consoles** → **Bash**.

## Шаг 3. Склонировать проект и установить зависимости

В открывшейся консоли:

```bash
git clone https://github.com/<ваш-логин>/<название-репо>.git russ
cd russ
mkvirtualenv --python=/usr/bin/python3.10 russ-venv
pip install -r requirements.txt
```

(`mkvirtualenv` сам активирует окружение; в следующий раз для входа в него
используйте `workon russ-venv`.)

## Шаг 4. Создать веб-приложение

1. Вкладка **Web** → **Add a new web app**.
2. Выберите **Manual configuration** (не «Django» из списка!) → тот же
   Python, что и в virtualenv (например 3.10).
3. В разделе **Virtualenv** укажите путь: `/home/<ваш-логин>/.virtualenvs/russ-venv`
4. В разделе **Code** укажите:
   - **Source code**: `/home/<ваш-логин>/russ`
   - **Working directory**: `/home/<ваш-логин>/russ`

## Шаг 5. Настроить WSGI-файл

Откройте ссылку на WSGI-файл в разделе **Code** (обычно
`/var/www/<ваш-логин>_pythonanywhere_com_wsgi.py`), **удалите всё
содержимое** и вставьте:

```python
import os
import sys

path = '/home/<ваш-логин>/russ'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = '<ваш-логин>.pythonanywhere.com'
os.environ['DJANGO_SECRET_KEY'] = '<сгенерированный-секретный-ключ>'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Секретный ключ сгенерируйте в консоли Bash (внутри активного virtualenv):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируйте результат в `DJANGO_SECRET_KEY` выше.

## Шаг 6. Применить миграции и собрать статику

В консоли Bash (`workon russ-venv`, затем `cd russ`):

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

При создании суперпользователя укажите логин и пароль, под которыми
учитель будет заходить в `/admin/`.

Если нужно сразу заполнить сайт стартовыми текстами:

```bash
python manage.py seed_demo_data
```

## Шаг 7. Указать пути к статике и медиа

Вкладка **Web** → раздел **Static files**, добавьте две записи:

| URL | Directory |
|---|---|
| `/static/` | `/home/<ваш-логин>/russ/staticfiles` |
| `/media/` | `/home/<ваш-логин>/russ/media` |

## Шаг 8. Запустить сайт

Нажмите зелёную кнопку **Reload** на вкладке **Web**. Сайт будет доступен по
адресу `https://<ваш-логин>.pythonanywhere.com/`, админка — по
`https://<ваш-логин>.pythonanywhere.com/admin/`.

## Обновление сайта после правок в коде

```bash
cd ~/russ
git pull
workon russ-venv
pip install -r requirements.txt   # если менялись зависимости
python manage.py migrate          # если менялись модели
python manage.py collectstatic --noinput
```

Затем снова нажмите **Reload** на вкладке **Web**.

## Важно

- Бесплатный тариф PythonAnywhere «усыпляет» сайт, если на него никто не
  заходил около 3 месяцев — достаточно один раз зайти на страницу
  **Web** и нажать **Run until 3 months from today**, чтобы продлить.
- Пароль администратора (`RusLit2025!`, заданный при локальной разработке)
  используется только локально — на PythonAnywhere вы создаёте нового
  суперпользователя на шаге 6 со своим паролем.
