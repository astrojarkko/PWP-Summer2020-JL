"""
Following course material testing example, perform tests on the
database model.
"""

import os
import pytest
import tempfile
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from routetracker import create_app, db
from routetracker.models import User, Route, Location, Discipline, Grade



@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
        }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_fname)


"""
Create boilerplates for populating the different tables in DB
"""


def get_user(id_num=1):
    """boilerplate for user as in test examples"""
    user = User(
                id=id_num,
                email="tesi@test.test",
                firstName="Test",
                lastName="User"
                )
    return user


def get_location(id_num=1):
    """boilerplate for location"""
    location = Location(
                        id=id_num,
                        name="test"
                        )
    return location


def get_discipline(id_num=1):
    """boilerplate for discipline"""
    discipline = Discipline(
                            id=id_num,
                            name="test"
                            )
    return discipline


def get_grade(id_num=1):
    """boilerplate for grade"""
    grade = Grade(
                  id=id_num,
                  name="test"
                  )
    return grade


def get_route(id_num=1):
    """boilerplate for user as in test examples"""
    route = Route(
                  id=id_num,
                  user=get_user(),
                  date=datetime.today(),
                  location=get_location(),
                  discipline=get_discipline(),
                  grade=get_grade(),
                  extraInfo="test"
                  )
    return route


"""
Test that items can be added and deleted in each table and commited to the DB:
"""


def test_create_user(app):
    with app.app_context():
        # test that we can create an user
        user = get_user()
        db.session.add(user)
        db.session.commit()
        assert User.query.count() == 1
        # and also delete
        db.session.delete(user)
        db.session.commit()
        assert User.query.count() == 0


def test_create_route(app):
    with app.app_context():
        # test that we can create a route
        route = get_route()
        db.session.add(route)
        db.session.commit()
        assert Route.query.count() == 1
        # and also delete
        db.session.delete(route)
        db.session.commit()
        assert Route.query.count() == 0


def test_create_location(app):
    with app.app_context():
        # test that we can create a location
        location = get_location()
        db.session.add(location)
        db.session.commit()
        assert Location.query.count() == 1
        # and also delete
        db.session.delete(location)
        db.session.commit()
        assert Location.query.count() == 0


def test_create_discipline(app):
    with app.app_context():
        # test that we can create a location
        discipline = get_discipline()
        db.session.add(discipline)
        db.session.commit()
        assert Discipline.query.count() == 1
        # and also delete
        db.session.delete(discipline)
        db.session.commit()
        assert Discipline.query.count() == 0


def test_create_grade(app):
    with app.app_context():
        # test that we can create a grade
        grade = get_grade()
        db.session.add(grade)
        db.session.commit()
        assert Grade.query.count() == 1
        # and also delete
        db.session.delete(grade)
        db.session.commit()
        assert Grade.query.count() == 0





def test_create_new_route_for_user(app):
    """
    Test that we can create an user and add new climbed routes for that user:
    """
    with app.app_context():
        # create user, and add a climb to it with location, discipline, and grades
        # nothing exists in any table at this point. This can be done by adding the
        # only as it will populate rest of the tables
        route = get_route()

        # commit changes
        db.session.add(route)
        db.session.commit()

        # now we want to add same kind of climb to the same user, because those
        # items already exit in the tables we need to retrieve them. Later on this
        # will be handled by the API code
        user = User.query.first()
        location = Location.query.first()
        discipline = Discipline.query.first()
        grade = Grade.query.first()

        route = Route(user=user,
                      date=datetime.today(),
                      location=location,
                      discipline=discipline,
                      grade=grade,
                      extraInfo="just a test")
        # commit changes
        db.session.add(route)
        db.session.commit()

        # test that route has two items now
        assert Route.query.count() == 2


def test_relationships(app):
    """
    Test relationships between the tables:
    """
    with app.app_context():
        # populate the tables
        route = get_route()
        db.session.add(route)
        db.session.commit()

        # check the relationships
        db_user = User.query.first()
        db_route = Route.query.first()
        db_location = Location.query.first()
        db_discipline = Discipline.query.first()
        db_grade = Grade.query.first()

        assert db_user == db_route.user
        assert db_location == db_route.location
        assert db_discipline == db_route.discipline
        assert db_grade == db_route.grade


"""
Test uniqueness in the tables:
"""


def test_user_uniqueness(app):
    with app.app_context():
        # users need to be unique
        user_a = get_user()
        user_b = get_user()
        db.session.add(user_a)
        db.session.add(user_b)
        with pytest.raises(IntegrityError):
            db.session.commit()
        # roll back the session after error
        db.session.rollback()


def test_location_uniqueness(app):
    with app.app_context():
        # locations need to be unique
        location_a = get_location()
        location_b = get_location()
        db.session.add(location_a)
        db.session.add(location_b)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_discipline_uniqueness(app):
    with app.app_context():
        # disciplines need to be unique
        discipline_a = get_discipline()
        discipline_b = get_discipline()
        db.session.add(discipline_a)
        db.session.add(discipline_b)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_grade_uniqueness(app):
    with app.app_context():
        # grades need to be unique
        grade_a = get_grade()
        grade_b = get_grade()
        db.session.add(grade_a)
        db.session.add(grade_b)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


