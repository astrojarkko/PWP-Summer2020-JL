import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from routetracker.models import User
from routetracker import db
from routetracker.utils import RouteBuilder, create_error_response
from routetracker.constants import *

"""
This file includes the classes for the User model resources of the API
"""

class UserCollection(Resource):
    """
    The user collection resource: GET, POST
    """

    def get(self):
        """
        Get all users.
        """
        # response body with proper controls
        body = RouteBuilder()
        body.add_namespace("users", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.usercollection"))
        body.add_control_all_users()
        body.add_control_add_user()
        body["items"] = []
        # create list of all users
        for db_user in User.query.all():
            item = RouteBuilder(
                        email=db_user.email,
                        firstName=db_user.firstName,
                        lastName=db_user.lastName
                        )
            item.add_control("self", url_for("api.useritem", user=db_user.id))
            item.add_control("profile", USER_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """
        Add a new user
        """
        # check that the request is valid
        if not request.json:
            return create_error_response(
                        415, "Unsupported media type",
                        "Requests must be JSON"
                        )
        # check that the request is correct against the schema
        try:
            validate(request.json, User.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))

        # test if firstname and lastname given, these are optional parameters
        # both need to exist in order to read either
        if "firstName" in request.json and "lastName" in request.json:
            user = User(
                    email=request.json["email"],
                    firstName=request.json["firstName"],
                    lastName=request.json["lastName"]
                    )
        else:
            user = User(email=request.json["email"])

        # try to commit to db
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                        409, "Already exists",
                        "User with email '{}' already exists.".format(request.json["email"])
                        )

        return Response(status=201, headers={"Location": url_for("api.useritem", user=user.id)})


class UserItem(Resource):
    """
    The user item resource: GET, PUT, DELETE
    """

    def get(self, user):
        """
        Get information of specific user
        """
        # test if user exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        # build response body
        body = RouteBuilder(
                    email=db_user.email,
                    firstName=db_user.firstName,
                    lastName=db_user.lastName
                    )
        body.add_namespace("users", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.useritem", user=user))
        body.add_control("profile", USER_PROFILE)
        body.add_control_climbed_by(user)
        body.add_control_all_users()
        body.add_control_edit_user(user)
        body.add_control_edit_user(user)
        body.add_control_delete_user(user)
        body.add_control_routes_all(user)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user):
        """
        Edit user information
        """
        # test if user exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )
        if not request.json:
            return create_error_response(
                        415, "Unsupported media type",
                        "Requests must be JSON"
                        )
        try:
            validate(request.json, User.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))

        # test if firstname and lastname given, these are optional parameters
        # both need to exist in order to read either
        if "firstName" in request.json and "lastName" in request.json:
            db_user.email=request.json["email"]
            db_user.firstName=request.json["firstName"]
            db_user.lastName=request.json["lastName"]
        else:
            db_user.email=request.json["email"]

        # try to commit to db
        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                        409, "Already exists",
                        "User with email '{}' already exists.".format(request.json["email"])
                        )
        return Response(status=204)

    def delete(self, user):
        """
        Delete user
        """
        # test if user exists
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                        404, "Not found",
                        "No user was found with the id {}".format(user)
                        )

        db.session.delete(db_user)
        db.session.commit()

        return Response(status=204)
