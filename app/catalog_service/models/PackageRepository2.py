from bson import ObjectId
from .util import load_config
from .modelPACKAGE import package
from pymongo import MongoClient
from bson.errors import InvalidId

class Package:
    def __init__(self, config_file):
        config = load_config('package', config_file)
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            status = data.get('status', 'in warehouse')
            package= package(data['name'], data['weight'], data['dimensions'], ObjectId(data['warehouse_id']), driver_id = None, status = status , delivery_address=data['delivery_address'])
            result = self.collection.insert_one(package.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")
        
    def get_by_id(self, package_id):
        try:
            package = self.collection.find_one({'_id': ObjectId(package_id)})
            return package.from_dict(package) if package else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error retrieving package by ID: {str(e)}")
        
    def get_by_warehouse_id(self, warehouse_id):
        try:
            package = self.collection.find_one({'warehouse_id': ObjectId(warehouse_id)})    
            return package.from_dict(package) if package else None
        except Exception as e:
            raise Exception(f"Error retrieving package by warehouse ID: {str(e)}")
        
    def update(self, package_id, data):
        try:
            # Convert driver_id to ObjectId if it exists in the data\
            if 'driver_id' in data:
                data['driver_id'] = ObjectId(data['driver_id'])
            
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
        
    def list_all_packages_without_driver(self):
        try:
            packages = list(self.collection.find({'driver_id': None}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages without driver: {str(e)}")
        
    def list_all(self):
        try:
            packages = list(self.collection.find())
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error listing packages: {str(e)}")
        
    def get_by_driver_id(self, driver_id):
        try:
            packages = list(self.collection.find({'driver_id': ObjectId(driver_id)}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by driver ID: {str(e)}")
        
    def get_by_warehouse_id(self, warehouse_id):
        try:
            packages = list(self.collection.find({'warehouse_id': ObjectId(warehouse_id)}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by warehouse ID: {str(e)}")
        
    def get_by_driver_id_and_status(self, driver_id, status):
        try:
            packages = list(self.collection.find({'driver_id': ObjectId(driver_id), 'status': status}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by driver ID and status: {str(e)}")
        
    def get_by_warehouse_id_and_status(self, warehouse_id, status):
        try:
            packages = list(self.collection.find({'warehouse_id': ObjectId(warehouse_id), 'status': status}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by warehouse ID and status: {str(e)}")
        
    def get_by_status(self, status):
        try:
            packages = list(self.collection.find({'status': status}))
            return [package.from_dict(package) for package in packages]
        except Exception as e:
            raise Exception(f"Error retrieving packages by status: {str(e)}")
        
    def update_status(self, package_id, status):
        try:
            result = self.collection.update_one({'_id': ObjectId(package_id)}, {'$set': {'status': status}})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error updating package status: {str(e)}")
        
    def assign_driver(self, package_id, driver_id):
        try:
            result = self.collection.update_one({'_id': ObjectId(package_id)}, {'$set': {'driver_id': ObjectId(driver_id), 'status': 'en route'}})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error assigning driver to package: {str(e)}")

    def mark_as_delivered(self, package_id):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(package_id)},
                {'$set': {'status': 'delivered'}}
            )
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {package_id}")
        except Exception as e:
            raise Exception(f"Error marking package as delivered: {str(e)}")