from bson import ObjectId

class package:
    def __init__(self, name: str, weight: float, dimensions: dict, warehouse_id: ObjectId, driver_id: ObjectId, status: str, _id: ObjectId = None, delivery_address: dict = None):
        self.name = name
        self.weight = weight
        self.dimensions = dimensions
        self.warehouse_id = warehouse_id
        self.driver_id = driver_id #can be None until assigned to a driver
        self._id = _id
        self.status = status #can be "in warehouse", "en route", "delivered"
        self.delivery_address = delivery_address #can be None until assigned to a driver

    def __str__(self):
        return f"package(name: {self.name}, weight: {self.weight}, dimensions: {self.dimensions}, warehouse_id: {self.warehouse_id}, driver_id: {self.driver_id}, status: {self.status}, delivery_address: {self.delivery_address})"

    def to_dict(self):
        return {
            "_id": str(self._id) if self._id else None,
            "name": self.name,
            "weight": self.weight,
            "dimensions": self.dimensions,
            "warehouse_id": str(self.warehouse_id),
            "driver_id": str(self.driver_id) if self.driver_id else None,
            "status": self.status,
            "delivery_address": self.delivery_address
        }
    @staticmethod
    def from_dict(data):
        return package(
            name=data["name"],
            weight=data["weight"],
            dimensions=data["dimensions"],
            warehouse_id=ObjectId(data["warehouse_id"]),
            driver_id=ObjectId(data["driver_id"]) if data["driver_id"] else None,
            status=data["status"],
            delivery_address=data["delivery_address"],
            _id=ObjectId(data["_id"]) if data["_id"] else None
        )