from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient


class Vehicle:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['IOT']
        self.collection = self.db['vehicle']

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting vehicle: {str(e)}")

    def get_by_id(self, vehicle_id):
        try:
            vehicle = self.collection.find_one({'_id': ObjectId(vehicle_id)})
            return self.json_encoder(vehicle) if vehicle else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {vehicle_id}")
        except Exception as e:
            raise Exception(f"Error retrieving vehicle by ID: {str(e)}")

    def update(self, vehicle_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(vehicle_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {vehicle_id}")
        except Exception as e:
            raise Exception(f"Error updating vehicle: {str(e)}")

    def delete(self, vehicle_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(vehicle_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {vehicle_id}")
        except Exception as e:
            raise Exception(f"Error deleting vehicle: {str(e)}")

    def list_all(self):
        try:
            vehicles = list(self.collection.find())
            return self.json_encoder(vehicles)
        except Exception as e:
            raise Exception(f"Error listing vehicles: {str(e)}")

    @staticmethod
    def json_encoder(data):
        if isinstance(data, list):
            for doc in data:
                doc['_id'] = str(doc['_id'])
        elif data and '_id' in data:
            data['_id'] = str(data['_id'])
        return data
