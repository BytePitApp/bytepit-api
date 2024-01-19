import sys
import os

import pytest
import pydantic
from unittest.mock import MagicMock, AsyncMock, patch

os.environ[
    "SECRET_KEY"
] = "5ce3b19d23543100e7be58f39c430a8dfb1b4584fec88283583515b05481cdf4"
sys.modules["bytepit_api.database"] = MagicMock()
sys.modules["bytepit_api.helpers.email_helpers"] = MagicMock()
sys.modules["bytepit_api.database.problem_queries"] = MagicMock()

from fastapi import HTTPException

from bytepit_api.models.dtos import LoginDTO, RegisterDTO


@pytest.mark.asyncio
async def test_register_bad():
    from bytepit_api import database
    from bytepit_api.helpers import email_helpers

    database.auth_queries = AsyncMock()
    database.auth_queries.get_user_by_email = MagicMock(return_value=False)
    database.auth_queries.get_user_by_username = MagicMock(return_value=False)
    database.auth_queries.create_user = AsyncMock(return_value=True)
    email_helpers.send_verification_email = AsyncMock()

    with pytest.raises(pydantic.ValidationError):
        form_data = RegisterDTO(
            username="testuser",
            password="testpassword",
            name="Test",
            surname="User",
            email="testuser@examp.com",
            role="sadf",
            image=None,
        )


@pytest.mark.asyncio
async def test_register_good():
    from bytepit_api import database
    from bytepit_api.helpers import email_helpers

    database.auth_queries = AsyncMock()
    database.auth_queries.get_user_by_email = MagicMock(return_value=False)
    database.auth_queries.get_user_by_username = MagicMock(return_value=False)
    database.auth_queries.create_user = AsyncMock(return_value=True)
    email_helpers.send_verification_email = AsyncMock()

    from bytepit_api.services.auth_service import register

    form_data = RegisterDTO(
        username="testuser",
        password="testpassword",
        name="Test",
        surname="User",
        email="fdge@gmail.com",
        role="organiser",
        image=None,
    )

    response = await register(form_data)

    assert response.status_code == 201
    email_helpers.send_verification_email.assert_called_once()


def test_create_problem():
    from fastapi import UploadFile, Response
    from bytepit_api import database
    from bytepit_api.models.dtos import CreateProblemDTO
    from bytepit_api.services.problem_service import create_problem
    import uuid
    from io import BytesIO

    database.problem_queries = AsyncMock()
    database.problem_queries.insert_problem = AsyncMock(return_value=uuid.uuid4())
    problem_dto_mock = MagicMock(spec=CreateProblemDTO)
    problem_dto_mock.name = "Test Problem"
    problem_dto_mock.example_input = "Example Input"
    problem_dto_mock.example_output = "Example Output"
    problem_dto_mock.is_hidden = False
    problem_dto_mock.num_of_points = 1.0
    problem_dto_mock.runtime_limit = 1.0
    problem_dto_mock.description = "This is a test problem"

    mock_file1 = MagicMock(spec=UploadFile)
    mock_file2 = MagicMock(spec=UploadFile)
    mock_file1.filename = "1_in.txt"
    mock_file2.filename = "1_out.txt"

    mock_file1.file = BytesIO(b"Test input file content")
    mock_file2.file = BytesIO(b"Test output file content")

    problem_dto_mock.test_files = [mock_file1, mock_file2]

    problem_dto_mock.is_private = False

    current_user_id = uuid.uuid4()

    result = create_problem(problem_dto_mock, current_user_id)

    assert isinstance(result, Response)
    assert result.status_code == 201


