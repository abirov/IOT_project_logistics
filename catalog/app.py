import cherrypy
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('mongodb://localhost:@@@@@/')
db = client.catalog.db
users = db.users
logistic_points = db.logistic_points
vehicles = db.vehicles

class CatalogApp:
  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def index(self):
    return {'message':'Initialization of Catalog API'}

  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def get_users(self):
    return dumps(list(users.find()))

  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def get_user(self,user_id):
    return dumps(users.find_one({'_id': user_id}))
   
  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def add_user(self,name,email,age):
    new_user = {'name': name, 'email': email, 'age':age}
    result = users.insert_one(new_user)
    return dumps(result.inserted_id)

  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def update_user(self,user_id,name,email,age):
    updated_user = {'name': name, 'email' : email, 'age' : age}
    result = users.update_one({'_id': user_id},{'$set': updated_user})
    return dumps(result.matched_count)
  @cherrypy.expose 
  @cherrypy.tools.json_out()
  def delete_user(self,user_id):
    result = users.delete_one({'_id':user_id})
    return dumps(result.deleted_count)

if __name__ == '__main__':
cherrypy.quickstart(CatalogApp())

