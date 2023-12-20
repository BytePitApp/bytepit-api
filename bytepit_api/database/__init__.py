import os

from azure.storage.blob import BlobServiceClient

from bytepit_api.database.database import Database

db = Database(os.environ["DB_CONNECTION_STRING"])

blob_service_client = BlobServiceClient.from_connection_string(
    os.environ.get("BLOB_STORAGE_CONNECTION_STRING"),
)

blob_storage_container = os.environ.get("BLOB_STORAGE_CONTAINER_NAME")