def test_create_problem_bad():
    from fastapi import UploadFile, Response
    from bytepit_api import database
    from bytepit_api.models.dtos import CreateProblemDTO
    from bytepit_api.services.problem_service import create_problem
    import uuid
    from io import BytesIO

    database.problem_queries = AsyncMock()
    database.problem_queries.insert_problem = AsyncMock(return_value=uuid.uuid4())

    problem_dto_mock = MagicMock(spec=CreateProblemDTO)
    problem_dto_mock.name = "Test Problem"
    problem_dto_mock.example_input = "Example Input"
    problem_dto_mock.example_output = "Example Output"
    problem_dto_mock.is_hidden = False
    problem_dto_mock.num_of_points = 1.0
    problem_dto_mock.runtime_limit = 1.0
    problem_dto_mock.description = "This is a test problem"

    mock_file1 = MagicMock(spec=UploadFile)
    mock_file2 = MagicMock(spec=UploadFile)
    mock_file1.filename = "1.txt"
    mock_file2.filename = "dsrthdrg.txt"

    problem_dto_mock.test_files = [mock_file1, mock_file2]

    problem_dto_mock.is_private = False

    current_user_id = uuid.uuid4()

    with pytest.raises(HTTPException):
        result = create_problem(problem_dto_mock, current_user_id)


def test_create_competition():
    from fastapi import Response
    from bytepit_api import database
    from bytepit_api.models.dtos import CreateCompetitionDTO
    from bytepit_api.services.competition_service import create_competition
    import uuid
    from unittest.mock import AsyncMock, MagicMock
    from datetime import datetime

    database.competition_queries = MagicMock()
    database.competition_queries.insert_competition = AsyncMock(
        return_value=uuid.uuid4()
    )
    problemlist = [uuid.uuid4(), uuid.uuid4()]
    database.competition_queries.get_problems = AsyncMock(return_value=problemlist)
    print(len(problemlist))
    competition_dto_mock = MagicMock(spec=CreateCompetitionDTO)
    competition_dto_mock.name = "Test Competition"
    competition_dto_mock.description = "This is a test competition"
    competition_dto_mock.start_time = datetime.strptime(
        "2021-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"
    )
    competition_dto_mock.end_time = datetime.strptime(
        "2021-01-02T00:00:00", "%Y-%m-%dT%H:%M:%S"
    )
    competition_dto_mock.is_private = False
    competition_dto_mock.image = None
    competition_dto_mock.organiser_id = uuid.uuid4()
    competition_dto_mock.problems = database.competition_queries.get_problems
    competition_dto_mock.first_place_trophy = None
    competition_dto_mock.second_place_trophy = None
    competition_dto_mock.third_place_trophy = None
    competition_dto_mock.parent_id = uuid.uuid4()

    result = create_competition(competition_dto_mock, competition_dto_mock.organiser_id)

    assert isinstance(result, Response)
    assert result.status_code == 201


def test_create_competition_bad():
    from bytepit_api import database
    from bytepit_api.models.dtos import CreateCompetitionDTO
    from bytepit_api.services.competition_service import create_competition
    import uuid
    from unittest.mock import AsyncMock, MagicMock
    from datetime import datetime

    database.competition_queries = MagicMock()
    database.competition_queries.insert_competition = AsyncMock(
        return_value=uuid.uuid4()
    )

    competition_dto_mock = MagicMock(spec=CreateCompetitionDTO)
    competition_dto_mock.name = "Test Competition"
    competition_dto_mock.description = "This is a test competition"
    competition_dto_mock.start_time = datetime.strptime(
        "2021-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"
    )
    competition_dto_mock.end_time = datetime.strptime(
        "2021-01-02T00:00:00", "%Y-%m-%dT%H:%M:%S"
    )
    competition_dto_mock.is_private = False
    competition_dto_mock.image = None
    competition_dto_mock.organiser_id = uuid.uuid4()
    competition_dto_mock.problems = [uuid.uuid4(), uuid.uuid4()]
    competition_dto_mock.first_place_trophy = None
    competition_dto_mock.second_place_trophy = None
    competition_dto_mock.third_place_trophy = None
    competition_dto_mock.parent_id = uuid.uuid4()

    with pytest.raises(HTTPException):
        create_competition(competition_dto_mock, competition_dto_mock.organiser_id)
