from bson import ObjectId
from datetime import datetime

class Feedback:
    def __init__(self, package_id: str, score: int, comment: str, weight: int, _id: ObjectId = ObjectId(), warehouse_id: ObjectId = None, driver_id: ObjectId = None, timestamp: datetime = datetime.now()):
        self.package_id = package_id
        self.score = score
        self.comment = comment
        self._id = _id
        self.warehouse_id = warehouse_id
        self.driver_id = driver_id
        self.timestamp = timestamp
        self.weight = weight

    def __str__(self):
        return f"Feedback(package_id={self.package_id}, score={self.score}, comment={self.comment}, weight={self.weight}, _id={self._id}, warehouse_id={self.warehouse_id}, driver_id={self.driver_id}, timestamp={self.timestamp})"
    
    def to_dict(self):
        return {
            "_id": str(self._id),
            "package_id": str(self.package_id),
            "score": self.score,
            "comment": self.comment,
            "weight": self.weight,
            "warehouse_id": str(self.warehouse_id) if self.warehouse_id else None,
            "driver_id": str(self.driver_id) if self.driver_id else None,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data):
        return Feedback(
            package_id=ObjectId(data["package_id"]),
            score=data["score"],
            comment=data["comment"],
            weight=data["weight"],
            _id=ObjectId(data["_id"]),
            warehouse_id=ObjectId(data["warehouse_id"]) if data["warehouse_id"] else None,
            driver_id=ObjectId(data["driver_id"]) if data["driver_id"] else None,
            timestamp=data["timestamp"]
        )    
    