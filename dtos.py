from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field


class VerifyNewsRequest(BaseModel):
    claim: str = Field(min_length=1, description="The claim to verify")


class VerifyNewsResultDTO(BaseModel):
    final_verdict: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    justification: str | None = None
    sources_used: list[str] = Field(default_factory=list)


class VerifyNewsResponse(BaseModel):
    claim: str
    evaluation: dict[str, Any] = Field(default_factory=dict)
    result: VerifyNewsResultDTO = Field(default_factory=VerifyNewsResultDTO)


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
