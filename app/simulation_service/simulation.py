import paho.mqtt.client as mqtt
import time
import random
import json
import signal
import sys

class VehicleSimulation:
    def __init__(self, broker_url, port, topic):
        self.broker_url = broker_url
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        signal.signal(signal.SIGINT, self.handle_exit)  # Handle Ctrl+C

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with result code {rc}")

    def simulate_vehicle_updates(self, vehicle_id):
        try:
            self.client.connect(self.broker_url, self.port, 60)
            self.client.loop_start()
            statuses = ['In Transit', 'Delivered', 'Pending', 'Delayed']
            while True:
                status = random.choice(statuses)
                message = json.dumps({'vehicle_id': vehicle_id, 'status': status})
                self.client.publish(self.topic, message)
                print(f"Published: {message}")
                time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def handle_exit(self, sig, frame):
        print("Exiting gracefully...")
        self.client.loop_stop()
        self.client.disconnect()
        sys.exit(0)

if __name__ == '__main__':
    broker_url = 'localhost'
    port = 1883
    topic = 'vehicles/status'
    vehicle_id = '60b85c5f3e8b9a4a988d4e3b'
    simulation = VehicleSimulation(broker_url, port, topic)
    simulation.simulate_vehicle_updates(vehicle_id)
