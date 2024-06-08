from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client['logistics_db']
drivers_collection = db['drivers']

def create_driver(data):
    return drivers_collection.insert_one(data)

def get_driver(driver_id):
    return drivers_collection.find_one({'_id': ObjectId(driver_id)})

def update_driver(driver_id, data):
    return drivers_collection.update_one({'_id': ObjectId(driver_id)}, {'$set': data})

def delete_driver(driver_id):
    return drivers_collection.delete_one({'_id': ObjectId(driver_id)})

def list_drivers():
    return list(drivers_collection.find())

