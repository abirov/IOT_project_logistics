from bson import ObjectId

class Warehouse:
    def __init__(self, db):
        self.collection = db['warehouses']

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def get(self, warehouse_id):
        return self.collection.find_one({'_id': ObjectId(warehouse_id)})

    def update(self, warehouse_id, data):
        return self.collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': data})

    def delete(self, warehouse_id):
        return self.collection.delete_one({'_id': ObjectId(warehouse_id)})

    def list(self):
        return list(self.collection.find())

    def update_reputation(self, warehouse_id):
        feedbacks = list(self.collection.find({'warehouse_id': warehouse_id}))
        if feedbacks:
            total_score = sum(fb['score'] for fb in feedbacks)
            average_score = total_score / len(feedbacks)
            self.collection.update_one({'_id': ObjectId(warehouse_id)}, {'$set': {'reputation': average_score}})

