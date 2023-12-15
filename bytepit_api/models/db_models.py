import base64
import uuid

from typing import Union, List

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
    runtime_limit: str
    description: str
    organiser_id: uuid.UUID
    is_private: bool
    created_on: str

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
    start_time: str
    end_time: str
    parent_id: Union[uuid.UUID, None] = None
    problems: List[uuid.UUID]
