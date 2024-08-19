import os
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import paho.mqtt.client as mqtt

class VehicleStatusBot:
    def __init__(self, token, mqtt_host):
        self.token = token
        self.mqtt_host = mqtt_host
        self.vehicles_data = []
        self.updater = Updater(token)
        self.setup_handlers()
        self.mqtt_client = self.setup_mqtt_client()

    def setup_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("status", self.status))

    def setup_mqtt_client(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        return client

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("vehicle/status")

    def on_message(self, client, userdata, msg):
        self.vehicles_data = json.loads(msg.payload.decode())
        print("Data received via MQTT:", self.vehicles_data)

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Hello! Use /status to get the status of vehicles.')

    def status(self, update: Update, context: CallbackContext) -> None:
        if self.vehicles_data:
            status_message = "\n".join([f"{v['name']}: {v['status']}" for v in self.vehicles_data])
        else:
            status_message = "No vehicle data available."
        update.message.reply_text(status_message)

    def run(self):
        self.mqtt_client.connect(self.mqtt_host)
        self.mqtt_client.loop_start()
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
    MQTT_BROKER_URL = "localhost"
    
    bot = VehicleStatusBot(TELEGRAM_API_TOKEN, MQTT_BROKER_URL)
    bot.run()
