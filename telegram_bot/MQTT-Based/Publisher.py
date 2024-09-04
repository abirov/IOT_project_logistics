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
            "package_id": str(package["_id"]),  
            "driver_id": package.get("driver_id"), 
            "source": package.get("source"),       
            "destination": package.get("destination"),  
            "status": package.get("status")         
        } for package in packages
    ]
    
    # Remove keys with None values
    cleaned_package_data = [
        {k: v for k, v in data.items() if v is not None}
        for data in package_data
    ]
    
    message = json.dumps(cleaned_package_data)
    publish.single(MQTT_TOPIC, payload=message, hostname=MQTT_BROKER_URL)
    print(f"Published: {message} to topic: {MQTT_TOPIC}")

if __name__ == '__main__':
    fetch_and_publish()
