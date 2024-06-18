from bson import ObjectId

class Feedback:
    def __init__(self, db):
        self.collection = db['feedback']

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def get(self, feedback_id):
        return self.collection.find_one({'_id': ObjectId(feedback_id)})

    def list_for_driver(self, driver_id):
        return list(self.collection.find({'driver_id': driver_id}))

    def list_for_warehouse(self, warehouse_id):
        return list(self.collection.find({'warehouse_id': warehouse_id}))
