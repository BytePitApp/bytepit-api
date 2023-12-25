import base64
import uuid
from datetime import datetime


from typing import Annotated, List, Union

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, EmailStr, field_validator, field_serializer, model_validator
from pydantic_core import PydanticCustomError

from bytepit_api.models.shared import as_form
from bytepit_api.models.enums import Language, RegisterRole, Role


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
    id: uuid.UUID
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
    runtime_limit: Union[float, None] = None
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


@as_form
class CreateProblemDTO(BaseModel):
    name: Annotated[str, Form()]
    example_input: Annotated[str, Form()]
    example_output: Annotated[str, Form()]
    is_hidden: Annotated[bool, Form()]
    num_of_points: Annotated[float, Form()]
    runtime_limit: Annotated[float, Form()]
    description: Annotated[str, Form()]
    test_files: Annotated[List[UploadFile], File()] = []
    is_private: Annotated[bool, Form()]

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points


@as_form
class ModifyProblemDTO(BaseModel):
    name: Annotated[Union[str, None], Form()] = None
    example_input: Annotated[Union[str, None], Form()] = None
    example_output: Annotated[Union[str, None], Form()] = None
    is_hidden: Annotated[Union[bool, None], Form()] = None
    num_of_points: Annotated[Union[float, None], Form()] = None
    runtime_limit: Annotated[Union[float, None], Form()] = None
    description: Annotated[Union[str, None], Form()] = None
    test_files: Annotated[List[UploadFile], File()] = []
    is_private: Annotated[Union[bool, None], Form()] = None

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points is not None and num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points


class TrophyDTO(BaseModel):
    id: uuid.UUID
    competition_id: Union[uuid.UUID, None] = None
    user_id: Union[uuid.UUID, None] = None
    position: int
    icon: Union[bytes, None] = None

    @field_serializer("icon")
    @classmethod
    def serialize_icon(cls, icon):
        if icon:
            encoded_file_content = base64.b64encode(icon).decode("utf-8")
            return encoded_file_content


class CompetitionDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    parent_id: Union[uuid.UUID, None] = None
    organiser_id: Union[uuid.UUID, None] = None
    problems: Union[List[ProblemDTO], None] = []
    trophies: Union[List[TrophyDTO], None] = []


@as_form
class CreateCompetitionDTO(BaseModel):
    name: Annotated[str, Form()]
    description: Annotated[str, Form()]
    start_time: Annotated[str, Form()]
    end_time: Annotated[str, Form()]
    parent_id: Annotated[Union[uuid.UUID, None], Form()] = None
    problems: Annotated[List[uuid.UUID], Form()]
    first_place_trophy: Annotated[Union[UploadFile, None], File()] = None
    second_place_trophy: Annotated[Union[UploadFile, None], File()] = None
    third_place_trophy: Annotated[Union[UploadFile, None], File()] = None

    @model_validator(mode="after")
    def validate_start_time(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


@as_form
class ModifyCompetitionDTO(BaseModel):
    name: Annotated[Union[str, None], Form()] = None
    description: Annotated[Union[str, None], Form()] = None
    start_time: Annotated[Union[str, None], Form()] = None
    end_time: Annotated[Union[str, None], Form()] = None
    parent_id: Annotated[Union[uuid.UUID, None], Form()] = None
    problems: Annotated[List[uuid.UUID], Form()] = []
    first_place_trophy: Annotated[Union[UploadFile, None], File()] = None
    second_place_trophy: Annotated[Union[UploadFile, None], File()] = None
    third_place_trophy: Annotated[Union[UploadFile, None], File()] = None

    @model_validator(mode="after")
    def validate_start_time(self):
        if self.start_time is not None and self.end_time is not None and self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class ProblemResultDTO(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    competition_id: uuid.UUID
    user_id: uuid.UUID
    average_runtime: float
    is_correct: bool
    num_of_points: float
    source_code: str


@as_form
class CreateSubmissionDTO(BaseModel):
    problem_id: uuid.UUID
    competition_id: Union[uuid.UUID, None] = None
    source_code: str
    language: Language
