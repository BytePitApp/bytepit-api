import base64
import uuid

from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, field_serializer, field_validator

from bytepit_api.models.enums import Role


class User(BaseModel):
    id: uuid.UUID
    password_hash: str
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


class Problem(BaseModel):
    id: uuid.UUID
    name: str
    example_input: str
    example_output: str
    is_hidden: bool
    num_of_points: float
    runtime_limit: float
    description: str
    organiser_id: uuid.UUID
    is_private: bool
    created_on: datetime

    @field_validator("num_of_points")
    @classmethod
    def validate_num_of_points(cls, num_of_points):
        if num_of_points <= 0:
            raise ValueError("num_of_points must be greater than 0")
        return num_of_points


class Competition(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    parent_id: Union[uuid.UUID, None] = None
    organiser_id: uuid.UUID
    problems: List[uuid.UUID]


class Trophy(BaseModel):
    id: uuid.UUID
    competition_id: uuid.UUID
    position: int
    user_id: Union[uuid.UUID, None] = None
    icon: str

    @field_serializer("icon")
    @classmethod
    def serialize_image(cls, image):
        if image:
            encoded_file_content = base64.b64encode(image).decode("utf-8")
            return encoded_file_content


class ProblemResult(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    competition_id: uuid.UUID
    user_id: uuid.UUID
    average_runtime: float
    is_correct: bool
    num_of_points: float
    source_code: str
