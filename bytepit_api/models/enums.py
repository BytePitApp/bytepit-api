from enum import Enum

class Role(str, Enum):
    organiser = "organiser"
    contestant = "contestant"
    admin = "admin"


class RegisterRole(str, Enum):
    organiser = "organiser"
    contestant = "contestant"
