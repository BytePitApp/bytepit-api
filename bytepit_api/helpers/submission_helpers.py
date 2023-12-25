import os
import requests

from bytepit_api.models.dtos import Language


def evaluate_problem_submission(source_code: str, test_input: str, language: str):
    languages = {
        Language.python: "main.py",
        Language.c: "main.c",
        Language.cpp: "main.cpp",
        Language.node: "main.js",
        Language.javascript: "main.js",
        Language.java: "Main.java",
    }
    evaluator_api_url = "https://onecompiler-apis.p.rapidapi.com/api/v1/run"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.environ.get("RAPID_API_KEY"),
        "X-RapidAPI-Host": "onecompiler-apis.p.rapidapi.com",
    }
    payload = {
        "language": language,
        "stdin": test_input,
        "files": [{"name": languages[language], "content": source_code}],
    }
    response = requests.post(evaluator_api_url, headers=headers, json=payload)
    response_json = response.json()
    return response_json
