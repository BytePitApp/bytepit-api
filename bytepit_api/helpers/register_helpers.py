import secrets

from passlib.context import CryptContext
from bytepit_api.database.queries import create_user


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def generate_confirmation_token():
    return secrets.token_urlsafe(20)


def register_user(username, password, name, surname, email, role, image):
    confirmation_token = generate_confirmation_token()
    password_hash = get_password_hash(password)
    result = create_user(username, password_hash, name, surname, email, role, image, confirmation_token)
    if not result:
        return None
    return confirmation_token
