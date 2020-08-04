import json
import os
import pytest
import tempfile
import time
import random
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from routetracker import create_app, db
from routetracker.models import User, Route, Location, Discipline, Grade


"""
API unit testing, adopted following the resource_test.py example given in:
pwp-course-sensorhub-api-example
"""


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    """
    copied directly from the course material
    """
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    """
    Populate the test database
    """

    # define pre-described climbing disciplines, grades, and locations
    disciplines = ["Bouldering", "Bouldering", "Toprope", "Lead", "Toprope"]
    grades = ["6A", "6A+", "6A+", "6B", "6B"]
    locations = ["Oulun Kiipeilykeskus", "Oulun Kiipeilykeskus", "Magic Woods", "Random", "Boulder"]

    for i in range(1, 3):
        user = User(email="{}email@url.com".format(i),
                    firstName="First{}".format(i),
                    lastName="Last{}".format(i))
        db.session.add(user)
        db.session.commit()

        # for each add three routes climbed, the locations, disciplines,
        # and grades are taken from the above lists
        for j in range(0, 5):

            # check if the location, discipline, or grade already exists, it
            # it does then use the already found one
            location = db.session.query(Location).filter_by(name=locations[j]).first()
            if not location:
                location = Location(name=locations[j])

            discipline = db.session.query(Discipline).filter_by(name=disciplines[j]).first()
            if not discipline:
                discipline = Discipline(name=disciplines[j])

            grade = db.session.query(Grade).filter_by(name=grades[j]).first()
            if not grade:
                grade = Grade(name=grades[j])

            route = Route(user=user,
                          date=datetime.today(),
                          location=location,
                          discipline=discipline,
                          grade=grade,
                          extraInfo="this is {}, {}".format(i, j)
                          )
            # add and commit changes
            db.session.add(route)
            db.session.commit()


def _user_template(user=1):
    """
    create valid JSON for user for POST, PUT tests
    """
    return {"email": "{}-unit@test.com".format(user),
            "firstName": "test",
            "lastName": "testington"}


def _route_template(route=1):
    """
    create valid JSON for route for POST, PUT tests
    """
    return {"date": "2030-12-31",
            "location": "Olympics",
            "discipline": "Speed climbing",
            "grade": "9a",
            "extraInfo": "{} this is the extra information".format(route)}


def _check_namespace(client, response, namespace):
    """
    Checks that the "users" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.

    MODIFIED FROM THE EXAMPLE GIVEN: added key to identify what namespace
    """

    ns_href = response["@namespaces"][namespace]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the controls method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj, collection):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.

    MODIFIED FROM GIVEN EXAMPLE CODE: added key to identify what collection
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"

    # two schemas in use, assign correct one
    if collection == "users":
        body = _user_template()
    elif collection == "routes":
        body = _route_template()

    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


def _check_control_put_method(ctrl, client, obj, collection):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.

    MODIFIED FROM GIVEN EXAMPLE CODE: added key to identify what collection
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"

    # two schemas in use, assign correct one
    if collection == "users":
        body = _user_template()
        body["email"] = obj["email"]
    elif collection == "routes":
        body = _route_template()
        body["date"] = obj["date"]
        body["location"] = obj["location"]
        body["discipline"] = obj["discipline"]
        body["grade"] = obj["grade"]
        body["extraInfo"] = obj["extraInfo"]

    validate(body, schema)
    print(href)
    print(body)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


