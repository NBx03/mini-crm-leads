import os
import sys

import httpx
from dotenv import load_dotenv


def telegram(method, **payload):
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}"
    return httpx.post(url, json=payload, timeout=10).json()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Использование: python -m app.set_webhook https://ваш-проект.vercel.app")
    load_dotenv()
    base_url = sys.argv[1].rstrip("/")
    result = telegram(
        "setWebhook",
        url=f"{base_url}/webhook",
        secret_token=os.environ["TELEGRAM_WEBHOOK_SECRET"],
        allowed_updates=["message"],
        drop_pending_updates=True,
    )
    print("setWebhook:", result.get("description", result))
    info = telegram("getWebhookInfo").get("result", {})
    print("url:", info.get("url"))
    print("ожидают обработки:", info.get("pending_update_count"))
    print("последняя ошибка:", info.get("last_error_message", "нет"))
