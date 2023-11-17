import base64
import inspect
import uuid

from enum import Enum
from typing import Annotated, Union

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, EmailStr, field_serializer, field_validator
from pydantic_core import PydanticCustomError


def as_form(cls):
    new_params = [
        inspect.Parameter(
            field_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.default,
            annotation=Annotated[model_field.annotation, model_field.metadata, Form()],
        )
        for field_name, model_field in cls.model_fields.items()
    ]

    cls.__signature__ = cls.__signature__.replace(parameters=new_params)

    return cls


class Role(str, Enum):
    organiser = "organiser"
    contestant = "contestant"
    admin = "admin"


class RegisterRole(str, Enum):
    organiser = "organiser"
    contestant = "contestant"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


@as_form
class RegistrationForm(BaseModel):
    username: Annotated[str, Form()]
    password: Annotated[str, Form()]
    name: Annotated[str, Form()]
    surname: Annotated[str, Form()]
    email: Annotated[EmailStr, Form()]
    role: Annotated[RegisterRole, Form()]
    image: Annotated[Union[UploadFile, None], File()] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, username):
        if len(username) < 4:
            raise PydanticCustomError("length", "Username must be at least 4 characters long")
        return username

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise PydanticCustomError("length", "Password must be at least 8 characters long")
        return password


@as_form
class LoginForm(BaseModel):
    username: Annotated[str, Form()]
    password: Annotated[str, Form()]
    scope: Annotated[str, Form()] = ""
    client_id: Annotated[Union[str, None], Form()] = None
    client_secret: Annotated[Union[str, None], Form()] = None
    grant_type: Annotated[Union[str, None], Form(pattern="password")] = None


class User(BaseModel):
    username: str
    email: str
    role: Role
    name: str
    surname: str
    is_verified: bool
    approved_by_admin: bool
    image: Union[bytes, None] = None

    @field_serializer("image")
    @classmethod
    def serialize_image(cls, image):
        if image:
            encoded_file_content = base64.b64encode(image).decode("utf-8")
            return encoded_file_content


class UserInDB(User):
    id: uuid.UUID
    password_hash: str
