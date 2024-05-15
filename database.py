from http import client
from pymongo import MongoClient
import json
from bson import ObjectId
import geojson
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['IOT']


# Create collections
driver_collection = db['driver']
company_collection = db['company']
package_collection = db['package']


# JSON data for a driver
driver_collection_json= {
    "driver_id": ObjectId(),
    "name": "John Smith",
    "contact_details": {
        "email": "john.smith@example.com",
        "phone": "123-456-7890"
    },
    "license_number": "D1234567890",
    "vehicle": {
        "type": "Van",
        "registration_number": "XYZ 1234",
        "capacity": "3.5 tons"
    },
    "availability": "8am - 6pm",
    "location": {
        "latitude": 34.0522,
        "longitude": -118.2437
    }
}

company_collection_json= {
    "company_id": ObjectId(),
    "company_name": "Quick Ship Logistics",
    "contact_details": {
        "email": "contact@quickshiplogistics.com",
        "phone": "987-654-3210"
    },
    "branches": [
        {
            "branch_id": ObjectId(),
            "name": "Downtown Branch",
            "address": "456 Center St, Los Angeles, CA 90002",
            "contact_details": {
                "phone": "123-456-7891",
                "email": "downtown@quickshiplogistics.com"
            }
        },
        {
            "branch_id": ObjectId(),
            "name": "Uptown Branch",
            "address": "789 Up St, Los Angeles, CA 90003",
            "contact_details": {
                "phone": "123-456-7892",
                "email": "uptown@quickshiplogistics.com"
            }
        }
    ],
    "company_registration_number": "LC123456",
    "address": "123 Main Street, Los Angeles, CA 90001",
    "fleet_info": {
        "total_vehicles": 50,
        "vehicle_types": ["Van", "Truck"]
    },
}
package_collection_json= {
    "weight": "1.5 tons",
    "currentWarehouseId": ObjectId(),  # Renamed for clarity
    "destinationWarehouseId": ObjectId(),   #Renamed for clarity
    "status": "In Transit",
    "delivery_date": "2022-01-15-08:00:00",
    "driver_id": ObjectId(),  # Store the driver_id who delivered the package
    "company_id": ObjectId()  # Store the company_id who owns the package
}


# Inserting the JSON data into the collection
driver_collection.insert_one(driver_collection_json)
company_collection.insert_one(company_collection_json)
package_collection.insert_one(package_collection_json)


print("Driver and company and package profiles have been inserted into MongoDB")

   


