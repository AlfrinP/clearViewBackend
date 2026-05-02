import datetime

from pydantic import BaseModel, ConfigDict, Field


class UploadFileResponse(BaseModel):
    message: str = Field(
        description="Human-readable status message.",
        examples=["File uploaded successfully"],
    )
    file_id: str = Field(
        description="Appwrite file id assigned to the uploaded file.",
        examples=["66f1c0d7e3b8a1f2c4d5"],
    )
    file_title: str = Field(
        description="Title supplied by the user when uploading the file.",
        examples=["NASA Mars 2025 Report"],
    )
    file_size: int = Field(
        description="Size of the uploaded file in bytes.",
        examples=[284_512],
    )
    file_created_at: datetime.datetime = Field(
        description="UTC timestamp when the file was uploaded.",
    )
    view_url: str = Field(
        description=(
            "Public Appwrite URL that renders the file inline in the browser. "
            "Requires the bucket to allow read access."
        ),
        examples=[
            "https://cloud.appwrite.io/v1/storage/buckets/documents/files/"
            "66f1c0d7e3b8a1f2c4d5/view?project=clearview"
        ],
    )
    download_url: str = Field(
        description="Public Appwrite URL that triggers a file download.",
        examples=[
            "https://cloud.appwrite.io/v1/storage/buckets/documents/files/"
            "66f1c0d7e3b8a1f2c4d5/download?project=clearview"
        ],
    )


class DeleteFileResponse(BaseModel):
    message: str = Field(
        description="Human-readable status message.",
        examples=["File deleted successfully"],
    )
    file_id: str = Field(
        description="Appwrite file id of the deleted file.",
        examples=["66f1c0d7e3b8a1f2c4d5"],
    )


class FileMetadataDTO(BaseModel):
    """Metadata for a single uploaded file."""

    file_id: str = Field(
        description="Appwrite file id.",
        examples=["66f1c0d7e3b8a1f2c4d5"],
    )
    file_name: str | None = Field(
        default=None,
        description="Original filename as uploaded by the user.",
        examples=["mars-2025-report.pdf"],
    )
    file_title: str | None = Field(
        default=None,
        description="Title supplied by the user when uploading the file.",
        examples=["NASA Mars 2025 Report"],
    )
    file_size: int | None = Field(
        default=None,
        description="Size of the file in bytes.",
        examples=[284_512],
    )
    uploaded_at: datetime.datetime | None = Field(
        default=None,
        description="UTC timestamp when the file was uploaded.",
    )
    view_url: str | None = Field(
        default=None,
        description=(
            "Public Appwrite URL that renders the file inline in the browser."
        ),
        examples=[
            "https://cloud.appwrite.io/v1/storage/buckets/documents/files/"
            "66f1c0d7e3b8a1f2c4d5/view?project=clearview"
        ],
    )
    download_url: str | None = Field(
        default=None,
        description="Public Appwrite URL that triggers a file download.",
        examples=[
            "https://cloud.appwrite.io/v1/storage/buckets/documents/files/"
            "66f1c0d7e3b8a1f2c4d5/download?project=clearview"
        ],
    )


class FilesPageResponse(BaseModel):
    items: list[FileMetadataDTO] = Field(
        description="Page of file metadata items, sorted by upload time descending.",
    )
    page: int = Field(description="1-based page number.", examples=[1])
    limit: int = Field(description="Page size.", examples=[10])
    total: int = Field(
        description="Total number of files available across all pages.",
        examples=[42],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "file_id": "66f1c0d7e3b8a1f2c4d5",
                        "file_name": "mars-2025-report.pdf",
                        "file_title": "NASA Mars 2025 Report",
                        "file_size": 284_512,
                        "uploaded_at": "2025-08-14T10:23:45+00:00",
                        "view_url": (
                            "https://cloud.appwrite.io/v1/storage/buckets/"
                            "documents/files/66f1c0d7e3b8a1f2c4d5/view?"
                            "project=clearview"
                        ),
                        "download_url": (
                            "https://cloud.appwrite.io/v1/storage/buckets/"
                            "documents/files/66f1c0d7e3b8a1f2c4d5/download?"
                            "project=clearview"
                        ),
                    }
                ],
                "page": 1,
                "limit": 10,
                "total": 42,
            }
        }
    )
