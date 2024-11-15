from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from .util import load_config  # Import the utility function
from .modelFEEDBACK import Feedback  # Import the Feedback model
class FeedbackRepository:
    def __init__(self, config_file):
        config = load_config('feedback', config_file)  # Use the utility function to load the config
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['db']]
        self.collection = self.db[config['collection']]

    def create(self, data):
        try:
            Feedback = Feedback(data['package_id'], data['rating'], data['comment'], data['warehouse_id'], data['driver_id'])
            result = self.collection.insert_one(Feedback.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting feedback: {str(e)}")
        
    def get_by_id(self, feedback_id):
        try:
            feedback = self.collection.find_one({'_id':(feedback_id)})
            return Feedback.from_dict(feedback) if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error retrieving feedback by ID: {str(e)}")
        
    def get_by_rating(self, feedback_rating):
        try:
            feedback = self.collection.find_one({'rating': feedback_rating})    
            return Feedback.from_dict(feedback) if feedback else None
        except Exception as e:
            raise Exception(f"Error retrieving feedback by rating: {str(e)}")
        
    def update(self, feedback_id, data):
        try:
            result = self.collection.update_one({'_id':(feedback_id)}, {'$set': data})
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error updating feedback: {str(e)}")
        
    def delete(self, feedback_id):
        try:
            result = self.collection.delete_one({'_id':(feedback_id)})
            return {"deleted_count": result.deleted_count}
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error deleting feedback: {str(e)}")
        
