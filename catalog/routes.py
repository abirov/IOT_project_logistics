from flask import jsonify, request
from flask_restful import Resource
from catalog import app, db
from catalog.models import User, LogisticsPoint, Vehicle

# Create resource classes for CRUD operations
class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.serialize())

    def post(self):
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'], age=data['age'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        user.name = data['name']
        user.email = data['email']
        user.age = data['age']
        db.session.commit()
        return jsonify(user.serialize())

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

# Add similar resource classes for LogisticsPoint and Vehicle

# Define API routes
app.add_url_rule('/users/<int:user_id>', view_func=UserResource.as_view('user_resource'))
app.add_url_rule('/users', view_func=UserResource.as_view('users_resource'))
# Add similar routes for LogisticsPoint and Vehicle
Run the Flask App:
In your main app.py or entry point file, import the catalog package and run the Flask app.
python
Copy code
# app.py

from catalog import app

if __name__ == '__main__':
    app.run(debug=True)
Initialize Database:
Run the following commands in your terminal to create and initialize the database:
bash
Copy code
# Navigate to your project directory
cd path/to/your/project

# Initialize the database (this will create catalog.db)
python
from catalog import db
db.create_all()
exit()
