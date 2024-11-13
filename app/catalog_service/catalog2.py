import cherrypy
import json
from bson import objectid

from models.driverRepository2 import DriverRepository
from models.PackageRepository2 import PackageRepository
from models.warehouseRepository2 import WarehouseRepository
from models.FeedbackRepository2 import FeedbackRepository

# from models.LogisticsPointRepository import LogisticsPoint    #not modified yet
# from models.vehicleRepository import Vehicle                  #not modified yet


class driverServer:
