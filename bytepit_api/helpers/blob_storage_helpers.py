import uuid

from typing import BinaryIO, Iterable


from fastapi import HTTPException
from fastapi.responses import StreamingResponse


from bytepit_api.database import blob_storage_container, blob_service_client


def remove_trailing_newline(string: str):
    if string[-1] == "\n":
        return string[:-1]
    return string


def response_stream(data: Iterable[bytes], status: int = 200, download: bool = False) -> StreamingResponse:
    if download:
        return StreamingResponse(content=data, status_code=status, media_type="application/octet-stream")
    else:
        return StreamingResponse(
            content=data,
            status_code=status,
        )


def upload_blob(filename: str, data: BinaryIO):
    try:
        blob_service_client.get_blob_client(container=blob_storage_container, blob=filename).upload_blob(data)
        return {"message": "File uploaded successfully in blob storage"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_blob(fullpath: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=blob_storage_container, blob=fullpath)
        return response_stream(data=blob_client.download_blob().chunks(), download=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def blob_to_text(fullpath: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=blob_storage_container, blob=fullpath)
        return blob_client.download_blob(max_concurrency=1, encoding="UTF-8").readall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def download_blob(filename: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=blob_storage_container, blob=filename)
        return response_stream(data=blob_client.download_blob().chunks(), download=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_blob(filename: str):
    try:
        blob_service_client.get_blob_client(container=blob_storage_container, blob=filename).delete_blob()
        return {"message": "File deleted successfully in blob storage"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_blobs(problem_id: uuid.UUID):
    try:
        files_to_delete = blob_service_client.get_container_client(container=blob_storage_container).list_blobs(
            name_starts_with=f"{problem_id}"
        )
        for file in files_to_delete:
            delete_blob(file.name)
        return {"message": "Files deleted successfully in blob storage"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_all_tests(problem_id: uuid.UUID):
    try:
        all_tests = blob_service_client.get_container_client(container=blob_storage_container).list_blobs(
            name_starts_with=f"{problem_id}"
        )
        tests = {}
        for test in all_tests:
            test_file = blob_to_text(test.name)
            test_idx = test.name.split("/")[1].split("_")[0]
            if test.name.endswith("in.txt"):
                tests[test_idx] = {"in": test_file}
            else:
                tests[test_idx]["out"] = test_file
                tests[test_idx]["out"] = remove_trailing_newline(tests[test_idx]["out"])
        return tests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
