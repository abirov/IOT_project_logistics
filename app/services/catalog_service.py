# /app/services/catalog_service.py
import cherrypy
import json
from bson import ObjectId
from pymongo import MongoClient
import paho.mqtt.client as mqtt

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

client = MongoClient('mongodb', 27017)
db = client['logistics_db']
logistics_points_collection = db['logistics_points']
vehicles_collection = db['vehicles']
drivers_collection = db['drivers']
warehouses_collection = db['warehouses']

BROKER = 'mqtt_broker'
PORT = 1883
TOPIC = 'vehicles/status'

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode())
    vehicle_id = message['vehicle_id']
    status = message['status']
    vehicles_collection.update_one({'_id': ObjectId(vehicle_id)}, {'$set': {'status': status}})
    print(f"Updated vehicle {vehicle_id} with status {status}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

class CatalogService:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def logistics_points(self, point_id=None):
        if cherrypy.request.method == 'GET':
            if point_id:
                point = logistics_points_collection.find_one({'_id': ObjectId(point_id)})
                return JSONEncoder().encode(point)
            else:
                points = list(logistics_points_collection.find())
                return JSONEncoder().encode(points)
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            logistics_points_collection.insert_one(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            logistics_points_collection.update_one({'_id': ObjectId(point_id)}, {'$set': data})
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            logistics_points_collection.delete_one({'_id': ObjectId(point_id)})
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vehicles(self, vehicle_id=None):
        if cherrypy.request.method == 'GET':
            if vehicle_id:
                vehicle = vehicles_collection.find_one({'_id': ObjectId(vehicle_id)})
                return JSONEncoder().encode(vehicle)
            else:
                vehicles = list(vehicles_collection.find())
                return JSONEncoder().encode(vehicles)
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            vehicles_collection.insert_one(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            vehicles_collection.update_one({'_id': ObjectId(vehicle_id)}, {'$set': data})
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            vehicles_collection.delete_one({'_id': ObjectId(vehicle_id)})
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def drivers(self, driver_id=None):
        if cherrypy.request.method == 'GET':
            if driver_id:
                driver = drivers_collection.find_one({'_id': ObjectId(driver_id)})
                return JSONEncoder().encode(driver)
            else:
                drivers = list(drivers_collection.find())
                return JSONEncoder().encode(drivers)
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            drivers_collection.insert_one(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            drivers_collection.update_one({'_id': ObjectId(driver_id)}, {'$set': data})
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            drivers_collection.delete_one({'_id': ObjectId(driver_id)})
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def warehouses(self, warehouse_id=None):
        if cherrypy.request.method == 'GET':
            if warehouse_id:
                warehouse = warehouses_collection.find_one({'_id': ObjectId(warehouse_id)})
                return JSONEncoder().encode(warehouse)
            else:
                warehouses = list(warehouses_collection.find())
                return JSONEncoder().encode(warehouses)
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            warehouses_collection.insert_one(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            warehouses_collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': data})
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            warehouses_collection.delete_one({'_id': ObjectId(warehouse_id)})
            return {'status': 'success'}

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.tree.mount(CatalogService(), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