"""
Test each table for NOT NULL and nullable values:
"""


def test_user_values(app):
    with app.app_context():
        # user table value tests
        user = get_user()

        # email can not be null
        user.email = None
        db.session.add(user)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # firstName and lastName can be null
        user = get_user()
        user.firstName = None
        user.lastName = None
        db.session.add(user)
        db.session.commit()
        assert user.firstName is None
        assert user.lastName is None


def test_location_values(app):
    with app.app_context():
        # location table value tests
        location = get_location()
        # set name to NULL and it should revert to default
        location.name = None
        db.session.add(location)
        db.session.commit()
        assert location.name == "Oulun Kiipeilykeskus"


def test_discipline_values(app):
    with app.app_context():
        # discipline table value tests
        discipline = get_discipline()
        # set name to NULL and it should revert to default
        discipline.name = None
        db.session.add(discipline)
        db.session.commit()
        assert discipline.name == "Bouldering"


def test_grade_values(app):
    with app.app_context():
        # grade table value tests
        grade = get_grade()
        # name can not be null
        grade.name = None
        db.session.add(grade)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_route_values(app):
    with app.app_context():
        # route table value tests
        route = get_route()
        db.session.add(route)
        db.session.commit()

        # foreign key user can not be null
        route.user = None
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # date can not be null
        route.date = None
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # extraInfo can be nullable
        route.extraInfo = None
        db.session.add(route)
        db.session.commit()
        assert route.extraInfo is None

        # foreign keys location, discipline, grade be null in order to keep information
        # of climbs even if some of these get deleted
        route.location = None
        route.discipline = None
        route.grade = None
        route.extraInfo = None
        db.session.add(route)
        db.session.commit()
        assert route.location is None
        assert route.discipline is None
        assert route.grade is None
        assert route.extraInfo is None


def test_update_cascade(app):
    """
    test that updates on values cascade from table to table:
    """
    with app.app_context():
        # create a route manually
        user = get_user()
        location = get_location()
        discipline = get_discipline()
        grade = get_grade()

        route = Route(
                      id=1,
                      user=user,
                      date=datetime.today(),
                      location=location,
                      discipline=discipline,
                      grade=grade
                      )
        db.session.add(route)
        db.session.commit()

        # user data can be changed
        user.email = "second@test.com"
        user.firstName = "Testing"
        user.lastName = "Isfun"
        db.session.commit()
        assert user.email == "second@test.com"
        assert user.firstName == "Testing"
        assert user.lastName == "Isfun"

        # location, discipline, and grade names can be changed
        location.name = "thisisatest"
        discipline.name = "thisisatest"
        grade.name = "thisisatest"
        db.session.commit()
        assert location.name == "thisisatest"
        assert discipline.name == "thisisatest"
        assert grade.name == "thisisatest"

        # foreign keys in routes need to be able to be updated as well
        location = Location(name="takapiha")
        discipline = Discipline(name="se edellä puuhun")
        grade = Grade(name="2A")
        route.location = location
        route.discipline = discipline
        route.grade = grade
        db.session.commit()
        assert route.location.name == "takapiha"
        assert route.discipline.name == "se edellä puuhun"
        assert route.grade.name == "2A"


def test_delete_cascade(app):
    """
    test ON DELETE cascading between tables
    """
    with app.app_context():
        # create a route manually
        user = get_user()
        location = get_location()
        discipline = get_discipline()
        grade = get_grade()

        route = Route(
                      id=1,
                      user=user,
                      date=datetime.today(),
                      location=location,
                      discipline=discipline,
                      grade=grade
                      )
        db.session.add(route)
        db.session.commit()

        # if user is deleted, then route should disappear as well, first make sure
        # that the route is found and then delete and test again
        assert Route.query.count() == 1
        db.session.delete(user)
        db.session.commit()
        assert Route.query.count() == 0

        # create route again
        user = get_user()
        route = Route(
                      id=1,
                      user=user,
                      date=datetime.today(),
                      location=location,
                      discipline=discipline,
                      grade=grade
                      )
        db.session.add(route)
        db.session.commit()

        # if location is deleted, then locationId foreign key is set to NULL in route
        assert Route.query.count() == 1
        db.session.delete(location)
        db.session.commit()
        assert route.locationId is None

        # if discipline is deleted, then disciplineId foreign key is set to NULL in route
        assert Route.query.count() == 1
        db.session.delete(discipline)
        db.session.commit()
        assert route.disciplineId is None

        # if grade is deleted, then gradeId foreign key is set to NULL in route
        assert Route.query.count() == 1
        db.session.delete(grade)
        db.session.commit()
        assert route.gradeId is None
