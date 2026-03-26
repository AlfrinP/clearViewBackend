from __future__ import annotations

import datetime

from appwrite.services.storage import Storage
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pymongo.asynchronous.collection import AsyncCollection

from app.db.mongo import mongo_collection_dependency
from app.integrations.appwrite_storage import (
    appwrite_storage_dependency,
    delete_file_from_bucket,
    upload_file_to_bucket,
)
from app.schemas.files import (
    DeleteFileResponse,
    FileMetadataDTO,
    FilesPageResponse,
    UploadFileResponse,
)
from app.schemas.news import VerifyNewsRequest, VerifyNewsResponse, VerifyNewsResultDTO
from app.services.verification_service import verify_claim

router = APIRouter(prefix="/api/v1", tags=["clearview-api"])


@router.post("/verify-news", response_model=VerifyNewsResponse)
def verify_news(payload: VerifyNewsRequest) -> VerifyNewsResponse:
    try:
        final_state = verify_claim(payload.claim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    evaluation = final_state.get("evaluation") or {}
    result = final_state.get("result") or {}
    return VerifyNewsResponse(
        claim=payload.claim,
        evaluation=evaluation,
        result=VerifyNewsResultDTO(**result)
        if isinstance(result, dict)
        else VerifyNewsResultDTO(),
    )


@router.post("/upload-file", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_title: str = Form(...),
    collection: AsyncCollection = Depends(mongo_collection_dependency),
    storage: Storage = Depends(appwrite_storage_dependency),
) -> UploadFileResponse:
    try:
        file_content = await file.read()
        created_file = await upload_file_to_bucket(
            storage=storage,
            file_bytes=file_content,
            filename=file.filename or "uploaded_file",
        )
        created_file_id = created_file["$id"]
        now = datetime.datetime.now(datetime.timezone.utc)
        file_size = len(file_content)

        try:
            await collection.insert_one(
                {
                    "file_id": created_file_id,
                    "file_name": file.filename,
                    "file_title": file_title,
                    "file_size": file_size,
                    "uploaded_at": now,
                }
            )
        except Exception as mongo_error:
            try:
                await delete_file_from_bucket(storage=storage, file_id=created_file_id)
            except Exception as rollback_error:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Mongo insert failed and rollback failed. "
                        f"mongo_error={mongo_error}; rollback_error={rollback_error}"
                    ),
                )
            raise HTTPException(
                status_code=500,
                detail=f"Mongo insert failed. Uploaded file rollback succeeded. error={mongo_error}",
            )

        return UploadFileResponse(
            message="File uploaded successfully",
            file_title=file_title,
            file_size=file_size,
            file_created_at=now,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}", response_model=DeleteFileResponse)
async def delete_file(
    file_id: str,
    collection: AsyncCollection = Depends(mongo_collection_dependency),
    storage: Storage = Depends(appwrite_storage_dependency),
) -> DeleteFileResponse:
    metadata = await collection.find_one({"file_id": file_id})
    if metadata is None:
        raise HTTPException(status_code=404, detail="File metadata not found")

    try:
        delete_result = await collection.delete_one({"file_id": file_id})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="File metadata not found")

        try:
            await delete_file_from_bucket(storage=storage, file_id=file_id)
        except Exception as appwrite_error:
            await collection.insert_one(metadata)
            raise HTTPException(
                status_code=500,
                detail=(
                    "Appwrite file deletion failed; Mongo metadata rollback succeeded. "
                    f"error={appwrite_error}"
                ),
            )

        return DeleteFileResponse(message="File deleted successfully", file_id=file_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=FilesPageResponse)
async def get_files(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    collection: AsyncCollection = Depends(mongo_collection_dependency),
) -> FilesPageResponse:
    skip = (page - 1) * limit
    try:
        total = await collection.count_documents({})
        cursor = (
            collection.find(
                {},
                {
                    "_id": 0,
                    "file_id": 1,
                    "file_name": 1,
                    "file_title": 1,
                    "file_size": 1,
                    "uploaded_at": 1,
                },
            )
            .sort("uploaded_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        items = [FileMetadataDTO(**doc) for doc in docs]
        return FilesPageResponse(items=items, page=page, limit=limit, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

