from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from .util import load_config  # Import the utility function 
from .modelDRIVER import Driver

class DriverRepository:
    def __init__(self, config_file):
        config = load_config('driver', config_file)
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            driver = Driver(data['name'], data['email'], data['phone'], data['address'], data['license_number'], data['car_model'])
            result = self.collection.insert_one(driver.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")
        
    def get_by_id(self, driver_id):
        try:
            driver = self.collection.find_one({'_id':(driver_id)})
            return Driver.from_dict(driver) if driver else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error retrieving driver by ID: {str(e)}")
        
    def get_by_name(self, driver_name):
        try:
            driver = self.collection.find_one({'name': driver_name})    
            return Driver.from_dict(driver) if driver else None
        except Exception as e:
            raise Exception(f"Error retrieving driver by name: {str(e)}")
        
    def update(self, driver_id, data):
        try:
            result = self.collection.update_one({'_id': (driver_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error updating driver: {str(e)}")
        
    def delete(self, driver_id):
        try:
            result = self.collection.delete_one({'_id':(driver_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error deleting driver: {str(e)}")
        
    def list_all(self):
        try:
            drivers = list(self.collection.find())
            return [Driver.from_dict(driver) for driver in drivers]
        except Exception as e:
            raise Exception(f"Error listing drivers: {str(e)}")
    
    def get_driver_by_package_id(self, package_id):
        try:
            pipeline = [
                {"$match": {"_id": (package_id)}},  # Match the specific package by its _id
                {"$lookup": {
                    "from": "driver",       # Join with the drivers collection
                    "localField": "driver_id",  # Field in the package document to match
                    "foreignField": "_id",   # Field in the driver document to match
                    "as": "driver"           # Output the joined driver document as "driver"
                }},
                {"$unwind": "$driver"},       # Convert driver array to a single object
                {"$replaceRoot": {"newRoot": "$driver"}}  # Replace the root document with the driver document
            ]
            
            # Execute the aggregation query and return the result
            result = list(self.db.package.aggregate(pipeline))
            if result:
                return Driver.from_dict(result[0])
            else:
                return None
        except Exception as e:
            raise Exception(f"Error retrieving driver by package ID: {str(e)}")
        
