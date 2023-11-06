import inspect

from enum import Enum
from typing import Annotated

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
    contenstant = "contenstant"


class Token(BaseModel):
    access_token: str
    token_type: str


@as_form
class RegistrationForm(BaseModel):
    username: Annotated[str, Form()]
    password: Annotated[str, Form()]
    name: Annotated[str, Form()]
    surname: Annotated[str, Form()]
    email: Annotated[EmailStr, Form()]
    role: Annotated[Role, Form()] = Role.contenstant
    # image: Annotated[str, Form()] = None
