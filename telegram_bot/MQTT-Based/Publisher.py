import json
import paho.mqtt.publish as publish
import pymongo

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["logistics_db"]
collection = db["Package"]

# MQTT Broker settings
MQTT_BROKER_URL = "localhost"
MQTT_TOPIC = "package/status"

def fetch_and_publish():
    packages = collection.find({})
    package_data = [
        {
            "driver_id": package["driver_id"],
            "source": package["source"],
            "destination": package["destination"],
            "status": package["status"]
        } for package in packages
    ]
    message = json.dumps(package_data)
    publish.single(MQTT_TOPIC, payload=message, hostname=MQTT_BROKER_URL)
    print(f"Published: {message} to topic: {MQTT_TOPIC}")

if __name__ == '__main__':
    fetch_and_publish()
