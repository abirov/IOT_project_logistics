import paho.mqtt.client as mqtt
import json
from DBconnectore3 import influxdbmanager
from paho.mqtt.client import CallbackAPIVersion

class MQTTService:
    def __init__(self,ClientID, broker, port, topic, config_file): 
        self.port = port
        self.topic = topic
        self.clientID = ClientID #vehicle_id
        self.broker = broker
        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)     
        self.influxdb = influxdbmanager(config_file = "configinfluxdb.json")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)

        

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
                tags={"vehicle_id": vehicle_id},
                fields={"latitude": latitude, "longitude": longitude},
                time=timestamp
            )
            print(f"Data stored for vehicle: {vehicle_id}")
        except Exception as e:
            print("Error processing MQTT message:", e)
    def Subscribe(self, topic):

        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        print("subscribed to %s" % (topic))

    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)


    def run(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.broker, self.port, 60)
        client.loop_forever()

# if __name__ == "__main__":
#     mqtt_service = MQTTService(ClientID="vehicle_1", broker="test.mosquitto.org", port=1883, topic="vehicle/position", config_file="configinfluxdb.json")
#     mqtt_service.run()
    
