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
This file includes the classes for the Route model resources of the API
"""

class RouteCollection(Resource):
    """
    Route collection resource
    """

    def get(self, user):
        """
        Get all routes for user.
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
        body.add_namespace("routes", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.routecollection", user=user))
        body.add_control_routes_all(user)
        body.add_control_add_route(user)
        body.add_control_locations_all(user)
        body.add_control_disciplines_all(user)
        body.add_control_grades_all(user)
        body["items"] = []

        # use that to get the routes
        for db_route in Route.query.filter_by(user=db_user):
            item = RouteBuilder(
                        date=db_route.date.isoformat(),  # convert date to isoformat
                        location=db_route.location.name,
                        discipline=db_route.discipline.name,
                        grade=db_route.grade.name,
                        extraInfo=db_route.extraInfo
                        )
            item.add_control("self", url_for("api.routeitem", user=user, route=db_route.id))
            item.add_control_edit_route(user, db_route.id)
            item.add_control_delete_route(user, db_route.id)
            item.add_control_location_routes(user, db_route.location.id)
            item.add_control_discipline_routes(user, db_route.discipline.id)
            item.add_control_grade_routes(user, db_route.grade.id)
            item.add_control("profile", ROUTE_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)


    def post(self, user):
        """
        Add a new route
        """
        # check that the request is valid
        if not request.json:
            return create_error_response(
                        415, "Unsupported media type",
                        "Requests must be JSON"
                        )
        try:
            validate(request.json, Route.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))

        # check that user exists
        user_db = User.query.filter_by(id=user).first()
        if user_db is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        # test if date is in the right format: YYYY-MM-DD
        date_string = request.json["date"]
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            return create_error_response(400, "Wrong date format", "Date was not given in YYYY-MM-DD format.")

        # check if the location, discipline, or grade already exists, it it does
        # then use the already found one
        location = db.session.query(Location).filter_by(name=request.json["location"]).first()
        if not location:
            location = Location(name=request.json["location"])
        discipline = db.session.query(Discipline).filter_by(name=request.json["discipline"]).first()
        if not discipline:
            discipline = Discipline(name=request.json["discipline"])
        grade = db.session.query(Grade).filter_by(name=request.json["grade"]).first()
        if not grade:
            grade = Grade(name=request.json["grade"])

        # and test if extraInfo (optional) is given in the request and act accordingly
        if "extraInfo" in request.json:
            route = Route(
                        user=user_db,
                        date=date,
                        location=location,
                        discipline=discipline,
                        grade=grade,
                        extraInfo=request.json["extraInfo"]
                    )
        else:
            route = Route(
                        user=user_db,
                        date=date,
                        location=location,
                        discipline=discipline,
                        grade=grade
                    )

        # try to commit to db
        try:
            db.session.add(route)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                        401, "Access denied",
                        "You can not perform this action.")

        # get the ID of the just commited route
        route = route.id
        return Response(status=201, headers={"Location": url_for("api.routeitem", user=user, route=route)})


class RouteItem(Resource):
    """
    Route item resource
    """

    def get(self, user, route):
        """
        get information of specific route
        """
        # test that user with the route exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        # test if route exists for this user
        db_route = Route.query.filter(Route.user==db_user).filter(Route.id==route).first()
        if db_route is None:
            return create_error_response(
                        404, "Not found",
                        "No route was found with the id {}".format(route)
                        )

        # response body with proper controls
        body = RouteBuilder(
                    date=db_route.date.isoformat(),
                    location=db_route.location.name,
                    discipline=db_route.discipline.name,
                    grade=db_route.grade.name,
                    extraInfo=db_route.extraInfo
                    )
        body.add_namespace("routes", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.routeitem", user=user, route=route))
        body.add_control("profile", ROUTE_PROFILE)
        body.add_control_routes_all(user)
        body.add_control_climbed_by(user)
        body.add_control_edit_route(user, route)
        body.add_control_delete_route(user, route)
        body.add_control_location_routes(user, db_route.locationId)
        body.add_control_discipline_routes(user, db_route.disciplineId)
        body.add_control_grade_routes(user, db_route.gradeId)

        return Response(json.dumps(body), 200, mimetype=MASON)


    def put(self, user, route):
        """
        Edit route information
        """
        # test if user exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )
        # test if route exists for this user
        db_route = Route.query.filter(Route.user==db_user).filter(Route.id==route).first()
        if db_route is None:
            return create_error_response(
                        404, "Not found",
                        "No route was found with the id {}".format(route)
                        )
        if not request.json:
            return create_error_response(
                        415, "Unsupported media type",
                        "Requests must be JSON"
                        )
        try:
            validate(request.json, Route.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))

        # test if date is in the right format: YYYY-MM-DD
        date_string = request.json["date"]
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            return create_error_response(400, "Wrong date format", "Date was not given in YYYY-MM-DD format.")

        # check if the location, discipline, or grade already exists, it it does
        # then use the already found one
        location = db.session.query(Location).filter_by(name=request.json["location"]).first()
        if not location:
            location = Location(name=request.json["location"])
        discipline = db.session.query(Discipline).filter_by(name=request.json["discipline"]).first()
        if not discipline:
            discipline = Discipline(name=request.json["discipline"])
        grade = db.session.query(Grade).filter_by(name=request.json["grade"]).first()
        if not grade:
            grade = Grade(name=request.json["grade"])

        # and test if extraInfo (optional) is given in the request and act accordingly
        if "extraInfo" in request.json:
            db_route.user = db_user
            db_route.date = date
            db_route.location = location
            db_route.discipline = discipline
            db_route.grade = grade
            db_route.extraInfo = request.json["extraInfo"]
        else:
            db_route.user = db_user
            db_route.date = date
            db_route.location = location
            db_route.discipline = discipline
            db_route.grade = grade

        # try to commit to db
        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                        409, "Already exists",
                        "Route with id '{}' already exists.".format(route)
                        )
        return Response(status=204)

    def delete(self, user, route):
        """
        Delete route
        """
        # test if user exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        # test if route exists for this user
        db_route = Route.query.filter(Route.user==db_user).filter(Route.id==route).first()
        if db_route is None:
            return create_error_response(
                        404, "Not found",
                        "No route was found with the id {}".format(route)
                        )

        db.session.delete(db_route)
        db.session.commit()

        return Response(status=204)
