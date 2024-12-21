from bson import ObjectId

class Warehouse:
    def __init__(self, name: str, address: dict , _id: ObjectId =ObjectId() , phone: str = None, email: str = None, reputation: dict = None):
        self.name = name
        self.address = address #ddress = {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"}
        self._id = _id
        self.phone = phone
        self.email = email
        self.reputation = reputation if reputation else {"score": 0, "reviews": 0}

    def __str__(self):
        return f"Warehouse(name: {self.name}, address: {self.address}, phone: {self.phone}, email: {self.email}, reputation: {self.reputation})"
    
    def to_dict(self):
        return {
            "_id": str(self._id) if self._id else None,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "reputation": self.reputation
        }
    @staticmethod   
    def from_dict(data):
        return Warehouse(
            name=data["name"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            reputation=data["reputation"],
            _id=ObjectId(data["_id"]) if data["_id"] else None
        )
    