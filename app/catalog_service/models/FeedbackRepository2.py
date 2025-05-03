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
        feedback = Feedback(**data)
        feedback_dict = feedback.to_dict()
        result = self.collection.insert_one(feedback_dict)
        return str(result.inserted_id)
        
    def get_by_id(self, feedback_id):
        try:
            feedback = self.collection.find_one({'_id':(feedback_id)})
            return Feedback.from_dict(feedback) if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {feedback_id}")
        except Exception as e:
            raise Exception(f"Error retrieving feedback by ID: {str(e)}")
        
    def list_all(self):
        try:
            feedbacks = self.collection.find()
            return [Feedback.from_dict(feedback) for feedback in feedbacks]
        except Exception as e:
            raise Exception(f"Error listing feedback: {str(e)}")
   
    def get_by_rating(self, feedback_rating):
        try:
            feedback = self.collection.find_one({'rating': feedback_rating})    
            return Feedback.from_dict(feedback) if feedback else None
        except Exception as e:
            raise Exception(f"Error retrieving feedback by rating: {str(e)}")

    def get_by_driver_id(self, driver_id):
        try:
            feedback = self.collection.find({'driver_id':(driver_id)})
            return [Feedback.from_dict(feedback) for feedback in feedback] if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {driver_id}")
        except Exception as e:
            raise Exception(f"Error retrieving feedback by driver ID: {str(e)}")
        


    def get_by_package_ids(self, package_ids):
        """Retrieve feedbacks for multiple packages."""
        try:
            
            if isinstance(package_ids, str):
                package_ids_list = package_ids.split(",")  
            elif isinstance(package_ids, list):
                package_ids_list = package_ids  
            else:
                raise ValueError("Invalid package_ids format")

            query = {"package_id": {"$in": package_ids_list}}
            feedbacks = list(self.collection.find(query))
            return [Feedback.from_dict(feedback) for feedback in feedbacks]

        except Exception as e:
            raise Exception(f"Error retrieving feedbacks: {str(e)}")
            
        
            
    def get_by_warehouse_id(self, warehouse_id):
        try:
            feedback = self.collection.find_one({'warehouse_id':(warehouse_id)})
            return Feedback.from_dict(feedback) if feedback else None
        except InvalidId:
            raise ValueError(f"Invalid ObjectId: {warehouse_id}")
        except Exception as e:
            raise Exception(f"Error retrieving feedback by warehouse ID: {str(e)}")    
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
        
