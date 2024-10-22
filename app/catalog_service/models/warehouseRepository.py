from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
import json
from util import load_config  # Import the utility function


class Warehouse:
    def __init__(self, config_file):
        config = load_config('warehouse', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting warehouse: {str(e)}")

    def get_by_id(self, warehouse_id):
        try:
            warehouse = self.collection.find_one({'_id': ObjectId(warehouse_id)})
            return self.json_encoder(warehouse) if warehouse else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error retrieving warehouse by ID: {str(e)}")

    def update(self, warehouse_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error updating warehouse: {str(e)}")

    def delete(self, warehouse_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(warehouse_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error deleting warehouse: {str(e)}")

    def list_all(self):
        try:
            warehouses = list(self.collection.find())
            return self.json_encoder(warehouses)
        except Exception as e:
            raise Exception(f"Error listing warehouses: {str(e)}")

    def update_reputation(self, warehouse_id, new_average):
        try:
            self.collection.update_one(
                {'_id': ObjectId(warehouse_id)},
                {'$set': {'reputation': new_average}}
            )
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error updating reputation: {str(e)}")

    @staticmethod
    def json_encoder(data):
        if isinstance(data, list):
            for doc in data:
                doc['_id'] = str(doc['_id'])
        elif data and '_id' in data:
            data['_id'] = str(data['_id'])
        return data
