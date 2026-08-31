"""Small Telegram helper for sending messages and status updates."""

import threading
import time

import requests

import botstate

import config
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


def send_status():
    """Read the current bot status and send it to Telegram."""

    from machine_state import get_state
    
    game_state = get_state()
    bot_status = botstate.get_status()

    message = (
        "❤️ Heartbeat\n"
        f"Bot 🤖: {bot_status}\n"
        f"Game 🎮: {game_state}"
    )

    send_message(message)


def _status_loop():
    """Send the bot status periodically while the application is running."""
    interval = config.TELEGRAM_STATUS_INTERVAL_MINUTES * 60

    while True:
        try:
            send_status()
        except Exception as e:
            print(f"Telegram status error: {e}")

        time.sleep(interval)


def start_status_thread():
    """Start the Telegram status thread when Telegram debugging is enabled."""
    if not config.DEBUG_TELEGRAM:
        return

    thread = threading.Thread(target=_status_loop, daemon=True)
    thread.start()
