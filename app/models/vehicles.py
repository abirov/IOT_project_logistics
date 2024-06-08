from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client['logistics_db']
vehicles_collection = db['vehicles']

def create_vehicle(data):
    return vehicles_collection.insert_one(data)

def get_vehicle(vehicle_id):
    return vehicles_collection.find_one({'_id': ObjectId(vehicle_id)})

def update_vehicle(vehicle_id, data):
    return vehicles_collection.update_one({'_id': ObjectId(vehicle_id)}, {'$set': data})

def delete_vehicle(vehicle_id):
    return vehicles_collection.delete_one({'_id': ObjectId(vehicle_id)})

def list_vehicles():
    return list(vehicles_collection.find())

