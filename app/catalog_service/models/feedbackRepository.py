from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from .util import load_config  # Import the utility function

class Feedback:
    def __init__(self, config_file):
        config = load_config('feedback', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting feedback: {str(e)}")

    def get_by_object_id(self, object_id):
        try:
            feedback = list(self.collection.find({'object_id': ObjectId(object_id)}))
            return self.json_encoder(feedback) if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {object_id}")
        except Exception as e:
            raise Exception(f"Error retrieving feedback by object ID: {str(e)}")

    def get_score(self, feedback_id):
        try:
            feedback = self.collection.find_one({'_id': ObjectId(feedback_id)}, {'score': 1})
            return feedback['score'] if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error retrieving score by feedback ID: {str(e)}")

    def update(self, feedback_id, data):
        try:
            result = self.collection.update_one({'_id': ObjectId(feedback_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error updating feedback: {str(e)}")

    def delete(self, feedback_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(feedback_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error deleting feedback: {str(e)}")

    @staticmethod
    def json_encoder(data):
        if isinstance(data, list):
            for doc in data:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for each document
        elif data and '_id' in data:
            data['_id'] = str(data['_id'])  # Convert ObjectId to string for a single document
        return data