class TestUserCollection(object):
    """
    Test the user collection resource: GET, POST
    """

    RESOURCE_URL = "/api/users/"

    def test_get(self, app):
        """
        test get method to return the user lists
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 2  # two users created above
        _check_namespace(app, body, "users")
        _check_control_get_method("self", app, body)
        _check_control_get_method("users:users-all", app, body)
        _check_control_post_method("users:add-user", app, body, "users")
        # each item should have email, firstName, and lastName
        for item in body["items"]:
            assert "email" in item
            assert "firstName" in item
            assert "lastName" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("profile", app, item)

    def test_post_valid_request(self, app):
        """
        Tests post method to create a new user
        """
        # test that we can create a new user
        valid = _user_template()
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        # we created third user, and see that the returned URL is correct
        assert resp.headers["Location"].endswith(self.RESOURCE_URL+'3/')

        # now get the new user and validate data
        resp = app.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["email"] == "1-unit@test.com"
        assert body["firstName"] == "test"
        assert body["lastName"] == "testington"

        # send same data again, email have to be unique so we should get 409
        valid = _user_template()
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # email is required, we should get 400 back without it
        valid.pop("email")
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # email can not be empty string either
        valid = _user_template()
        valid["email"] = ""
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # remove firstName and lastName to see that also just minimum is OK
        valid = _user_template()
        valid["email"] = "newone"
        valid.pop("firstName")
        valid.pop("lastName")
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        # we created third user, and see that the returned URL is correct
        assert resp.headers["Location"].endswith(self.RESOURCE_URL+'4/')

        # now get the new user and validate data
        resp = app.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["email"] == "newone"

        # test post response to invalid request
        valid = _user_template()
        resp = app.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415


class TestUserItem(object):
    """
    Test the user item resource: GET, PUT, DELETE
    """

    RESOURCE_URL = "/api/users/1/"
    INVALID_URL = "/api/users/saddsa/"

    def test_get(self, app):
        """
        test get method to return the information of the first user
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # check content
        _check_namespace(app, body, "users")
        assert body["email"] == "1email@url.com"
        assert body["firstName"] == "First1"
        assert body["lastName"] == "Last1"
        _check_control_get_method("self", app, body)
        _check_control_get_method("profile", app, body)
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("users:users-all", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_put_method("users:edit-user", app, body, "users")
        _check_control_delete_method("users:delete", app, body)

        # and see also that we get 404 if we try to access invalid url
        resp = app.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put_valid_request(self, app):
        """
        Tests put method to edit information of an user
        """
        # test that we can create a new user
        valid = _user_template()

        # wrong Content
        resp = app.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # for user not found
        resp = app.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # with wrong email that already exists
        valid["email"] = "2email@url.com"
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # change only firstName
        valid["email"] = "1-unit@test.com"
        valid["firstName"] = "changed"
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # change only email
        valid.pop("firstName")
        valid.pop("lastName")
        valid["email"] = "test"
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove email to see that it is not accepted
        valid = _user_template()
        valid.pop("email")
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # email can not be empty string either
        valid = _user_template()
        valid["email"] = ""
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    def test_delete(self, app):
        """
        test delete method
        """
        # delete user
        resp = app.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        # can not delete it second time
        resp = app.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        # can not delete user that does not exist
        resp = app.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestRouteCollection(object):
    """
    Test the route collection resource: GET, POST
    """

    RESOURCE_URL = "/api/users/1/routes/"
    INVALID_URL = "/api/users/saddsa/routes/"

    def test_get(self, app):
        """
        test get method to return the routes lists for user
        """
        # for user not found
        resp = app.get(self.INVALID_URL)
        assert resp.status_code == 404

        # test the content
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 5  # number of routes created above
        _check_namespace(app, body, "routes")
        _check_control_get_method("self", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_get_method("locations:locations-all", app, body)
        _check_control_get_method("disciplines:disciplines-all", app, body)
        _check_control_get_method("grades:grades-all", app, body)
        _check_control_post_method("routes:add-route", app, body, "routes")
        # each item should have information of the route and bunch of controls
        for item in body["items"]:
            assert "date" in item
            assert "location" in item
            assert "discipline" in item
            assert "grade" in item
            assert "extraInfo" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("locations:in-location", app, item)
            _check_control_get_method("disciplines:in-discipline", app, item)
            _check_control_get_method("grades:in-grade", app, item)
            _check_control_get_method("profile", app, item)
            _check_control_put_method("routes:edit-route", app, item, "routes")
            _check_control_delete_method("routes:delete", app, item)

    def test_post_valid_request(self, app):
        """
        Tests post method to create a new route for user
        """
        # test wrong url
        # for user not found
        valid = _route_template()
        resp = app.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test that we can create a new route
        valid = _route_template()
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        # we created third user, and see that the returned URL is correct
        assert resp.headers["Location"].endswith(self.RESOURCE_URL+'11/')

        # now get the new route and validate data
        resp = app.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["date"] == "2030-12-31"
        assert body["location"] == "Olympics"
        assert body["discipline"] == "Speed climbing"
        assert body["grade"] == "9a"
        assert body["extraInfo"] == "1 this is the extra information"

        # test with wrong date information
        valid = _route_template()
        valid["date"] = 'asdasdsda'
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # location, discipline, or grade can not be empty string
        valid = _route_template()
        valid["location"] = ""
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _route_template()
        valid["discipline"] = ""
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _route_template()
        valid["grade"] = ""
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # date is required among other items, we should get 400 back without it
        valid.pop("date")
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # remove extraInfo to see that also just minimum is OK
        valid = _route_template()
        valid.pop("extraInfo")
        resp = app.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        # we created third user, and see that the returned URL is correct
        assert resp.headers["Location"].endswith(self.RESOURCE_URL+'12/')

        # test put response to invalid request
        valid = _route_template()
        resp = app.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415


class TestRouteItem(object):
    """
    Test the route item resource: GET, PUT, DELETE
    """

    RESOURCE_URL = "/api/users/1/routes/1/"
    INVALID_USER_URL = "/api/users/saddsa/routes/1/"
    INVALID_ROUTE_URL = "/api/users/1/routes/122213/"

    def test_get(self, app):
        """
        test get method to return the information of first route of first user
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "routes")
        # check content
        assert body["date"] == datetime.today().strftime('%Y-%m-%d')
        assert body["location"] == "Oulun Kiipeilykeskus"
        assert body["discipline"] == "Bouldering"
        assert body["grade"] == "6A"
        _check_control_get_method("self", app, body)
        _check_control_get_method("profile", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("locations:in-location", app, body)
        _check_control_get_method("disciplines:in-discipline", app, body)
        _check_control_get_method("grades:in-grade", app, body)
        _check_control_put_method("routes:edit-route", app, body, "routes")
        _check_control_delete_method("routes:delete", app, body)

        # and see also that we get 404 if we try to access invalid user
        resp = app.get(self.INVALID_USER_URL)
        assert resp.status_code == 404
        # and same for invalid route
        resp = app.get(self.INVALID_ROUTE_URL)
        assert resp.status_code == 404

    def test_put_valid_request(self, app):
        """
        Tests put method to edit information of a route
        """
        valid = _route_template()

        # wrong Content
        resp = app.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # for user not found
        resp = app.put(self.INVALID_USER_URL, json=valid)
        assert resp.status_code == 404

        # for route not found
        resp = app.put(self.INVALID_ROUTE_URL, json=valid)
        assert resp.status_code == 404

        # change only location
        valid["location"] = "moon"
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # try wrong date information
        valid["date"] = "yesterday"
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # location, discipline, or grade can not be empty string
        valid = _route_template()
        valid["location"] = ""
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _route_template()
        valid["discipline"] = ""
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _route_template()
        valid["grade"] = ""
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # should be accepted without extraInfo
        valid = _route_template()
        valid.pop("extraInfo")
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove email to see that it is not accepted
        valid = _route_template()
        valid.pop("date")
        resp = app.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    def test_delete(self, app):
        """
        test delete method
        """
        # delete user
        resp = app.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        # cannot delete it second time
        resp = app.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        # cannot delete route for user that does not exist
        resp = app.delete(self.INVALID_USER_URL)
        assert resp.status_code == 404
        # cannot delete route that does not exist
        resp = app.delete(self.INVALID_ROUTE_URL)
        assert resp.status_code == 404


class TestLocationCollection(object):
    """
    Test the location collection resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/locations/"
    INVALID_URL = "/api/users/saddsa/routes/locations/"

    def test_get(self, app):
        """
        test get method to return the locations lists for user
        """
        # for user not found
        resp = app.get(self.INVALID_URL)
        assert resp.status_code == 404

        # test the list
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "locations")
        _check_control_get_method("self", app, body)
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        assert len(body["items"]) == 4  # number of UNIQUE locations created above
        for item in body["items"]:
            assert "location" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("locations:in-location", app, item)
            _check_control_get_method("profile", app, item)


class TestLocationItem(object):
    """
    Test the location item resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/locations/1/"
    INVALID_USER_URL = "/api/users/saddsa/routes/locations/1/"
    INVALID_LOCATION_URL = "/api/users/1/routes/locations/122213/"

    def test_get(self, app):
        """
        test get method to return the information of first location of first user
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "locations")
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_get_method("locations:locations-all", app, body)
        # check content
        assert len(body["items"]) == 2  # number of routes in location created above
        for item in body["items"]:
            assert "date" in item
            assert "location" in item
            assert "discipline" in item
            assert "grade" in item
            assert "extraInfo" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("profile", app, item)
            _check_control_get_method("disciplines:in-discipline", app, item)
            _check_control_get_method("grades:in-grade", app, item)
            _check_control_put_method("routes:edit-route", app, item, "routes")
            _check_control_delete_method("routes:delete", app, item)

        # and see also that we get 404 if we try to access invalid user
        resp = app.get(self.INVALID_USER_URL)
        assert resp.status_code == 404
        # and same for invalid location
        resp = app.get(self.INVALID_LOCATION_URL)
        assert resp.status_code == 404


