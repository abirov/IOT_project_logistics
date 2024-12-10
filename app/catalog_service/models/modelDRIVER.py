from bson import ObjectId
import uuid

class Driver:

    def __init__(self, name: str, email: str, phone: str, address: str, license_number: str, _id: ObjectId= ObjectId(), vehicle_id:uuid.UUID = uuid.uuid4(), car_model: str):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.license_number = license_number
        self._id = _id
        self.vehicle_id = vehicle_id
        self.car_model = car_model

        

    def __str__(self):
        return f"Driver(id:{self._id} ,name: {self.name}, email: {self.email}, phone: {self.phone}, address: {self.address}, license_number: {self.license_number}, vehicle_id: {self.vehicle_id}, car_model: {self.car_model})"
    
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
            _id = data.get("_id"),
            vehicle_id = data.get("vehicle_id"),
            car_model=data["car_model"]

        )
    