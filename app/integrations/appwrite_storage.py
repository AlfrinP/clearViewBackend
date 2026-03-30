from fastapi import Request
from appwrite.client import Client
from appwrite.id import ID
from appwrite.input_file import InputFile
from appwrite.services.storage import File, Storage

from app.core.config import (
    APPWRITE_API_KEY,
    APPWRITE_BUCKET_ID,
    APPWRITE_ENDPOINT,
    APPWRITE_PROJECT_ID,
)


def create_appwrite_storage() -> Storage:
    client = Client()
    (
        client.set_endpoint(APPWRITE_ENDPOINT)
        .set_project(APPWRITE_PROJECT_ID)
        .set_key(APPWRITE_API_KEY)
    )
    return Storage(client)


def ensure_appwrite_connection(storage: Storage) -> None:
    try:
        storage.get_bucket(bucket_id=APPWRITE_BUCKET_ID)
    except Exception as e:
        raise RuntimeError(
            "Appwrite connection check failed. Verify APPWRITE_ENDPOINT, "
            "APPWRITE_PROJECT_ID, APPWRITE_API_KEY, and APPWRITE_BUCKET_ID."
        ) from e


def upload_file_to_bucket(storage: Storage, file_bytes: bytes, filename: str) -> File:
    input_file = InputFile.from_bytes(file_bytes, filename=filename)
    create_file_result = storage.create_file(
        bucket_id=APPWRITE_BUCKET_ID,
        file_id=ID.unique(),
        file=input_file,
    )
    return create_file_result


def delete_file_from_bucket(storage: Storage, file_id: str) -> None:
    storage.delete_file(bucket_id=APPWRITE_BUCKET_ID, file_id=file_id)


def appwrite_storage_dependency(request: Request) -> Storage:
    return request.app.state.appwrite_storage
