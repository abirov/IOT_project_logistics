from bson import ObjectId

class Feedback:
    def __init__(self, package_id: ObjectId, rating: int, comment: str, _id: ObjectId = None, warehouse_id: ObjectId = None, driver_id: ObjectId = None):
        self.package_id = package_id
        self.rating = rating
        self.comment = comment
        self._id = _id
        self.warehouse_id = warehouse_id
        self.driver_id = driver_id

    def __str__(self):
        return f"feedback(package_id: {self.package_id}, rating: {self.rating}, comment: {self.comment}, warehouse_id: {self.warehouse_id}, driver_id: {self.driver_id})"
    
    def to_dict(self):
        return {
            "_id": str(self._id) if self._id else None,
            "package_id": str(self.package_id),
            "rating": self.rating,
            "comment": self.comment,
            "warehouse_id": str(self.warehouse_id) if self.warehouse_id else None,
            "driver_id": str(self.driver_id) if self.driver_id else None
        }
    
    @staticmethod
    def from_dict(data):
        return feedback(
            package_id=ObjectId(data["package_id"]),
            rating=data["rating"],
            comment=data["comment"],
            warehouse_id=ObjectId(data["warehouse_id"]) if data["warehouse_id"] else None,
            driver_id=ObjectId(data["driver_id"]) if data["driver_id"] else None,
            _id=ObjectId(data["_id"]) if data["_id"] else None
        )
    
    