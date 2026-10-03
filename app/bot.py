import logging
import os

import httpx

from app import dialog, leads, tags
from app.db import connect

BOT_TAG = "telegram-бот"
log = logging.getLogger(__name__)
# httpx на уровне INFO пишет в лог URL запроса, а в нём токен бота.
logging.getLogger("httpx").setLevel(logging.WARNING)


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
    httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=8).raise_for_status()


def process_update(update):
    message = update.get("message")
    if not message or message["chat"]["type"] != "private":
        return
    chat_id = message["chat"]["id"]
    username = (message.get("from") or {}).get("username")

    # Отметка об update_id, сессия и лид пишутся одной транзакцией: при сбое откатывается всё,
    # и повтор от Telegram обработается заново, а не будет принят за дубль.
    with connect() as conn:
        is_new = conn.execute(
            "INSERT INTO processed_updates (update_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (update["update_id"],),
        ).rowcount
        if not is_new:
            return
        session = conn.execute(
            "SELECT step, name, contact FROM bot_sessions WHERE tg_id = %s", (chat_id,)
        ).fetchone()
        new_session, reply, lead = dialog.handle(session, message.get("text"))
        if new_session is None:
            conn.execute("DELETE FROM bot_sessions WHERE tg_id = %s", (chat_id,))
        else:
            conn.execute(
                "INSERT INTO bot_sessions (tg_id, step, name, contact) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (tg_id) DO UPDATE SET step = EXCLUDED.step, name = EXCLUDED.name, "
                "contact = EXCLUDED.contact, updated_at = now()",
                (chat_id, new_session["step"], new_session["name"], new_session["contact"]),
            )
        if lead:
            lead_id = leads.create_lead(
                conn, lead["name"], lead["contact"], lead["request"], "bot", chat_id, username
            )
            tags.add_tag(conn, lead_id, BOT_TAG)

    # Сбой отправки не должен вызывать повтор webhook: лид уже сохранён.
    # Текст исключения httpx содержит URL с токеном бота, поэтому в лог идут только тип ошибки и код ответа.
    try:
        send_message(chat_id, reply)
    except httpx.HTTPError as exc:
        status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else "-"
        log.error("Не удалось отправить ответ в чат %s: %s, код %s", chat_id, type(exc).__name__, status)
