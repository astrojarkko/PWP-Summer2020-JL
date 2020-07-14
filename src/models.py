from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

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
db.create_all()
