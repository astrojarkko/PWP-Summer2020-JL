import json
from datetime import datetime
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from routetracker.models import Route, User, Location, Discipline, Grade
from routetracker import db
from routetracker.utils import RouteBuilder, create_error_response
from routetracker.constants import *


"""
This file includes the classes for the Location model resources of the API
"""

class LocationCollection(Resource):
    """
    Location collection resource
    """

    def get(self, user):
        """
        Get all unique locations for user.
        """
        # find the approriate user with the id
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        # response body with proper controls
        body = RouteBuilder()
        body.add_namespace("locations", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationcollection", user=user))
        body.add_control_climbed_by(user)
        body.add_control_routes_all(user)
        body["items"] = []

        # get the locations, and only get unique values
        for db_route in Route.query.filter_by(user=db_user).group_by(Route.locationId):
            item = RouteBuilder(
                        location=db_route.location.name
                        )
            item.add_control("self", url_for("api.locationitem", user=user, location=db_route.locationId))
            item.add_control_location_routes(user, db_route.locationId)
            item.add_control("profile", ROUTE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

class LocationItem(Resource):
    """
    Location item resource
    """

    def get(self, user, location):
        """
        Get all routes for specific location for user.
        """
        # find the approriate user with the id
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )
        # test if grade is found for user
        db_location = Route.query.filter(Route.user==db_user).filter(Route.locationId==location).first()
        if db_location is None:
            return create_error_response(
                        404, "Not found",
                        "No location was found with the id {}".format(location)
                        )

        # response body with proper controls
        body = RouteBuilder()
        body.add_namespace("locations", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationitem", user=user, location=location))
        body.add_control_climbed_by(user)
        body.add_control_routes_all(user)
        body.add_control_locations_all(user)
        body["items"] = []

        # get the routes with proper location, and only get unique values
        for db_route in Route.query.filter(Route.user==db_user).filter(Route.locationId==location).all():
            item = RouteBuilder(
                        date=db_route.date.isoformat(),
                        location=db_route.location.name,
                        discipline=db_route.discipline.name,
                        grade=db_route.grade.name,
                        extraInfo=db_route.extraInfo
                        )
            item.add_control("self", url_for("api.routeitem", user=user, route=db_route.id))
            item.add_control_edit_route(user, db_route.id)
            item.add_control_delete_route(user, db_route.id)
            item.add_control_discipline_routes(user, db_route.disciplineId)
            item.add_control_grade_routes(user, db_route.gradeId)
            item.add_control("profile", ROUTE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)
