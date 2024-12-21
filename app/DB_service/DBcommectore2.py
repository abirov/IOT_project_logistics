from bson import ObjectId
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Client
client = MongoClient('mongodb://localhost:27017/')
db = client['IOT']

class DBConnector:
    def __init__(self, collection_name):
        self.collection = db[collection_name]

    def get_all(self):
        try:
            return list(self.collection.find())
        except Exception as e:
            logger.error(f"Error fetching all documents: {e}")
            return None

    def get_by_id(self, id):
        try:
            return self.collection.find_one({"_id": ObjectId(id)})
        except Exception as e:
            logger.error(f"Error fetching document by ID: {e}")
            return None

    def insert(self, data):
        try:
            self.collection.insert_one(data)
            return data
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return None

    def update(self, id, data):
        try:
            self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
            return data
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return None

    def delete(self, id):
        try:
            self.collection.delete_one({"_id": ObjectId(id)})
            return id
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return None


class DriverService(DBConnector):
    def __init__(self):
        super().__init__('driver')

    def get_driver_by_name(self, name):
        try:
            return self.collection.find_one({"name": name})
        except Exception as e:
            logger.error(f"Error fetching driver by name: {e}")
            return None

    def get_driver_by_availability(self, availability):
        try:
            return self.collection.find({"availability": availability})
        except Exception as e:
            logger.error(f"Error fetching driver by availability: {e}")
            return None

    def update_rating(self, driver_id, rating, company_id):
        try:
            driver = self.get_by_id(driver_id)
            if driver:
                # Convert 'num_ratings' and 'rating' to int/float before performing operations
                num_ratings = int(driver.get("num_ratings", 0))
                current_rating = float(driver.get("rating", 0))

                # Calculate the new rating
                new_rating = (current_rating * num_ratings + rating) / (num_ratings + 1)
                
                # Update the driver document in MongoDB
                self.collection.update_one(
                    {"_id": ObjectId(driver_id)},
                    {"$push": {"ratings": {"company_id": company_id , "rating": rating}},
                    "$set": {"rating": new_rating, "num_ratings": num_ratings + 1}}
                )
                return new_rating
            return None
        except Exception as e:
            logger.error(f"Error updating driver rating: {e}")
            return None



class CompanyService(DBConnector):
    def __init__(self):
        super().__init__('company')

    def get_company_by_branch_id(self, branch_id):
        try:
            return self.collection.find_one({"branches._id": ObjectId(branch_id)})
        except Exception as e:
            logger.error(f"Error fetching company by branch ID: {e}")
            return None

    def get_branches(self, company_id):
        try:
            company = self.get_by_id(company_id)
            return company.get("branches", []) if company else None
        except Exception as e:
            logger.error(f"Error fetching branches: {e}")
            return None

    def add_branch(self, company_id, branch):
        try:
            self.collection.update_one({"_id": ObjectId(company_id)}, {"$push": {"branches": branch}})
        except Exception as e:
            logger.error(f"Error adding branch: {e}")

    def update_branch(self, company_id, branch_id, branch):
        try:
            self.collection.update_one({"_id": ObjectId(company_id), "branches._id": ObjectId(branch_id)},
                                       {"$set": branch})
            return branch
        except Exception as e:
            logger.error(f"Error updating branch: {e}")
            return None

    def delete_branch(self, company_id, branch_id):
        try:
            self.collection.update_one({"_id":ObjectId(company_id)},
                                       {"$pull": {"branches": {"_id":ObjectId(branch_id)}}})
            return branch_id
        except Exception as e:
            logger.error(f"Error deleting branch: {e}")
            return None


class VehicleService(DBConnector):
    def __init__(self):
        super().__init__('driver')

    def get_vehicles_by_driver(self, driver_id):
        try:
            driver = self.get_by_id(driver_id)
            return driver.get("vehicles", []) if driver else None
        except Exception as e:
            logger.error(f"Error fetching vehicles by driver: {e}")
            return None

    def update_vehicle(self, driver_id, vehicle):
        try:
            self.collection.update_one({"_id": ObjectId(driver_id)}, {"$set": {"vehicle": vehicle}})
            return vehicle
        except Exception as e:
            logger.error(f"Error updating vehicle: {e}")
            return None

    def delete_vehicle(self, driver_id):
        try:
            self.collection.update_one({"_id": ObjectId(driver_id)}, {"$unset": {"vehicle": ""}})
            return driver_id
        except Exception as e:
            logger.error(f"Error deleting vehicle: {e}")
            return None

# Example usage

if __name__ == "__main__":
    driver_service = DriverService()
    company_service = CompanyService()
    vehicle_service = VehicleService()
    
    # Replace with your actual company and branch ObjectId values
    result = company_service.delete_branch(ObjectId("66bf5dfb9f227cc7fc101131"),ObjectId("66bf5dfb9f227cc7fc10112a"))
    