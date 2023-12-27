from datetime import datetime
import uuid
from typing import List, Union
from bytepit_api.database import db
from bytepit_api.models.db_models import Competition, Trophy
from bytepit_api.models.dtos import ProblemDTO


def get_competitions():
    query_tuple = ("""SELECT * FROM competitions""", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return []


def get_trophies_by_competition(competition_id: uuid.UUID):
    query_tuple = ("""SELECT * FROM trophies WHERE competition_id = %s""", (competition_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Trophy(**trophy) for trophy in result["result"]]
    else:
        return []


def insert_competition(
    name: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    problems: List[uuid.UUID],
    organiser_id: uuid.UUID,
    parent_id: Union[uuid.UUID, None] = None,
):
    problems_array = "{" + ",".join(map(str, problems)) + "}" if problems else None
    competition_insert_query = (
        """
        INSERT INTO competitions (name, description, start_time, end_time, parent_id, organiser_id, problems)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (name, description, start_time, end_time, parent_id, organiser_id, problems_array),
    )
    result = db.execute_one(competition_insert_query)
    if result["affected_rows"] == 1:
        return result["result"][0]["id"]
    else:
        return None


def insert_trophy(competition_id: uuid.UUID, position: int, icon):
    icon_binary = icon.file.read() if icon else None
    if not icon:
        return False
    trophy_insert_query = (
        """
        INSERT INTO trophies (competition_id, position, icon)
        VALUES (%s, %s, %s)
        """,
        (competition_id, position, icon_binary),
    )
    result = db.execute_one(trophy_insert_query)
    return result["affected_rows"] == 1


def get_problems(problem_ids: List[uuid.UUID]):
    query_tuple = (f"SELECT * FROM problems WHERE id IN ({', '.join(['%s']*len(problem_ids))});", tuple(problem_ids))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return []


def get_active_competitions():
    query_tuple = (
        """SELECT * FROM competitions WHERE start_time < NOW() AND end_time > NOW() ORDER BY start_time ASC""",
        (),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return []


def get_random_competition():
    query_tuple = (
        """SELECT * FROM competitions ORDER BY RANDOM() LIMIT 1""",
        (),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return Competition(**result["result"][0])
    else:
        return None


def get_competition(competition_id: uuid.UUID):
    query_tuple = (
        """SELECT * FROM competitions WHERE id = %s""",
        (competition_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return Competition(**result["result"][0])
    else:
        return None


def set_user_trophy(competition_id: uuid.UUID, user_id: uuid.UUID, position: int):
    query_tuple = (
        """
        UPDATE trophies
        SET user_id = %s
        WHERE competition_id = %s AND position = %s
        """,
        (user_id, competition_id, position),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def modify_competition(competition_id: uuid.UUID, competition: Competition):
    query_tuple = (
        """
        UPDATE competitions
        SET name = %s, description = %s, start_time = %s, end_time = %s, parent_id = %s, organiser_id = %s, problems = %s
        WHERE id = %s
        """,
        (
            competition.name,
            competition.description,
            competition.start_time,
            competition.end_time,
            competition.parent_id,
            competition.organiser_id,
            competition.problems,
            competition_id,
        ),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def delete_competition(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM competitions WHERE id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def delete_trophy_by_competition_id(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM trophies WHERE competition_id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] > 0


def get_competitions_by_organiser(organiser_id: uuid.UUID):
    query_tuple = (
        """SELECT * FROM competitions WHERE organiser_id = %s ORDER BY start_time DESC""",
        (organiser_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return []
