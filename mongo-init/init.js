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
  },
  {
    "_id": "68178d4f7efb71006df1d4b7",
    "name": "Antonio Seira",
    "email": "Antonio@teu.com",
    "phone": "0991137",
    "address": "Corso CITTA",
    "license_number": "Q565656",
    "vehicle_id": "2747de30-69a6-415a-9ad1-71487cc2111f",
    "car_model": "BENZ-7"
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
},
{
  "_id": "67572ff6bc5f1e5d578fc488",
  "package_id": "5f3f99e530c5b8cab93e8621",
  "score": 5,
  "comment": "Package was well-handled and arrived on time.",
  "weight": 1200,
  "warehouse_id": "5f3f99e530c5b8cab93e8623",
  "driver_id": "5f3f99e530c5b8cab93e8624",
  "timestamp": "2023-01-01T00:00:00Z"
},
{
  "_id": "675767f0909c223c7e9d0df0",
  "package_id": "5f3f99e530c5b8cab93e8622",
  "score": 3,
  "comment": "Package was well-handled and arrived on time.",
  "weight": 5200,
  "warehouse_id": "5f3f99e530c5b8chb93e8623",
  "driver_id": "5f3f99e530c5b8cab83e8624",
  "timestamp": "2023-01-01T00:00:00Z"
}
]);

db.package.insertMany([{
  "_id": "67bde95c4ebfd6fa7d427ea3",
  "name": " Package 42",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67572ff6bc5f1e5d578fc487",
  "driver_id": "6758ad45327ada76ec9a215f",
  "status": "in transit",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "67be03894caf6388d758055a",
  "name": " Package 2",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67572ff6bc5f1e5d578fc487",
  "driver_id": "675897aebdb7c9ebe2fa26ce",
  "status": "delivered",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "67c03339dcf2bfe433d57325",
  "name": " Package H687",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "67a9eebc4e9ba0d9cc6a0cc4",
  "status": "in transit",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "67c03352dcf2bfe433d57326",
  "name": " Package 7",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "6758ad45327ada76ec9a215f",
  "status": "delivered",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "68175d17774e7546a9654ee8",
  "name": " Package 87",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "6817408045686f496d86080d",
  "status": "delivered",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "68175d1f774e7546a9654ee9",
  "name": " Package 67",
  "weight": 5,
  "dimensions": {
    "length": 34,
    "width": 44,
    "height": 20
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "6817408045686f496d86080d",
  "status": "delivered",
  "delivery_address": {
    "city": "Milan",
    "street": "Corso Alfonso,34",
    "zipcode": "0598"
  }
},
{
  "_id": "68178e317efb71006df1d4be",
  "name": "Amazon2",
  "weight": 22,
  "dimensions": {
    "length": 22,
    "width": 22,
    "height": 33
  },
  "warehouse_id": "681749f85febcc2278868721",
  "driver_id": "68178d4f7efb71006df1d4b7",
  "status": "in-transit",
  "delivery_address": "CORSO"
},
{
  "_id": "681794b37dcd49dcd32b3cd6",
  "name": "sss",
  "weight": 22,
  "dimensions": {
    "length": 22,
    "width": 33,
    "height": 44
  },
  "warehouse_id": "681749f85febcc2278868721",
  "driver_id": "6817408045686f496d86080d",
  "status": "in-transit",
  "delivery_address": "dddd"
},
{
  "_id": "68192c928c73dcc52c486799",
  "name": "web1",
  "weight": 1111,
  "dimensions": {
    "length": 22,
    "width": 33,
    "height": 33
  },
  "warehouse_id": "67bdb5fac86ffd92dba1c6ab",
  "driver_id": "6817408045686f496d86080d",
  "status": "in-transit",
  "delivery_address": "torinlo"
},
{
  "_id": "68192e398c73dcc52c48679a",
  "name": "bot1",
  "weight": 2,
  "dimensions": {
    "length": 1,
    "width": 4,
    "height": 5
  },
  "warehouse_id": "68191b05b0421a4b00016004",
  "driver_id": "6817408045686f496d86080d",
  "status": "in-transit",
  "delivery_address": "ahivaz"
},
{
  "_id": "68192f358c73dcc52c48679b",
  "name": "bot2",
  "weight": 6,
  "dimensions": {
    "length": 2,
    "width": 4,
    "height": 5
  },
  "warehouse_id": "68191b05b0421a4b00016004",
  "driver_id": "6817408045686f496d86080d",
  "status": "delivered",
  "delivery_address": "tehran"
},
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