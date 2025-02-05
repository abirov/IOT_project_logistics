from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

client = MongoClient('localhost', 27017)
db = client['IOT']
collection = db['driver']
collection1  = db['feedback']
collection2 = db['warehouse']
collection3 = db['package']


    
# collection.insert_one({    
#     "name": "John Doe",
#     "email": "john@example.com",
#     "phone": "1234567890",
#     "address": "123 Main St",
#     "license_number": "XYZ123"
# })
# collection3.insert_one({
#     "name": "package1",
#     "weight": 10.0,
#     "dimensions": {
#         "length": 10,
#         "width": 10,
#         "height": 10
#     },
#     "warehouse_id": ObjectId("5f8f2a4f1c9d440000b2d2c7"),
#     "driver_id": None,
#     "status": "in warehouse",
#     "delivery_address": {
#         "street": "123 Elm St",
#         "city": "Springfield",
#         "state": "IL",
#         "zip": "62701"
#     }
# })
collection2.insert_one({
    "name": "warehouse1",
    "address": {
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701"
    },
    "phone": "1234567890",
    "email": "warhouse1@iot.com",
    "reputation": {
        "score": 5,
        "reviews": 10
    }
})