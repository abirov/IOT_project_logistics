from bson import ObjectId
import uuid

class Driver:

    def __init__(self, name: str, email: str, phone: str, address: str, license_number: str, car_model: str, _id=None, vehicle_id=None):
        self._id = _id if _id is not None else ObjectId()
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.license_number = license_number
        self.vehicle_id = vehicle_id if vehicle_id is not None else uuid.uuid4()
        self.car_model = car_model

    def __str__(self):
        return f"Driver(id: {self._id}, name: {self.name}, email: {self.email}, phone: {self.phone}, address: {self.address}, license_number: {self.license_number}, vehicle_id: {self.vehicle_id}, car_model: {self.car_model})"
    
    def to_dict(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "license_number": self.license_number,
            "vehicle_id": str(self.vehicle_id),
            "car_model": self.car_model
        }

    @staticmethod
    def from_dict(data):
        return Driver(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
            license_number=data["license_number"],
            car_model=data["car_model"],
            _id=ObjectId(data.get("_id")),
            vehicle_id=uuid.UUID(data.get("vehicle_id"))
        )
