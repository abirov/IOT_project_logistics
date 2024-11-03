from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from .util import load_config  # Import the utility function

class LogisticsPoint:
    def __init__(self, config_file):
        config = load_config('logisticpoint', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting logistics point: {str(e)}")

    def get_by_id(self, point_id):
        try:
            point = self.collection.find_one({'_id': ObjectId(point_id)})
            return self.json_encoder(point) if point else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {point_id}")
        except Exception as e:
            raise Exception(f"Error retrieving logistics point by ID: {str(e)}")

    def get_by_name(self, point_name):
        try:
            point = self.collection.find_one({'name': point_name})
            return self.json_encoder(point) if point else None
        except Exception as e:
            raise Exception(f"Error retrieving logistics point by name: {str(e)}")

    def update(self, point_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(point_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {point_id}")
        except Exception as e:
            raise Exception(f"Error updating logistics point: {str(e)}")

    def delete(self, point_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(point_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {point_id}")
        except Exception as e:
            raise Exception(f"Error deleting logistics point: {str(e)}")

    def list_all(self):
        try:
            points = list(self.collection.find())
            return self.json_encoder(points)
        except Exception as e:
            raise Exception(f"Error listing logistics points: {str(e)}")

    @staticmethod
    def json_encoder(data):
        if isinstance(data, list):
            for doc in data:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for each document
        elif data and '_id' in data:
            data['_id'] = str(data['_id'])  # Convert ObjectId to string for a single document
        return data
