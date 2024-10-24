from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from util import load_config  # Import the utility function

class Package:
    def __init__(self, config_file):
        config = load_config('package', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]


    def create(self, data,driver_id,warehouse_id):
        try:
            #add reference to driver and warehouse
            data['driver_id'] = ObjectId(driver_id)
            data['warehouse_id'] = ObjectId(warehouse_id)

            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except InvalidId:
            raise ValueError("Invalid ObjectId for driver or warehouse")
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")
                
        
