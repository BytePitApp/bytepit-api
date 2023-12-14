import uuid
from azure.storage.blob import BlobServiceClient, ContainerClient
from os import getenv
from typing import BinaryIO
from fastapi import HTTPException
from bytepit_api.helpers.response_stream import response_stream
from typing import Union

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

def get_blob(filename: str):
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


def delete_all_blobs_by_id(problemId: Union[int, uuid.UUID]):
    try:
        files_to_delete = blob_service_client \
            .get_container_client(container=container) \
            .list_blobs(name_starts_with=f"{problemId}")

        for file in files_to_delete:
            delete_blob(file.name)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
