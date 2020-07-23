import json
from flask import Response, request, url_for
from routetracker.constants import *
from routetracker.models import *


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class RouteBuilder(MasonBuilder):
    """
    schemas and controls for all resources used by the API
    """

    @staticmethod
    def _user_schema():
        """
        user schema
        """
        schema = {
            "type": "object",
            "required": ["email"]
        }
        props = schema["properties"] = {}
        props["email"] = {
            "description": "users unique email address",
            "type": "string"
        }
        props["firstName"] = {
            "description": "users first name",
            "type": "string"
        }
        props["lastName"] = {
            "description": "users last name",
            "type": "string"
        }
        return schema

    @staticmethod
    def _route_schema():
        """
        route schema
        """
        schema = {
            "type": "object",
            "required": ["date", "location", "discipline", "grade"]
        }
        props = schema["properties"] = {}
        props["date"] = {
            "description": "date when the route was climbed",
            "type": "date"
        }
        props["lastName"] = {
            "location": "location where the route was climbed",
            "type": "string"
        }
        props["discipline"] = {
            "discipline": "discipline of the route",
            "type": "string"
        }
        props["grade"] = {
            "grade": "grade of the route",
            "type": "string"
        }
        return schema

    def add_control_all_users(self):
        """
        get a list of all users
        """
        self.add_control(
            "users:users-all",
            href=url_for("api.usercollection"),
            method="GET",
            title="Get list of all users"
            )

    def add_control_add_user(self):
        """
        add a new user
        """
        self.add_control(
            "users:add-user",
            href=url_for("api.usercollection"),
            method="POST",
            encoding="json",
            title="Add new user",
            schema=self._user_schema()
            )

    def add_control_edit_user(self, user):
        """
        edit user
        """
        self.add_control(
            "users:edit-user",
            href=url_for("api.useritem", user=user),
            method="PUT",
            encoding="json",
            title="Edit user",
            schema=self._user_schema()
            )

    def add_control_delete_user(self, user):
        """
        delete user
        """
        self.add_control(
            "users:delete",
            href=url_for("api.useritem", user=user),
            method="DELETE",
            title="Delete this user"
            )

    def add_control_climbed_by(self, user):
        """
        get information about user user
        """
        self.add_control(
            "users:climbed-by",
            href=url_for("api.useritem", user=user),
            method="GET",
            title="Get information about user"
            )

    def add_control_routes_all(self, user):
        """
        get routes climbed by user
        """
        self.add_control(
            "routes:routes-all",
            href=url_for("api.routecollection", user=user),
            method="GET",
            title="Get list of all routes climbed by user"
            )

    def add_control_add_route(self, user):
        """
        add a new route for user
        """
        self.add_control(
            "routes:add-route",
            href=url_for("api.routecollection", user=user),
            method="POST",
            encoding="json",
            title="Add new route",
            schema=self._route_schema()
            )

    def add_control_edit_route(self, user, route):
        """
        edit route
        """
        self.add_control(
            "routes:edit-route",
            href=url_for("api.routeitem", user=user, route=route),
            method="PUT",
            encoding="json",
            title="Edit route",
            schema=self._route_schema()
            )

    def add_control_delete_route(self, user, route):
        """
        delete route
        """
        self.add_control(
            "routes:delete",
            href=url_for("api.routeitem", user=user, route=route),
            method="DELETE",
            title="Delete route"
            )

    def add_control_locations_all(self, user):
        """
        get all locations where user has climbed a route
        """
        self.add_control(
            "locations:locations-all",
            href=url_for("api.locationcollection", user=user),
            method="GET",
            title="Get all locations for user"
            )

    def add_control_location_routes(self, user, location):
        """
        get all routes user has climbed in a location
        """
        self.add_control(
            "locations:in-location",
            href=url_for("api.locationitem", user=user, location=location),
            method="GET",
            title="Get routes in location for user"
            )

    def add_control_disciplines_all(self, user):
        """
        get all disciplines in which user has climbed a route
        """
        self.add_control(
            "disciplines:disciplines-all",
            href=url_for("api.disciplinecollection", user=user),
            method="GET",
            title="Get all locations for user"
            )

    def add_control_discipline_routes(self, user, discipline):
        """
        get all routes user has climbed in a discipline
        """
        self.add_control(
            "disciplines:in-discipline",
            href=url_for("api.disciplineitem", user=user, discipline=discipline),
            method="GET",
            title="Get routes in discipline for user"
            )

    def add_control_grades_all(self, user):
        """
        get all grades in which user has climbed a route
        """
        self.add_control(
            "grades:grades-all",
            href=url_for("api.gradecollection", user=user),
            method="GET",
            title="Get all grades for user"
            )

    def add_control_grade_routes(self, user, grade):
        """
        get all routes user has climbed in a grade
        """
        self.add_control(
            "grades:in-grade",
            href=url_for("api.gradeitem", user=user, grade=grade),
            method="GET",
            title="Get routes in grade for user"
            )


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href="")
    return Response(json.dumps(body), status_code, mimetype=MASON)
