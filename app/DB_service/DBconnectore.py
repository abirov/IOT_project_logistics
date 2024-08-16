from http import client
from pymongo import MongoClient
import json
from bson import ObjectId
import geojson
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['IOT']



# Get all drivers

class DB_GET_Driver:


    def get_drivers():
        driver = db.driver.find()
        return driver

    def get_driver_by_id(id):
        driver = db.driver.find_one({"_id": ObjectId(id)})
        return driver

    def get_driver_by_name(name):
        driver = db.driver.find_one({"name": name})
        return driver  
    def get_driver_by_availability(availability):
        driver = db.driver.find_one({"availability": availability})
        return driver
    
    def get_driver_by_vehicle(vehicle_id):
        driver = db.driver.find_one({"vehicle_id": vehicle_id})
        return driver 
    def get_driver_by_location(latitude, longitude):
        location = {"latitude": latitude, "longitude": longitude}
        driver = db.driver.find_one({"location": location})
        return driver
    def get_driver_by_rating(avg_score):
        driver = db.driver.find_one({"rating": avg_score})
        return driver
    def get_driver_by_status(status):
        driver = db.driver.find_one({"status": status})
        return driver

class update_score:
    def update_rating(driver_id, rating):
        driver = db.driver.find_one({"_id": ObjectId(driver_id)})
        if driver:
            num_ratings = driver.get("num_ratings", 0)
            db.driver.update_one({"_id": ObjectId(driver_id)}, {"$push": {"ratings": rating}})
            num_ratings += 1
            return rating
        return None

    

class add_driver:
    def add_driver(driver):
        db.driver.insert_one(driver)
        return driver
    

class update_driver:
    def update_driver(driver_id, driver):
        db.driver.update_one({"_id": ObjectId(driver_id)}, {"$set": driver})
        return driver
    
class delete_driver:
    def delete_driver(driver_id):
        db.driver.delete_one({"_id": ObjectId(driver_id)})
        return driver_id
############################################################################################################
############################################################################################################
# Get all companies
    
class DB_GET_Company:
    def get_companies():
        company = db.company.find()
        return company

    def get_company_by_id(id):
        company = db.company.find_one({"_id": ObjectId(id)})
        return company
    
    def get_company_by_branch_id(id):
        company = db.company.find_one({"branch_id": ObjectId(id)})
        return company
    
    def get_company_by_name(name):
        company = db.company.find_one({"name": name})
        return company
    
    def get_company_by_branch_name(name):
        company = db.company.find_one({"name": name})
        return company
    
    def get_company_by_branch_address(address):
        company = db.company.find_one({"address": address})
        return company

class update_company:
    def update_company(company_id, company):
        db.company.update_one({"_id": ObjectId(company_id)}, {"$set": company})
        return company, company_id
    
class delete_company:
    def delete_company(company_id):
        db.company.delete_one({"_id": ObjectId(company_id)})
        return company_id
    
class add_company:
    def add_company(company):
        db.company.insert_one(company)
        return company

class get_branches:
    def get_branches(company_id):
        company = db.company.find_one({"_id": ObjectId(company_id)})
        if company:
            branches = company.get("branches", [])
            return branches    

class add_branch:
    def add_branch(company_id, branch):
        db.company.update_one({"_id": ObjectId(company_id)}, 
                              {"$push": {"branches": branch}})

class update_branch:
    def update_branch(company_id, branch_id, branch):
        db.company.update_one({"_id": ObjectId(company_id), "branches._id": ObjectId(branch_id)},
                               {"$set": branch})
        return branch, branch_id, company_id
    
class delete_branch:
    def delete_branch(company_id, branch_id):
        db.company.update_one({"_id": ObjectId(company_id)}, 
                              {"$pull": {"branches": {"_id": ObjectId(branch_id)}}})
        return branch_id, company_id
        
############################################################################################################
############################################################################################################

#get all vehicles in driver collection

class DB_GET_Vehicle:
    def get_vehicles_by_driver(driver_id):
        driver = db.driver.find_one({"_id": ObjectId(driver_id)})
        if driver:
            vehicles = driver.get("vehicles", [])
            return vehicles
        return None
    
    def get_vehicle_by_rating(avg_score):
        driver = db.driver.find_one({"rating": avg_score})
        if driver:
            vehicles = driver.get("vehicles", [])
            return vehicles
        return None
    
    def get_vehicle_by_status(status):
        driver = db.driver.find_one({"status": status})
        if driver:
            vehicles = driver.get("vehicles", [])
            return vehicles
        return None
    
class update_vehicle:
    def update_vehicle(driver_id, vehicle):
        db.driver.update_one({"_id": ObjectId(driver_id)},
                             {"$set": {"vehicle": vehicle}})
        return vehicle, driver_id
    
class delete_vehicle:
    def delete_vehicle(driver_id):
        db.driver.update_one({"_id": ObjectId(driver_id)}, 
                             {"$unset": {"vehicle": ""}})
        return driver_id




   


