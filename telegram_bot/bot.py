import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog_service:8080")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Use /status to get the status of vehicles.')

def status(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{CATALOG_SERVICE_URL}/vehicles")
    vehicles = response.json()
    status_message = "\n".join([f"{v['name']}: {v['status']}" for v in vehicles])
    update.message.reply_text(status_message)

def main() -> None:
    updater = Updater(TELEGRAM_API_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("status", status))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

