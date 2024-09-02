import os
import json
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import paho.mqtt.client as mqtt

class VehicleStatusBot:
    def __init__(self, token, mqtt_host):
        self.token = token
        self.mqtt_host = mqtt_host
        self.packages_data = []
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        self.mqtt_client = self.setup_mqtt_client()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("driver", self.ask_for_driver_id))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.filter_by_driver_id))

    def setup_mqtt_client(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        return client

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("package/status")

    def on_message(self, client, userdata, msg):
        print("Message received on topic:", msg.topic)
        print("Message payload:", msg.payload.decode())
        try:
            self.packages_data = json.loads(msg.payload.decode())
            print("Data received via MQTT:", self.packages_data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text('Hello! Use /status to get the status of packages or /driver to filter by driver ID.')

    async def status(self, update: Update, context: CallbackContext) -> None:
        if self.packages_data:
            status_message = "\n".join([f"Driver {p['driver_id']} - From {p['source']} to {p['destination']}: {p['status']}" for p in self.packages_data])
        else:
            status_message = "No package data available."
        await update.message.reply_text(status_message)

    async def ask_for_driver_id(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text('Please enter the driver ID to filter the data.')

    async def filter_by_driver_id(self, update: Update, context: CallbackContext) -> None:
        driver_id = update.message.text.strip()
        filtered_data = [p for p in self.packages_data if p['driver_id'] == driver_id]
        if filtered_data:
            status_message = "\n".join([f"Driver {p['driver_id']} - From {p['source']} to {p['destination']}: {p['status']}" for p in filtered_data])
        else:
            status_message = "No data available for driver ID: " + driver_id
        await update.message.reply_text(status_message, parse_mode=ParseMode.HTML)

    def run(self):
        self.mqtt_client.connect(self.mqtt_host)
        self.mqtt_client.loop_start()
        self.application.run_polling()

if __name__ == '__main__':
    TELEGRAM_API_TOKEN ="6998616059:AAFEB07QcjFw-twXCqdgm_NYNZBMXZRx9h4"
    MQTT_BROKER_URL = "localhost"
    
    bot = VehicleStatusBot(TELEGRAM_API_TOKEN, MQTT_BROKER_URL)
    bot.run()
