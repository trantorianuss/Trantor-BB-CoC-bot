"""Small Telegram helper for sending messages."""

import requests

import telegram_auth


def send_message(message):
    """Send a text message to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{telegram_auth.BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": telegram_auth.CHAT_ID,
            "text": message,
        },
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")

    return data
