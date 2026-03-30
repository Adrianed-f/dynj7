# Развертывание на Nginx + Gunicorn (Ubuntu/Debian)


## 1) Установить системные зависимости

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib curl
```

## 2) Подготовить PostgreSQL

Пример (выполнять от пользователя `postgres`):

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE mydb;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

\c mydb
GRANT USAGE, CREATE ON SCHEMA public TO myuser;
ALTER SCHEMA public OWNER TO myuser;
```

В `config/settings.py` должны быть корректные параметры `DATABASES` (ENGINE = postgresql, NAME/USER/PASSWORD/HOST/PORT).

## 3) Склонировать проект и создать виртуальное окружение

```bash
cd /srv
sudo git clone <URL_РЕПОЗИТОРИЯ> app
sudo chown -R $USER:$USER /srv/app
cd /srv/app

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Установить Python-зависимости:

```bash
pip install -r requirements.txt
```

## 4) Подготовить Django (миграции, статика)

```bash
source /srv/app/venv/bin/activate
cd /srv/app

python manage.py migrate
```

Если нужна раздача статики через Nginx, добавьте в `config/settings.py`:

```python
STATIC_ROOT = BASE_DIR / "static"
```

и выполните:

```bash
python manage.py collectstatic --noinput
```

## 5) Проверить Gunicorn вручную

```bash
source /srv/app/venv/bin/activate
cd /srv/app
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Проверка:

```bash
curl -I http://127.0.0.1:8000/
```

Остановить: `Ctrl+C`.

## 6) systemd: сервис Gunicorn

Создать файл:

```bash
sudo nano /etc/systemd/system/app-gunicorn.service
```

Содержимое:

```ini
[Unit]
Description=Gunicorn for Django project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/app
Environment="DJANGO_SETTINGS_MODULE=config.settings"
ExecStart=/srv/app/venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 60
Restart=always

[Install]
WantedBy=multi-user.target
```

Права:

```bash
sudo chown -R www-data:www-data /srv/app
sudo systemctl daemon-reload
sudo systemctl enable --now app-gunicorn
sudo systemctl status app-gunicorn --no-pager
```

Логи:

```bash
sudo journalctl -u app-gunicorn -f
```

## 7) Nginx: конфиг сайта

Создать файл:

```bash
sudo nano /etc/nginx/sites-available/app
```

Пример конфига:

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 10m;

    location /static/ {
        alias /srv/app/static/;
        access_log off;
        expires 30d;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass http://127.0.0.1:8000;
    }
}
```

Включить сайт и проверить конфиг:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo nginx -t
sudo systemctl reload nginx
```

## 8) Проверка

Открыть в браузере:

- `/` — форма с динамическими инпутами
- после отправки будет редирект на `/result/<id>/`

CLI-проверка:

```bash
curl -I http://127.0.0.1/
curl -I http://127.0.0.1:8000/
```

## 9) Полезные команды

Перезапуск:

```bash
sudo systemctl restart app-gunicorn
sudo systemctl reload nginx
```

Статус:

```bash
sudo systemctl status app-gunicorn --no-pager
sudo systemctl status nginx --no-pager
```

