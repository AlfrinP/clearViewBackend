import datetime

from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    message: str
    file_title: str
    file_size: int
    file_created_at: datetime.datetime


class DeleteFileResponse(BaseModel):
    message: str
    file_id: str


class FileMetadataDTO(BaseModel):
    file_id: str
    file_name: str | None = None
    file_title: str | None = None
    file_size: int | None = None
    uploaded_at: datetime.datetime | None = None


class FilesPageResponse(BaseModel):
    items: list[FileMetadataDTO]
    page: int
    limit: int
    total: int

