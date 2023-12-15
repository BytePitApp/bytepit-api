import uuid
from azure.storage.blob import BlobServiceClient
from os import getenv
from typing import BinaryIO, Iterable
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

def response_stream(data: Iterable[bytes], status: int = 200, download: bool = False)-> StreamingResponse:
    if download:
        return StreamingResponse(
            content=data, 
            status_code=status, 
            media_type="application/octet-stream"
        )
    else:
        return StreamingResponse(
            content=data,
            status_code=status,
        )

blob_service_client = BlobServiceClient.from_connection_string(
    getenv("BLOB_STORAGE_CONNECTION_STRING"),
)
container = getenv("BLOB_STORAGE_CONTAINER_NAME")

def upload_blob(filename: str, data: BinaryIO):
    try:
        blob_service_client \
            .get_blob_client(container=container, blob=filename) \
            .upload_blob(data)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_file_by_problem_id_and_file_name(filename: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=container, blob=filename)
        return response_stream(data=blob_client.download_blob().chunks(), download=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def download_blob(filename: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=container, blob=filename)
        return response_stream(data=blob_client.download_blob().chunks(), download=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_blob(filename: str):
    try:
        blob_service_client.get_blob_client(container=container, blob=filename).delete_blob()
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_blobs_by_problem_id(problem_id: uuid.UUID):
    try:
        files_to_delete = blob_service_client \
            .get_container_client(container=container) \
            .list_blobs(name_starts_with=f"{problem_id}")

        for file in files_to_delete:
            delete_blob(file.name)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
