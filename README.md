# Мини-CRM для заявок

CRM для сбора лидов: заявки из Telegram-бота, ручное добавление, теги и фильтр по тегу.

- CRM: https://mini-crm-leads-two.vercel.app (вход по общему паролю)
- Бот: [@mini_crm_coolbot](https://t.me/mini_crm_coolbot)

## Стек

Python 3.11+, FastAPI, Jinja2, PostgreSQL (Neon), хостинг Vercel, Telegram Bot API через webhook.

## Структура

| Путь | Назначение |
|---|---|
| `app/main.py` | Маршруты CRM и webhook |
| `app/auth.py` | Вход по паролю |
| `app/leads.py`, `app/tags.py` | Запросы к БД: лиды и теги |
| `app/dialog.py` | Диалог бота (чистая функция, без БД и сети) |
| `app/bot.py` | Обработка апдейта Telegram: сессия, лид, ответ |
| `app/schema.sql`, `app/init_db.py` | Схема БД и её создание |
| `app/set_webhook.py` | Регистрация webhook в Telegram |
| `app/templates/` | HTML-шаблоны |

## Переменные окружения

| Имя | Значение |
|---|---|
| `DATABASE_URL` | Строка подключения Neon (pooled, с `-pooler` в хосте) |
| `CRM_PASSWORD` | Общий пароль для входа в CRM |
| `SESSION_SECRET` | Случайная строка для подписи cookie, не короче 32 символов |
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather |
| `TELEGRAM_WEBHOOK_SECRET` | Случайная строка из латинских букв и цифр, Telegram передаёт её в заголовке каждого запроса |

Сгенерировать случайную строку:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## База данных

1. Создайте проект на [neon.tech](https://neon.tech) (бесплатный план).
2. В проекте нажмите **Connect**, выберите ветку `production`, включите **Connection pooling** и скопируйте строку подключения. Она нужна как `DATABASE_URL`.

## Telegram-бот

1. В Telegram откройте @BotFather, отправьте `/newbot`, задайте имя и username (оканчивается на `bot`).
2. Скопируйте выданный токен. Он нужен как `TELEGRAM_BOT_TOKEN`.

## Локальный запуск

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env` по таблице выше, затем создайте таблицы и запустите сервер:

```bash
python -m app.init_db
python -m uvicorn app.main:app --port 8000
```

CRM откроется на http://localhost:8000. Бот локально не получает сообщения: Telegram отправляет их только на публичный HTTPS-адрес, поэтому диалог проверяется на задеплоенной версии.

## Деплой на Vercel

1. Отправьте репозиторий на GitHub (`.env` в репозиторий не попадает).
2. На [vercel.com](https://vercel.com) выберите **Add New → Project** и импортируйте репозиторий. Vercel сам определит FastAPI по `app/main.py`, Build и Install Command оставьте пустыми.
3. В **Environment Variables** добавьте все пять переменных из таблицы выше.
4. Нажмите **Deploy**.
5. Откройте **Settings → Deployment Protection** и убедитесь, что **Vercel Authentication** выключена для production: иначе CRM и webhook будут недоступны без входа в Vercel.

После изменения переменных окружения нужен **Redeploy**.

## Регистрация webhook

После каждого деплоя на новый адрес (и один раз после первого) выполните локально, подставив production-адрес:

```bash
python -m app.set_webhook https://mini-crm-leads-two.vercel.app
```

Скрипт использует `TELEGRAM_BOT_TOKEN` и `TELEGRAM_WEBHOOK_SECRET` из `.env`, значение секрета должно совпадать с заданным в Vercel. В выводе `последняя ошибка: нет` означает, что Telegram достучался до приложения.

## Маршруты

| Метод и путь | Назначение |
|---|---|
| `GET /` | Список лидов, фильтр `?tag=<тег>` |
| `POST /leads` | Добавление лида вручную |
| `POST /leads/{id}/tags` | Добавление тега лиду |
| `POST /leads/{id}/tags/remove` | Снятие тега |
| `GET /login`, `POST /login` | Вход |
| `POST /webhook` | Приём апдейтов Telegram (проверяется секретный заголовок) |

Все маршруты, кроме `/login` и `/webhook`, требуют входа.
