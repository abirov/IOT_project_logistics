from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['logistics_db']
logistics_points_collection = db['logistics_points']

def create_logistics_point(data):
    return logistics_points_collection.insert_one(data)

def get_logistics_point(point_id):
    return logistics_points_collection.find_one({'_id': ObjectId(point_id)})

def update_logistics_point(point_id, data):
    return logistics_points_collection.update_one({'_id': ObjectId(point_id)}, {'$set': data})

def delete_logistics_point(point_id):
    return logistics_points_collection.delete_one({'_id': ObjectId(point_id)})

def list_logistics_points():
    return list(logistics_points_collection.find())

