import os
import requests


def evaluate_problem_submission(source_code: str, test_input: str, language: str):
    evaluator_api_url = "https://onecompiler-apis.p.rapidapi.com/api/v1/run"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.environ.get("RAPID_API_KEY"),
        "X-RapidAPI-Host": "onecompiler-apis.p.rapidapi.com",
    }
    payload = {
        "language": language,
        "stdin": test_input,
        "files": [{"name": "main.py", "content": source_code}],
    }
    response = requests.post(evaluator_api_url, headers=headers, json=payload)
    response_json = response.json()
    return response_json
