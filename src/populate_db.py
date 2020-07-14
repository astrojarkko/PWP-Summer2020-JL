import random
from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from models import db
from models import User, Route, Location, Discipline, Grade


# define pre-described climbing disciplines, grades, and locations
disciplines = ["Bouldering", "Bouldering", "Toprope"]
grades = ["6A+", "6A+", "6B+"]
locations = ["Oulun Kiipeilykeskus", "Oulun Kiipeilykeskus", "Magic Woods"]

def populate_models():

    # add two Users
    for i in range(1, 3):
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

populate_models()
