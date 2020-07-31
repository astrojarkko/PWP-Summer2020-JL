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
# we exclude this section from testing, since they are only used to populate the DB
def init_db_command():  # pragma: no cover
    db.create_all()
    print("Database initialized.")

# to populate the database for testing with users that have several climbs etc.
# NOTE:
# modified from the models.py of the pwp-course-sensorhub-api-example
@click.command("testgen")
@with_appcontext
# we also exclude this from testing
def generate_test_data():  # pragma: no cover
    import random
    from datetime import datetime

    # define pre-described climbing disciplines, grades, and locations
    disciplines = ["Bouldering", "Bouldering", "Toprope", "Lead"]
    grades = ["5", "5", "6A", "6A", "6A+", "6A+", "6B", "6B", "6B+"]
    locations = ["Oulun Kiipeilykeskus", "Oulun Kiipeilykeskus", "Magic Woods"]

    for i in range(1, 6):
        user = User(email="{}email@url.com".format(i), firstName="First{}".format(i), lastName="Last{}".format(i))
        db.session.add(user)
        db.session.commit()

        # for each add three routes climbed, the locations, disciplines, and grades
        # are taken from the above lists
        for j in range(0, 100):

            # check if the location, discipline, or grade already exists, it it does
            # then use the already found one
            loc = random.choice(locations)
            location = db.session.query(Location).filter_by(name=loc).first()
            if not location:
                location = Location(name=loc)

            discp = random.choice(disciplines)
            discipline = db.session.query(Discipline).filter_by(name=discp).first()
            if not discipline:
                discipline = Discipline(name=discp)

            gr = random.choice(grades)
            grade = db.session.query(Grade).filter_by(name=gr).first()
            if not grade:
                grade = Grade(name=gr)

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

    print("Database populated succesfully.")
