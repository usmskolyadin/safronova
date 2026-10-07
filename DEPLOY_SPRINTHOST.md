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

Адрес сервера для подключения смотрите в панели: **«Сайты» → «Подключение
к сервисам»**, поле «Сервер» (вид `serverN.sprinthost.ru`) — не собирайте
его сами из IP-адреса, эти два варианта не совмещаются. Можно также
подключиться напрямую по IP-адресу из **«Сайты» → «IP-адреса»**.

```bash
ssh <логин>@<адрес-сервера-из-панели>
cd ~
pip install virtualenv --user
virtualenv --system-site-packages python
source ~/python/bin/activate
```

Окружение лежит в `~/python`. Активировать его нужно заново при каждом
новом SSH-подключении.

Важно выполнить `cd ~` перед `virtualenv` — на некоторых тарифах SSH-логин
приземляет не в домашний каталог, а сразу в `~/domains/<ваш-домен>/`, и
тогда `virtualenv --system-site-packages python` создаст окружение там
(`~/domains/<ваш-домен>/python`), а не в `~/python`, как ожидают следующие
шаги и `site.wsgi`. Проверить, где вы оказались после логина, можно
командой `pwd`.

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

На некоторых тарифах системный `sqlite3` старее, чем требует Django 6.1 —
при `migrate` в этом случае появится ошибка вида
`NotSupportedError: deterministic=True requires SQLite 3.8.3 or higher`.
Лечится одной командой:

```bash
pip install pysqlite3-binary
```

Код уже готов к обоим последствиям этой замены:
`config/settings.py` сам подхватывает более новую SQLite, если пакет
установлен, а `config/sqlite_compat.py` обходит то, что `pysqlite3` не
реализует `getlimit()/setlimit()` (иначе следующим шагом вылезла бы
`AttributeError: 'pysqlite3.dbapi2.Connection' object has no attribute
'getlimit'` прямо во время `migrate` — причём сразу в нескольких местах
Django, поэтому чинится не точечным патчем, а подменой класса
`Connection` через `factory=`).

После установки просто повторите `migrate` — ничего руками
патчить не нужно. Локально это прогнано end-to-end (полный `migrate` со
всеми миграциями проекта) через имитацию такого окружения — должно
сработать и у вас.

## Шаг 5. Настроить `site.wsgi`

Создайте файл `~/domains/<ваш-домен>/public_html/site.wsgi`:

```python
import glob
import os
import sys

for site_packages in glob.glob(
    "/home/<логин>/python/lib*/python3.*/site-packages"
):
    sys.path.insert(0, site_packages)

sys.path.insert(0, "/home/<логин>/domains/<ваш-домен>/myproject")

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<ваш-домен>,www.<ваш-домен>"
os.environ["DJANGO_SECRET_KEY"] = "<сгенерированный-секретный-ключ>"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Раньше здесь использовался `activate_this.py` для активации виртуального
окружения, но начиная с virtualenv 20.x этот файл больше не создаётся по
умолчанию — `open(activate_this)` падает с `FileNotFoundError`, и Apache
отдаёт 500 ещё до старта Django (без единой строчки в логах приложения,
так как падение происходит до инициализации логгера). Добавление
`site-packages` виртуального окружения в `sys.path` напрямую даёт тот же
результат и не зависит от версии virtualenv — благодаря `--system-site-packages`
на шаге 3 остальные системные пакеты и так видны интерпретатору.

Путь до venv в этом файле прописан абсолютно (`/home/<логин>/...`), а не
через `os.path.expanduser("~/...")` — процесс Apache/mod_wsgi, который
исполняет `site.wsgi`, может работать от другого системного пользователя,
чем аккаунт по SSH, и тогда `~` разворачивается не туда (или не туда, куда
вы ожидаете), venv не находится, а `from django.core.wsgi import
get_wsgi_application` падает с `ModuleNotFoundError: No module named
'django'` — при том что тот же файл, запущенный вручную по SSH
(`python3 site.wsgi`), отрабатывает без единой ошибки.

Путь собирается через `lib*` (а не просто `lib`), потому что на RHEL-подобных
системах (например, `/opt/rh/rh-python*`, как у Sprinthost) чистые
Python-пакеты (Django) ставятся в `lib/python3.X/site-packages`, а пакеты
с C-расширениями (`pysqlite3-binary`, `Pillow`) — отдельно, в
`lib64/python3.X/site-packages`. Если добавить в `sys.path` только `lib`,
Django импортируется нормально, но `pysqlite3-binary` останется
недоступен — падение будет не на `import django`, а позже, уже внутри
Django, с `NotSupportedError: deterministic=True requires SQLite 3.8.3 or
higher`, хотя пакет формально `pip install`-ом уже стоит.

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
