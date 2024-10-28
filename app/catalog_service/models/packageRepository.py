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
        

    def update(self, package_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(package_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error updating package: {str(e)}")
        
    def delete(self, package_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(package_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error deleting package: {str(e)}")
        
    def list_all(self):
        try:
            packages = list(self.collection.find())
            return self.json_encoder(packages)
        except Exception as e:
            raise Exception(f"Error listing packages: {str(e)}")
        
                
        
    def get_by_id(self, package_id):
        try:
            package = self.collection.find_one({'_id': ObjectId(package_id)})
            return self.json_encoder(package) if package else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error retrieving package by ID: {str(e)}")
        
    def get_by_driver(self, driver_id):
        try:
            packages = list(self.collection.find({'driver_id': ObjectId(driver_id)}))
            return self.json_encoder(packages)
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error retrieving packages by driver ID: {str(e)}")
    
    def get_by_warehouse(self, warehouse_id):
        try:
            packages = list(self.collection.find({'warehouse_id': ObjectId(warehouse_id)}))
            return self.json_encoder(packages)
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error retrieving packages by warehouse ID: {str(e)}")
        
    @staticmethod
    def json_encoder(data):
        if isinstance(data, list):
            for doc in data:
                doc['_id'] = str(doc['_id'])
        elif data and '_id' in data:
            data['_id'] = str(data['_id'])
        return data
