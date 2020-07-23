import click
from flask.cli import with_appcontext
from routetracker import db


"""
Course exercise/lecture material was used as base for this database model.

The table structures are given in the wiki documentation.
"""


# Table: User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    firstName = db.Column(db.String(64), nullable=True)
    lastName = db.Column(db.String(64), nullable=True)

    # delete routes in case the parent table item (user) is deleted
    routes = db.relationship("Route", cascade="delete", back_populates="user")

    @staticmethod
    def get_schema():
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


# Table: routes
class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # when user is deleted, also routes are deleted
    userId = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    # if location, discipline, or grade is deleted we want to keep record of the route still,
    # so we set these values to NULL in case of deletion in the parent table
    locationId = db.Column(db.Integer, db.ForeignKey("location.id", ondelete="SET NULL"))
    disciplineId = db.Column(db.Integer, db.ForeignKey("discipline.id", ondelete="SET NULL"))
    gradeId = db.Column(db.Integer, db.ForeignKey("grade.id", ondelete="SET NULL"))
    extraInfo = db.Column(db.String(250), nullable=True)

    user = db.relationship("User", back_populates="routes")
    location = db.relationship("Location", back_populates="routes")
    discipline = db.relationship("Discipline", back_populates="routes")
    grade = db.relationship("Grade", back_populates="routes")

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["date", "location", "discipline", "grade"]
        }
        props = schema["properties"] = {}
        props["date"] = {
            "description": "date when the route was climbed",
            "type": "string"
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


# Table: locations
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, default="Oulun Kiipeilykeskus")

    routes = db.relationship("Route", back_populates="location")


# Table: discipline
class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, default="Bouldering")

    routes = db.relationship("Route", back_populates="discipline")


# Table: grade
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)

    routes = db.relationship("Route", back_populates="grade")


# to initialize the database
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

# to populate the database for testing etc.
# NOTE:
# modified from the models.py of the pwp-course-sensorhub-api-example
@click.command("testgen")
@with_appcontext
def generate_test_data():
    import random
    from datetime import datetime

    # define pre-described climbing disciplines, grades, and locations
    disciplines = ["Bouldering", "Bouldering", "Toprope"]
    grades = ["6A+", "6A+", "6B+"]
    locations = ["Oulun Kiipeilykeskus", "Oulun Kiipeilykeskus", "Magic Woods"]

    for i in range(1, 5):
        user = User(email=f"{i}email@url.com", firstName=f"First{i}", lastName=f"Last{i}")
        db.session.add(user)
        db.session.commit()

        # for each add three routes climbed, the locations, disciplines, and grades
        # are taken from the above lists
        for j in range(0, 3):

            # check if the location, discipline, or grade already exists, it it does
            # then use the already found one
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
                          extraInfo=f"this is {i}, {j}"
                          )
            # add and commit changes
            db.session.add(route)
            db.session.commit()
