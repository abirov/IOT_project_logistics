from bson import ObjectId

class Driver:
    def __init__(self, name: str, email: str, phone: str, address: str, license_number: str, _id: ObjectId = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.license_number = license_number
        self._id = _id
        

        

    def __str__(self):
        return f"Driver(name: {self.name}, email: {self.email}, phone: {self.phone}, address: {self.address}, license_number: {self.license_number})"
    
    def to_dict(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "license_number": self.license_number
        }
    @staticmethod
    def from_dict(data):
        return Driver(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
            license_number=data["license_number"],
            _id=ObjectId(data["_id"]) if data["_id"] else None
        )
    