from bson import ObjectId

class LogisticsPoint:
    def __init__(self, db):
        self.collection = db['logistics_points']

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def get(self, point_id):
        return self.collection.find_one({'_id': ObjectId(point_id)})

    def update(self, point_id, data):
        return self.collection.update_one({'_id': ObjectId(point_id)}, {'$set': data})

    def delete(self, point_id):
        return self.collection.delete_one({'_id': ObjectId(point_id)})

    def list(self):
        return list(self.collection.find())

