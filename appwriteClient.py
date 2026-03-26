from appwrite.client import Client
from appwrite.id import ID
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage

from env import (
    APPWRITE_API_KEY,
    APPWRITE_BUCKET_ID,
    APPWRITE_ENDPOINT,
    APPWRITE_PROJECT_ID,
)

client = Client()
(
    client.set_endpoint(APPWRITE_ENDPOINT)
    .set_project(APPWRITE_PROJECT_ID)
    .set_key(APPWRITE_API_KEY)
)

bucket = Storage(client)


async def ensure_appwrite_connection() -> None:
    try:
        await bucket.get_bucket(bucket_id=APPWRITE_BUCKET_ID)
    except Exception as e:
        raise RuntimeError(
            "Appwrite connection check failed. Verify APPWRITE_ENDPOINT, "
            "APPWRITE_PROJECT_ID, APPWRITE_API_KEY, and APPWRITE_BUCKET_ID."
        ) from e
    print("Appwrite connection successful")


async def upload_file_to_bucket(file_bytes: bytes, filename: str) -> dict:
    input_file = InputFile.from_bytes(file_bytes, filename=filename)
    return await bucket.create_file(
        bucket_id=APPWRITE_BUCKET_ID,
        file_id=ID.unique(),
        file=input_file,
    )


async def delete_file_from_bucket(file_id: str) -> None:
    await bucket.delete_file(bucket_id=APPWRITE_BUCKET_ID, file_id=file_id)
