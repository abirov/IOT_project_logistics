db = db.getSiblingDB('IOT');

db.driver.insertMany([
  {
    "_id": "675897aebdb7c9ebe2fa26ce",
    "name": "Jane Cristina",
    "email": "janeroe222@example.com",
    "phone": "9876543461",
    "address": "134 Pine Street",
    "license_number": "v2365678",
    "vehicle_id": "af91581d-a0b2-4b96-a67c-73b46383c14f",
    "car_model": "benz"
  },
  {
    "_id": "6758ad45327ada76ec9a215f",
    "name": "Davide Matti",
    "email": "Davidmatti88@gmail.com",
    "phone": "3517633659",
    "address": "Corso Racconigi, 188, Milano",
    "license_number": "Z56434",
    "vehicle_id": "09102cd8-c063-4af1-8269-3b29f137d975",
    "car_model": "Benz-w2"
  },
  {
    "_id": "67a9eebc4e9ba0d9cc6a0cc4",
    "name": "Antonio Verceli",
    "email": "antonio.v4@gmail.com",
    "phone": "3712368667",
    "address": "Via Frejus, 33, Torino",
    "license_number": "X23789",
    "vehicle_id": "01759d5f-2bb2-448e-b91d-fa5beefe9fd9",
    "car_model": "motor"
  },
  {
    "_id": "6817408045686f496d86080d",
    "name": "Mattias ILKOVIC",
    "email": "Mattias2000@yahoo.com",
    "phone": "09911377619",
    "address": "Torino, 10156",
    "license_number": "AL654890",
    "vehicle_id": "b4615184-2e1b-40be-aa07-9b1882a35955",
    "car_model": "Fiat-700"
  }

]);

db.feedback.insertMany([{
  "_id": "674b25c82ac95806b0c056b9",
  "package_id": "64a8f6e4b4a8c9d08a9f5e71",
  "score": 1,
  "comment": "Excellent service and timely delivery.",
  "weight": 10,
  "warehouse_id": "64a8f6e4b4a8c9d08a9f5e72",
  "driver_id": "674b225b3918bf50ebcc6a6f",
  "timestamp": "2024-11-30T12:34:56"
},
{
  "_id": "674b2b377c273017ce253ce7",
  "package_id": "64a8f6e4b4a5c9d08a9f5e72",
  "score": 5,
  "comment": "Excellent service.",
  "weight": 53,
  "warehouse_id": "63a8f6e4b4a8c9d08a9f5e74",
  "driver_id": "674b225b3918bf50ebcc6a6f",
  "timestamp": "2023-11-30T12:34:76"
}
]);

db.package.insertMany([
{
  "_id": "6819dde418ab1f1892341a67",
  "name": " Package 15",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "67a9eebc4e9ba0d9cc6a0cc4",
  "status": "in warehouse",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "681a1d4b0b751a0716907d18",
  "name": "yy",
  "weight": 5,
  "dimensions": {
    "length": 33,
    "width": 55,
    "height": 77
  },
  "warehouse_id": "68191b05b0421a4b00016004",
  "driver_id": "6817408045686f496d86080d",
  "status": "in-transit",
  "delivery_address": "torino"
}]);

db.warehouse.insertMany([{
  "_id": "67572ff6bc5f1e5d578fc487",
  "name": "Central Warehouse3",
  "address": {
    "street": "345 ABC St",
    "city": "Tehran",
    "state": "Tehran",
    "zip": "10134"
  },
  "phone": "987-111-2500",
  "email": "centralwarehouse2@example.com",
  "reputation": {
    "score": 0,
    "reviews": 0
  }
},
{
  "_id": "67bdb5fac86ffd92dba1c6ab",
  "name": "Central Warehouse5",
  "address": {
    "street": "Corso Abruzi,78",
    "city": "Torino",
    "state": "Torino",
    "zip": "10134"
  },
  "phone": "987-111-2569",
  "email": "centralwarehouse5@example.com",
  "reputation": {
    "score": 0,
    "reviews": 0
  }
},
{
  "_id": "681749f85febcc2278868721",
  "name": "Warehouse 7",
  "address": {
    "street": "Via Giovanni Paisiello,10",
    "city": "Torino",
    "state": "TO",
    "zip": "10154"
  },
  "phone": "3518354321",
  "email": "Warehouse7@gmail.com",
  "reputation": {
    "score": 0,
    "reviews": 0
  }
},
{
  "_id": "68191b05b0421a4b00016004",
  "name": "warehouse8",
  "address": {
    "street": "Corso Giacomo",
    "city": "Torino",
    "state": "TO",
    "zip": "10154"
  },
  "phone": "3245604420",
  "email": "warehouse8@gmail.com",
  "reputation": {
    "score": 0,
    "reviews": 0
  }
}]);