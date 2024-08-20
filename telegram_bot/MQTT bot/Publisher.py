import json
import paho.mqtt.publish as publish
import pymongo

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["vehicle_db"]
collection = db["vehicles"]

# MQTT Broker settings
MQTT_BROKER_URL = "localhost"
MQTT_TOPIC = "vehicle/status"

def fetch_and_publish():
    vehicles = collection.find({})
    vehicle_data = [{"name": vehicle["name"], "status": vehicle["status"]} for vehicle in vehicles]
    message = json.dumps(vehicle_data)
    publish.single(MQTT_TOPIC, payload=message, hostname=MQTT_BROKER_URL)
    print(f"Published: {message} to topic: {MQTT_TOPIC}")

if __name__ == '__main__':
    fetch_and_publish()