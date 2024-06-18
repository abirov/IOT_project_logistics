from bson import ObjectId

class Vehicle:
    def __init__(self, db):
        self.collection = db['vehicles']

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def get(self, vehicle_id):
        return self.collection.find_one({'_id': ObjectId(vehicle_id)})

    def update(self, vehicle_id, data):
        return self.collection.update_one({'_id': ObjectId(vehicle_id)}, {'$set': data})

    def delete(self, vehicle_id):
        return self.collection.delete_one({'_id': ObjectId(vehicle_id)})

    def list(self):
        return list(self.collection.find())
