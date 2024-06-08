from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client['logistics_db']
drivers_collection = db['drivers']
warehouses_collection = db['warehouses']

def update_driver_reputation(driver_id, feedback):
    driver = drivers_collection.find_one({'_id': ObjectId(driver_id)})
    if not driver:
        return

    # Example logic for calculating reputation score
    current_score = driver.get('reputation', 0)
    new_score = (current_score + feedback) / 2
    drivers_collection.update_one({'_id': ObjectId(driver_id)}, {'$set': {'reputation': new_score}})

def update_warehouse_reputation(warehouse_id, feedback):
    warehouse = warehouses_collection.find_one({'_id': ObjectId(warehouse_id)})
    if not warehouse:
        return

    # Example logic for calculating reputation score
    current_score = warehouse.get('reputation', 0)
    new_score = (current_score + feedback) / 2
    warehouses_collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': {'reputation': new_score}})
