from urllib.parse import quote, urlencode

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


def _build_appwrite_file_url(file_id: str, action: str) -> str:
    """Build a public Appwrite storage URL for a given file and action.

    `action` is one of: "view", "download", "preview".
    The bucket must allow read access for the URL to be usable without an
    additional session/JWT.
    """
    base = APPWRITE_ENDPOINT.rstrip("/")
    bucket = quote(APPWRITE_BUCKET_ID, safe="")
    safe_file_id = quote(file_id, safe="")
    query = urlencode({"project": APPWRITE_PROJECT_ID})
    return f"{base}/storage/buckets/{bucket}/files/{safe_file_id}/{action}?{query}"


def get_file_view_url(file_id: str) -> str:
    """Return the inline-view URL for a file stored in Appwrite."""
    return _build_appwrite_file_url(file_id, "view")


def get_file_download_url(file_id: str) -> str:
    """Return the download URL for a file stored in Appwrite."""
    return _build_appwrite_file_url(file_id, "download")


def appwrite_storage_dependency(request: Request) -> Storage:
    return request.app.state.appwrite_storage
