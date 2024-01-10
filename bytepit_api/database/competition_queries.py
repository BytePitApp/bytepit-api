from datetime import datetime
import uuid
from typing import List, Union
from bytepit_api.database import db
from bytepit_api.models.db_models import Competition, Trophy
from bytepit_api.models.dtos import ProblemDTO


def get_competitions():
    query_tuple = ("""SELECT * FROM competitions WHERE parent_id IS NULL""", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return []


def get_virtual_competitions():
    query_tuple = ("""SELECT * FROM competitions WHERE parent_id IS NOT NULL""", ())
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
        """SELECT * FROM competitions WHERE start_time < NOW() AND end_time > NOW() AND parent_id IS NULL ORDER BY start_time ASC""",
        (),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Competition(**competition) for competition in result["result"]]
    else:
        return []


def get_random_competition():
    query_tuple = (
        """SELECT * FROM competitions WHERE parent_id IS NULL ORDER BY RANDOM() LIMIT 1""",
        (),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return Competition(**result["result"][0])
    else:
        return None


def get_competition(competition_id: uuid.UUID):
    query_tuple = (
        """SELECT * FROM competitions WHERE id = %s AND parent_id IS NULL""",
        (competition_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return Competition(**result["result"][0])
    else:
        return None


def get_virtual_competition(competition_id: uuid.UUID):
    query_tuple = (
        """SELECT * FROM competitions WHERE id = %s AND parent_id IS NOT NULL""",
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


def get_competition_results(competition_id: uuid.UUID):
    query_tuple = (
        """
        SELECT
            problems.name,
            problem_results.*
        FROM problem_results
        JOIN problems
        ON problems.id = problem_results.problem_id
        WHERE  competition_id = %s;  
        """,
        (competition_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        problems_by_user = {}
        for problem in result["result"]:
            if problem["user_id"] not in problems_by_user:
                problems_by_user[problem["user_id"]] = {
                    "user_id": problem["user_id"],
                    "total_points": 0,
                    "problem_results": [],
                }
            problems_by_user[problem["user_id"]]["problem_results"].append(
                {
                    "id": problem["id"],
                    "problem_id": problem["problem_id"],
                    "user_id": problem["user_id"],
                    "competition_id": problem["competition_id"],
                    "num_of_points": problem["num_of_points"],
                    "source_code": problem["source_code"],
                    "language": problem["language"],
                    "average_runtime": problem["average_runtime"],
                    "is_correct": problem["is_correct"],
                }
            )
            problems_by_user[problem["user_id"]]["total_points"] += problem["num_of_points"]
        return sorted(problems_by_user.values(), key=lambda x: x["total_points"], reverse=True)
    else:
        return []


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


def get_trophies_by_user(user_id: uuid.UUID):
    query_tuple = (
        """
        WITH total_points AS (
        SELECT
            competition_id,
            user_id,
            SUM(num_of_points) as total_points
        FROM
            problem_results
        GROUP BY
            competition_id,
            user_id
        ),
        top_3_in_each_competition AS (
        SELECT
            competition_id,
            user_id,
            total_points,
            ROW_NUMBER() OVER(
            PARTITION BY competition_id
            ORDER BY
                total_points DESC
            ) as rn
        FROM
            total_points
        )
        SELECT
        top_3_in_each_competition.competition_id,
        top_3_in_each_competition.rn AS rank_in_competition,
        trophies.icon
        FROM
        top_3_in_each_competition
        LEFT JOIN trophies ON top_3_in_each_competition.competition_id = trophies.competition_id
        INNER JOIN competitions ON competitions.id = top_3_in_each_competition.competition_id
        AND rn = position
        WHERE
        rn <= 3
        AND top_3_in_each_competition.competition_id IS NOT NULL
        AND top_3_in_each_competition.user_id = %s
        AND competitions.end_time < NOW()
        AND competitions.parent_id IS NULL
        ORDER BY
        total_points DESC;
        """,
        (user_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return result["result"]
    else:
        return []
