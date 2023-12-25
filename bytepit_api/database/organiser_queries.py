import uuid

from bytepit_api.database import db
from bytepit_api.models.db_models import Problem, Competition


def get_problems_by_organiser(organiser_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE organiser_id = %s", (organiser_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Problem(**problem) for problem in result["result"]]
    else:
        return None


def get_competitions_by_organiser(organiser_id: uuid.UUID):
    query_tuple = ("""SELECT * FROM competitions WHERE organiser_id = %s""", (organiser_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return None