class TestDisciplineCollection(object):
    """
    Test the discipline collection resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/disciplines/"
    INVALID_URL = "/api/users/saddsa/routes/disciplines/"

    def test_get(self, app):
        """
        test get method to return the disciplines lists for user
        """
        # for user not found
        resp = app.get(self.INVALID_URL)
        assert resp.status_code == 404

        # test the list
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "disciplines")
        _check_control_get_method("self", app, body)
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        assert len(body["items"]) == 3  # number of UNIQUE disciplines created above
        for item in body["items"]:
            assert "discipline" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("disciplines:in-discipline", app, item)
            _check_control_get_method("profile", app, item)


class TestDisciplineItem(object):
    """
    Test the discipline item resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/disciplines/1/"
    INVALID_USER_URL = "/api/users/saddsa/routes/disciplines/1/"
    INVALID_DISCIPLINE_URL = "/api/users/1/routes/disciplines/122213/"

    def test_get(self, app):
        """
        test get method to return the information of first discipline of first user
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "disciplines")
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_get_method("disciplines:disciplines-all", app, body)
        # check content
        assert len(body["items"]) == 2  # number of routes in discipline created above
        for item in body["items"]:
            assert "date" in item
            assert "location" in item
            assert "discipline" in item
            assert "grade" in item
            assert "extraInfo" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("profile", app, item)
            _check_control_get_method("locations:in-location", app, item)
            _check_control_get_method("grades:in-grade", app, item)
            _check_control_put_method("routes:edit-route", app, item, "routes")
            _check_control_delete_method("routes:delete", app, item)

        # and see also that we get 404 if we try to access invalid user
        resp = app.get(self.INVALID_USER_URL)
        assert resp.status_code == 404
        # and same for invalid location
        resp = app.get(self.INVALID_DISCIPLINE_URL)
        assert resp.status_code == 404


class TestGradeCollection(object):
    """
    Test the grade collection resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/grades/"
    INVALID_URL = "/api/users/saddsa/routes/grades/"

    def test_get(self, app):
        """
        test get method to return the grades lists for user
        """
        # for user not found
        resp = app.get(self.INVALID_URL)
        assert resp.status_code == 404

        # test the list
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "grades")
        _check_control_get_method("self", app, body)
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        assert len(body["items"]) == 3  # number of UNIQUE grades created above
        for item in body["items"]:
            assert "grade" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("grades:in-grade", app, item)
            _check_control_get_method("profile", app, item)


