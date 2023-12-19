import uuid
from typing import List
from bytepit_api.database import db
from bytepit_api.models.dtos import ProblemDTO, TrophyDTO

def get_trophies_by_ids(trophy_ids: List[uuid.UUID]):
    query_tuple = (f"SELECT * FROM trophies WHERE id IN ({', '.join(['%s']*len(trophy_ids))});", tuple(trophy_ids))   
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [TrophyDTO(**trophy) for trophy in result["result"]]
    else:
        return []


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


def delete_trophy_by_competition_id(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM trophies WHERE competition_id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] > 0
