# /app/simulations/vehicle_simulation.py
import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = 'mqtt_broker'
PORT = 1883
TOPIC = 'vehicles/status'

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)

def simulate_vehicle_updates(vehicle_id):
    statuses = ['In Transit', 'Delivered', 'Pending', 'Delayed']
    while True:
        status = random.choice(statuses)
        message = json.dumps({'vehicle_id': vehicle_id, 'status': status})
        client.publish(TOPIC, message)
        time.sleep(5)  # Simulate every 5 seconds

if __name__ == '__main__':
    vehicle_id = '60b85c5f3e8b9a4a988d4e3b'  # Example vehicle ID
    simulate_vehicle_updates(vehicle_id)
    client.loop_forever()