class TestGradeItem(object):
    """
    Test the grade item resource: GET
    """

    RESOURCE_URL = "/api/users/1/routes/grades/1/"
    INVALID_USER_URL = "/api/users/saddsa/routes/grades/1/"
    INVALID_GRADE_URL = "/api/users/1/routes/grades/122213/"

    def test_get(self, app):
        """
        test get method to return the information of first grade of first user
        """
        resp = app.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(app, body, "grades")
        _check_control_get_method("users:climbed-by", app, body)
        _check_control_get_method("routes:routes-all", app, body)
        _check_control_get_method("grades:grades-all", app, body)
        # check content
        assert len(body["items"]) == 1  # number of routes in grade created above
        for item in body["items"]:
            assert "date" in item
            assert "location" in item
            assert "discipline" in item
            assert "grade" in item
            assert "extraInfo" in item
            _check_control_get_method("self", app, item)
            _check_control_get_method("profile", app, item)
            _check_control_get_method("locations:in-location", app, item)
            _check_control_get_method("disciplines:in-discipline", app, item)
            _check_control_put_method("routes:edit-route", app, item, "routes")
            _check_control_delete_method("routes:delete", app, item)

        # and see also that we get 404 if we try to access invalid user
        resp = app.get(self.INVALID_USER_URL)
        assert resp.status_code == 404
        # and same for invalid location
        resp = app.get(self.INVALID_GRADE_URL)
        assert resp.status_code == 404
