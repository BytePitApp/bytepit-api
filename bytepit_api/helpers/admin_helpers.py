import uuid

from bytepit_api.database.queries import update_user_role
from bytepit_api.models.auth_schemes import Role


def save_role_to_db(user_id: uuid.UUID, role: str):
    return update_user_role(user_id, role)


def verify_role(role: str):
    return role in [role.value for role in Role]