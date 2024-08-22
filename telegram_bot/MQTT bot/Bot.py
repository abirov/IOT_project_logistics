from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import paho.mqtt.client as mqtt
import os
import json

class VehicleStatusBot:
    def __init__(self, token, mqtt_host):
        self.token = token
        self.mqtt_host = mqtt_host
        self.vehicles_data = []
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        self.mqtt_client = self.setup_mqtt_client()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status))

    def setup_mqtt_client(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        return client

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text('Hello! Use /status to get the status of vehicles.')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.vehicles_data:
            status_message = "\n".join([f"{v['name']}: {v['status']}" for v in self.vehicles_data])
        else:
            status_message = "No vehicle data available."
        await update.message.reply_text(status_message)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("vehicle/status")

    def on_message(self, client, userdata, msg):
        self.vehicles_data = json.loads(msg.payload.decode())
        print("Data received via MQTT:", self.vehicles_data)

    def run(self):
        self.mqtt_client.connect(self.mqtt_host)
        self.mqtt_client.loop_start()
        self.application.run_polling()

if __name__ == '__main__':
    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN_MQTT")
    MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL_BOT")
    
    bot = VehicleStatusBot(TELEGRAM_API_TOKEN, MQTT_BROKER_URL)
    bot.run()
    
