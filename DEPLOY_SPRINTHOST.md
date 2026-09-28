# Публикация сайта на Sprinthost

В отличие от PythonAnywhere (см. `DEPLOY.md`), Sprinthost — обычный
виртуальный хостинг с доступом по SSH, где Python-приложение запускается
через модуль **uWSGI** для Apache. Домен уже должен быть подключён к
хостингу (свой или поддомен sprinthost).

Официальная инструкция хостера: https://help.sprinthost.ru/framework/django
и https://help.sprinthost.ru/howto/python — ниже те же шаги, но подставлены
под структуру именно этого проекта (модуль настроек — `config.settings`,
зависимости — в `requirements.txt`).

## Шаг 1. Выложить код на GitHub

Если ещё не делали:

```bash
git add -A
git commit -m "Подготовка к деплою"
git remote add origin https://github.com/<ваш-логин>/<название-репо>.git
git branch -M main
git push -u origin main
```

## Шаг 2. Включить Python для домена

В панели управления (`cp.sprinthost.ru`): **«Сайты» → «Веб-серверы»** →
у нужного домена выберите версию Python (берите самую новую из
предложенных, например 3.13 — Django 6.1 требует свежий Python).

## Шаг 3. Зайти по SSH и создать виртуальное окружение

```bash
ssh <логин>@<ваш-сервер>.sprinthost.ru
pip install virtualenv --user
virtualenv --system-site-packages python
source ~/python/bin/activate
```

Окружение лежит в `~/python`. Активировать его нужно заново при каждом
новом SSH-подключении.

## Шаг 4. Склонировать проект и поставить зависимости

Проект разворачивается **рядом с** `public_html`, а не внутри него —
наружу торчит только файл `site.wsgi`:

```bash
cd ~/domains/<ваш-домен>/
git clone https://github.com/<ваш-логин>/<название-репо>.git myproject
cd myproject
pip install -r requirements.txt
```

### Если Django ругается на версию SQLite

На некоторых тарифах системный `sqlite3` старее, чем требует Django 6.1.
Если при `migrate` увидите ошибку про версию SQLite:

```bash
pip install pysqlite3-binary
```

и добавьте в самое начало `manage.py` и `config/wsgi.py` (после
`import os`, перед остальным кодом):

```python
__import__("pysqlite3")
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
```

## Шаг 5. Настроить `site.wsgi`

Создайте файл `~/domains/<ваш-домен>/public_html/site.wsgi`:

```python
import os
import sys

activate_this = "/home/<логин>/python/bin/activate_this.py"
with open(activate_this) as f:
    exec(f.read(), {"__file__": activate_this})

sys.path.insert(0, "/home/<логин>/domains/<ваш-домен>/myproject")

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<ваш-домен>,www.<ваш-домен>"
os.environ["DJANGO_SECRET_KEY"] = "<сгенерированный-секретный-ключ>"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Секретный ключ сгенерируйте (в активном virtualenv):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Шаг 6. Подключить uWSGI в `.htaccess`

Создайте `~/domains/<ваш-домен>/public_html/.htaccess`:

```apache
DirectoryIndex site.wsgi
Options +ExecCGI
AddHandler wsgi-script .wsgi
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /site.wsgi/$1 [QSA,PT,L]
```

Правила `RewriteCond ... !-f` и `!-d` пропускают напрямую (без WSGI) любой
запрос, которому соответствует реальный файл или папка на диске — это
важно для статики и медиа на следующем шаге.

## Шаг 7. Собрать статику и подключить медиа

В проекте `STATIC_ROOT`/`MEDIA_ROOT` смотрят внутрь `myproject/`, а не в
`public_html/`, поэтому веб-сервер их напрямую не видит — свяжите
симлинками:

```bash
cd ~/domains/<ваш-домен>/myproject
python manage.py collectstatic --noinput

ln -s ~/domains/<ваш-домен>/myproject/staticfiles ~/domains/<ваш-домен>/public_html/static
ln -s ~/domains/<ваш-домен>/myproject/media ~/domains/<ваш-домен>/public_html/media
```

## Шаг 8. Применить миграции и создать администратора

```bash
python manage.py migrate
python manage.py createsuperuser
```

Если нужно сразу заполнить сайт стартовыми текстами:

```bash
python manage.py seed_demo_data
```

## Шаг 9. Перезапустить приложение

После первого запуска и после каждого обновления кода uWSGI-процесс нужно
перезапустить — на большинстве хостингов с таким модулем это делается
командой `touch` по wsgi-файлу:

```bash
touch ~/domains/<ваш-домен>/public_html/site.wsgi
```

Если после этого изменения не подхватились — перезапустите через
соответствующую кнопку в панели («Сайты» → «Веб-серверы») или напишите
в поддержку Sprinthost, у разных тарифов перезапуск воркеров может
отличаться.

## Шаг 10. Включить HTTPS

В панели: **«Сайты» → SSL** — подключите бесплатный сертификат Let's
Encrypt для домена. `CSRF_TRUSTED_ORIGINS` в `config/settings.py` уже
считается автоматически из `DJANGO_ALLOWED_HOSTS`, дополнительно ничего
менять не нужно.

## Обновление сайта после правок в коде

```bash
cd ~/domains/<ваш-домен>/myproject
source ~/python/bin/activate
git pull
pip install -r requirements.txt   # если менялись зависимости
python manage.py migrate          # если менялись модели
python manage.py collectstatic --noinput
touch ~/domains/<ваш-домен>/public_html/site.wsgi
```

## Важно

- Пароль администратора, использованный при локальной разработке,
  действует только локально — на хостинге вы создаёте нового
  суперпользователя на шаге 8 со своим паролем.
- `db.sqlite3` и папка `media/` (загруженные фото и файлы) хранятся на
  диске хостинга постоянно, в отличие от Netlify/Vercel — ничего не
  пропадёт при перезапуске.
