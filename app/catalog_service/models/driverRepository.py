from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from .util import load_config  # Import the utility function

class Driver:
    def __init__(self, config_file):
        config = load_config('driver', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]


    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")

    def get_by_id(self, driver_id):
        try:
            driver = self.collection.find_one({'_id': ObjectId(driver_id)})
            return self.json_encoder(driver) if driver else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error retrieving driver by ID: {str(e)}")

    def get_by_name(self, driver_name):
        try:
            driver = self.collection.find_one({'name': driver_name})
            return self.json_encoder(driver) if driver else None
        except Exception as e:
            raise Exception(f"Error retrieving driver by name: {str(e)}")

    def update(self, driver_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(driver_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error updating driver: {str(e)}")

    def delete(self, driver_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(driver_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error deleting driver: {str(e)}")

    def list_all(self):
        try:
            drivers = list(self.collection.find())
            return self.json_encoder(drivers)
        except Exception as e:
            raise Exception(f"Error listing drivers: {str(e)}")

    def update_reputation(self, driver_id, new_average):
        try:
            self.collection.update_one(
                {'_id': ObjectId(driver_id)},
                {'$set': {'reputation': new_average}}
            )
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
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




    def get_by_package_id(self, package_id):
        return self.db.driver.aggregate([
            {
                '$lookup': {
                    'from': 'package',
                    'localField': '_id',
                    'foreignField': 'driver_id',
                    'as': 'packages'
                }
            },
            {
                '$match': {
                    'packages.package_id': package_id  # Match inside the joined 'packages' array
                }
            }
        ])
