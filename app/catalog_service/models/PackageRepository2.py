from bson import ObjectId
from .util import load_config
from .modelPACKAGE import Package 
from pymongo import MongoClient
from bson.errors import InvalidId

class PackageRepository:
    def __init__(self, config_file):
        config = load_config('package', config_file)
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            status = data.get('status', 'in warehouse')
            package= Package(data['name'], data['weight'], data['dimensions'], ObjectId(data['warehouse_id']), driver_id = None, status = status , delivery_address=data['delivery_address'])
            result = self.collection.insert_one(package.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")
        
    def get_by_id(self, package_id):
        try:
            package = self.collection.find_one({'_id': (package_id)})
            return Package.from_dict(package) if package else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error retrieving package by ID: {str(e)}")
        
    def get_by_id_with_warehouse_address(self, package_id):
        try:
            pipeline = [
                {"$match": {"_id": ObjectId(package_id)}},
                {"$lookup": {
                    "from": "warehouses",
                    "localField": "warehouse_id",
                    "foreignField": "_id",
                    "as": "warehouse_info"
                }},
                {"$unwind": "$warehouse_info"},
                {"$project": {
                    "name": 1,
                    "weight": 1,
                    "dimensions": 1,
                    "status": 1,
                    "delivery_address": 1,
                    "warehouse_info.address": 1
                }}
            ]
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error retrieving package with warehouse address: {str(e)}")
        
    def get_by_warehouse_id(self, warehouse_id):
        try:
            package = self.collection.find_one({'warehouse_id':(warehouse_id)})    
            return Package.from_dict(package) if package else None
        except Exception as e:
            raise Exception(f"Error retrieving package by warehouse ID: {str(e)}")
        
    def update(self, package_id, data):
        try:
            # Convert driver_id to ObjectId if it exists in the data\
            if 'driver_id' in data:
                data['driver_id'] = (data['driver_id'])
            
            result = self.collection.update_one({'_id':(package_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error updating package: {str(e)}")
        
    def delete(self, package_id):
        try:
            result = self.collection.delete_one({'_id':(package_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error deleting package: {str(e)}")
        
    def list_all_packages_without_driver(self):
        try:
            packages = list(self.collection.find({'driver_id': None}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages without driver: {str(e)}")
        
    def list_all(self):
        try:
            packages = list(self.collection.find())
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error listing packages: {str(e)}")
        
    def get_by_driver_id(self, driver_id):
        try:
            packages = list(self.collection.find({'driver_id':(driver_id)}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by driver ID: {str(e)}")
        
    def get_by_warehouse_id(self, warehouse_id):
        try:
            packages = list(self.collection.find({'warehouse_id':(warehouse_id)}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by warehouse ID: {str(e)}")
        
    def get_by_driver_id_and_status(self, driver_id, status):
        try:
            packages = list(self.collection.find({'driver_id':(driver_id), 'status': status}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by driver ID and status: {str(e)}")
        
    def get_by_warehouse_id_and_status(self, warehouse_id, status):
        try:
            packages = list(self.collection.find({'warehouse_id':(warehouse_id), 'status': status}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by warehouse ID and status: {str(e)}")
        
    def get_by_status(self, status):
        try:
            packages = list(self.collection.find({'status': status}))
            return [Package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by status: {str(e)}")
        
    def update_status(self, package_id, status):
        try:
            result = self.collection.update_one({'_id':(package_id)}, {'$set': {'status': status}})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error updating package status: {str(e)}")
        
    def assign_driver(self, package_id, driver_id):
        try:
            result = self.collection.update_one({'_id': (package_id)}, {'$set': {'driver_id': ObjectId(driver_id), 'status': 'en route'}})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error assigning driver to package: {str(e)}")

    def mark_as_delivered(self, package_id):
        try:
            result = self.collection.update_one(
                {'_id': (package_id)},
                {'$set': {'status': 'delivered'}}
            )
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error marking package as delivered: {str(e)}")