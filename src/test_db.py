"""
Following course material testing example, perform tests on the
database model.
"""

import os
import pytest
import tempfile
from datetime import datetime

import models as app

from models import db
from models import User, Route, Location, Discipline, Grade

from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


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





def test_create_user(db_handle):
    """test that we can create an user"""
    user = get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1


def test_create_route(db_handle):
    """test that we can create a route"""
    route = get_route()
    db_handle.session.add(route)
    db_handle.session.commit()
    assert Route.query.count() == 1


def test_create_location(db_handle):
    """test that we can create a location"""
    location = get_location()
    db_handle.session.add(location)
    db_handle.session.commit()
    assert Location.query.count() == 1


def test_create_discipline(db_handle):
    """test that we can create a location"""
    discipline = get_discipline()
    db_handle.session.add(discipline)
    db_handle.session.commit()
    assert Discipline.query.count() == 1


def test_create_grade(db_handle):
    """test that we can create a grade"""
    grade = get_grade()
    db_handle.session.add(grade)
    db_handle.session.commit()
    assert Grade.query.count() == 1
