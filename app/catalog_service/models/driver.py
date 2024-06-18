from bson import ObjectId

class Driver:
    def __init__(self, db):
        self.collection = db['drivers']

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def get(self, driver_id):
        return self.collection.find_one({'_id': ObjectId(driver_id)})

    def update(self, driver_id, data):
        return self.collection.update_one({'_id': ObjectId(driver_id)}, {'$set': data})

    def delete(self, driver_id):
        return self.collection.delete_one({'_id': ObjectId(driver_id)})

    def list(self):
        return list(self.collection.find())

    def update_reputation(self, driver_id):
        feedbacks = list(self.collection.find({'driver_id': driver_id}))
        if feedbacks:
            total_score = sum(fb['score'] for fb in feedbacks)
            average_score = total_score / len(feedbacks)
            self.collection.update_one({'_id': ObjectId(driver_id)}, {'$set': {'reputation': average_score}})

