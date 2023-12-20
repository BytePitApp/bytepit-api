import uuid

from typing import BinaryIO, Iterable


from fastapi import HTTPException
from fastapi.responses import StreamingResponse


from bytepit_api.database import blob_storage_container, blob_service_client


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
