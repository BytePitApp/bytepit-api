import uuid

from datetime import datetime
from fastapi import HTTPException, status, Response

from bytepit_api.database import problem_queries, competition_queries
from bytepit_api.helpers import blob_storage_helpers, problem_helpers, submission_helpers
from bytepit_api.models.dtos import CreateSubmissionDTO, CreateProblemDTO, ModifyProblemDTO


def get_all_problems():
    result = problem_queries.get_all_problems()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not found any problems")
    return result


def get_problem(problem_id: uuid.UUID):
    return problem_helpers.get_problem(problem_id)


def delete_problem(problem_id: uuid.UUID):
    result = problem_queries.delete_problem(problem_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not delete problem with id {problem_id}"
        )
    blob_storage_helpers.delete_all_blobs(problem_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def create_problem(problem: CreateProblemDTO, current_user_id: uuid.UUID):
    if not problem_helpers.validate_problems(problem.test_files):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test files")
    problem_id = problem_queries.insert_problem(problem, current_user_id)
    if not problem_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not insert problem")
    for test_file in problem.test_files:
        data = test_file.file.read()
        blob_storage_helpers.upload_blob(f"{problem_id}/{test_file.filename}", data)
    return Response(status_code=status.HTTP_201_CREATED)


def modify_problem(problem_id: uuid.UUID, problem: ModifyProblemDTO):
    if len(problem.test_files) > 0:
        if not problem_helpers.validate_problems(problem.test_files):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test files")
        problem_helpers.modify_problem_in_blob_storage(problem_id, problem.test_files)
    problem_helpers.modify_problem_in_database(problem_id, problem)
    return Response(status_code=status.HTTP_200_OK)


def create_submission(current_user_id: uuid.UUID, submission: CreateSubmissionDTO):
    problem = problem_helpers.get_problem(submission.problem_id)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not found problem")
    if submission.competition_id:
        competition = competition_queries.get_competition(submission.competition_id)
        if not competition:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not found competition")
        if competition.start_time > datetime.now() or competition.end_time < datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition is not running")
        # if not problem_helpers.is_user_in_competition(current_user_id, competition):
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not in competition")
    submission_results = []
    for test_idx, test_dict in blob_storage_helpers.get_all_tests(submission.problem_id).items():
        result = submission_helpers.evaluate_problem_submission(
            submission.source_code, test_dict["in"], submission.language
        )

        if result["exception"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["exception"])

        result["stdout"] = blob_storage_helpers.remove_newline(result["stdout"])

        submission_results.append(
            {
                "execution_time": result["executionTime"],
                "output": result["stdout"],
                "expected_output": test_dict["out"],
            }
        )
    correct_submissions = len(
        [
            submission_result
            for submission_result in submission_results
            if submission_result["output"] == submission_result["expected_output"]
        ]
    )
    total_points = (correct_submissions / len(submission_results)) * problem.num_of_points
    total_runtime = sum([submission_result["execution_time"] for submission_result in submission_results])
    average_runtime = total_runtime / len(submission_results)
    is_correct = total_points == problem.num_of_points
    return problem_queries.insert_problem_result(
        submission.problem_id,
        submission.competition_id,
        current_user_id,
        average_runtime,
        is_correct,
        total_points,
        submission.source_code,
        submission.language,
    )


def get_submission(problem_id: uuid.UUID, user_id: uuid.UUID):
    return problem_queries.get_problem_result(problem_id, user_id)


def get_submission_on_competition(
    problem_id: uuid.UUID,
    user_id: uuid.UUID,
    competition_id: uuid.UUID,
):
    return problem_queries.get_problem_result(problem_id, user_id, competition_id)
