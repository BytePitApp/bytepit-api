import inspect
import uuid

from enum import Enum
from typing import Annotated, Union

from fastapi import Form
from pydantic import BaseModel, EmailStr


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
    role: Annotated[Role, Form()]
    # image: Annotated[str, Form()] = None


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
    role: str
    name: str
    surname: str
    is_verified: bool


class UserInDB(User):
    id: uuid.UUID
    password_hash: str
