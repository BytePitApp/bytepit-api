from enum import Enum


class Role(str, Enum):
    organiser = "organiser"
    contestant = "contestant"
    admin = "admin"


class RegisterRole(str, Enum):
    organiser = "organiser"
    contestant = "contestant"


class Language(str, Enum):
    python = "python"
    c = "c"
    cpp = "cpp"
    node = "nodejs"
    javascript = "javascript"
    java = "java"
