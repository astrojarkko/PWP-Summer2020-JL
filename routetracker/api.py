from flask import Blueprint
from flask_restful import Api

from routetracker.resources.user import UserCollection, UserItem
from routetracker.resources.route import RouteCollection, RouteItem
from routetracker.resources.location import LocationCollection, LocationItem
from routetracker.resources.discipline import DisciplineCollection, DisciplineItem
from routetracker.resources.grade import GradeCollection, GradeItem


"""
Adapted following the pwp-course-sensorhub-api-example api.py example
"""

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<user>/")
api.add_resource(RouteCollection, "/users/<user>/routes/")
api.add_resource(RouteItem, "/users/<user>/routes/<route>/")
api.add_resource(LocationCollection, "/users/<user>/routes/locations/")
api.add_resource(LocationItem, "/users/<user>/routes/locations/<location>/")
api.add_resource(DisciplineCollection, "/users/<user>/routes/disciplines/")
api.add_resource(DisciplineItem, "/users/<user>/routes/disciplines/<discipline>/")
api.add_resource(GradeCollection, "/users/<user>/routes/grades/")
api.add_resource(GradeItem, "/users/<user>/routes/grades/<grade>/")
