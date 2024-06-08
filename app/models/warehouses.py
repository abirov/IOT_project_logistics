from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client['logistics_db']
warehouses_collection = db['warehouses']

def create_warehouse(data):
    return warehouses_collection.insert_one(data)

def get_warehouse(warehouse_id):
    return warehouses_collection.find_one({'_id': ObjectId(warehouse_id)})

def update_warehouse(warehouse_id, data):
    return warehouses_collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': data})

def delete_warehouse(warehouse_id):
    return warehouses_collection.delete_one({'_id': ObjectId(warehouse_id)})

def list_warehouses():
    return list(warehouses_collection.find())

