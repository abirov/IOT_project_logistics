import json
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
from DBconnectore3 import influxdbmanager

BROKER = "localhost"
PORT   = 1883
TOPIC  = "vehicle/position"
CFG    = "configinfluxdb.json"

class MQTTService:
    def __init__(self):
        self.client  = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)
        self.influx = influxdbmanager(config_file=CFG)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT, 60)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected (code", rc, ") — subscribing to", TOPIC)
        client.subscribe(TOPIC)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.influx.write_data(
                measurement="LOCATION",
                tags={"vehicle_id": data["vehicle_id"]},
                fields={"latitude": data["latitude"], "longitude": data["longitude"]},
                time=data["timestamp"]
            )
            print("✔ Stored:", data["vehicle_id"], data["timestamp"])
        except Exception as e:
            print("⚠️ Error:", e)

    def run(self):
        self.client.loop_forever()

if __name__ == "__main__":
    MQTTService().run()
