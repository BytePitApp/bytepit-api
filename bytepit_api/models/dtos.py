import base64
import uuid
from datetime import datetime, time

from typing import Annotated, Union, List

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, EmailStr, field_validator, field_serializer, model_validator
from pydantic_core import PydanticCustomError

from bytepit_api.models.shared import as_form
from bytepit_api.models.enums import RegisterRole, Role

@as_form
class RegisterDTO(BaseModel):
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
class LoginDTO(BaseModel):
    username: Annotated[str, Form()]
    password: Annotated[str, Form()]
    scope: Annotated[str, Form()] = ""
    client_id: Annotated[Union[str, None], Form()] = None
    client_secret: Annotated[Union[str, None], Form()] = None
    grant_type: Annotated[Union[str, None], Form(pattern="password")] = None


class UserDTO(BaseModel):
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
        

class TokenDTO(BaseModel):
    access_token: str
    token_type: str


class ProblemDTO(BaseModel):
    id: Union[uuid.UUID, None] = None
    name: Union[str, None] = None
    example_input: Union[str, None] = None
    example_output: Union[str, None] = None
    is_hidden: Union[bool, None] = None
    num_of_points: Union[float, None] = None
    runtime_limit: Union[time, None] = None
    description: Union[str, None] = None
    organiser_id: Union[uuid.UUID, None] = None
    is_private: Union[bool, None] = None
    created_on: Union[datetime, None] = None

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points is not None and num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points


class CreateProblemDTO(BaseModel):
    name: str
    example_input: str
    example_output: str
    is_hidden: bool
    num_of_points: float
    runtime_limit: str
    description: str
    test_files: List[UploadFile]
    is_private: bool

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points
    

class ModifyProblemDTO(BaseModel):
    name: Union[str, None] = None
    example_input: Union[str, None] = None
    example_output: Union[str, None] = None
    is_hidden: Union[bool, None] = None
    num_of_points: Union[float, None] = None
    runtime_limit: Union[str, None] = None
    description: Union[str, None] = None
    test_files: List[UploadFile] = []
    is_private: Union[bool, None] = None

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points is not None and num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points


class CompetitionDTO(BaseModel):
    name: str
    description: str
    start_time: str
    end_time: str
    parent_id: Union[uuid.UUID, None] = None
    problems: List[ProblemDTO]


class CreateCompetitionDTO(BaseModel):
    name: str
    description: str
    start_time: str
    end_time: str
    parent_id: Union[uuid.UUID, None] = None
    problems: List[uuid.UUID]


class ModifyCompetitionDTO(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    start_time: Union[str, None] = None
    end_time: Union[str, None] = None
    parent_id: Union[uuid.UUID, None] = None
    problems: Union[List[uuid.UUID], None] = None
