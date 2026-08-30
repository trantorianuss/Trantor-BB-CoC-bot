"""Simple Telegram connectivity test."""

from telegram import send_message


if __name__ == "__main__":
    send_message("Hola Mundo")
    print("Mensaje enviado a Telegram.")
