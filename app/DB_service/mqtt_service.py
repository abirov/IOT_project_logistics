import paho.mqtt.client as mqtt
import json
from DBconnectore3 import influxdbmanager
from paho.mqtt.client import CallbackAPIVersion
import os

class MQTTService:
    def __init__(self, config_file="configmqtt.json"):
        config = {} 
        path = os.path.join(os.path.dirname(__file__), config_file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)
        self.broker = config['broker']
        self.port = config['port']
        self.topic = config['topic']


        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)     
        self.influxdb = influxdbmanager(config_file = "configinfluxdb.json")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message


        

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with code:", rc)
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            vehicle_id = data['vehicle_id']
            latitude = data['latitude']
            longitude = data['longitude']
            timestamp = data['timestamp']

            # Write data to InfluxDB
            self.influxdb.write_data(
                measurement="LOCATION",
                tags={"vehicle_id": data["vehicle_id"]},
                fields={"latitude": data["latitude"], "longitude": data["longitude"]},
                time=data["timestamp"]
            )
            print(f"Data stored for vehicle: {vehicle_id}")
        except Exception as e:
            print("Error processing MQTT message:", e)

    def subscribe(self, topic):
        self.client.subscribe(topic, qos=2)
        self.topic = topic
        print(f"Subscribed to topic: {topic}")


    def run(self):
        self.client.loop_forever()


if __name__ == "__main__":
    service = MQTTService("configmqtt.json")
    service.run()
    
