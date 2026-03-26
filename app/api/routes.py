from __future__ import annotations

import datetime
import os
import tempfile

from appwrite.services.storage import Storage
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo.asynchronous.collection import AsyncCollection

from app.ai.retrieval import get_vector_store
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
from langchain_community.document_loaders import PyPDFLoader

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
        result=(
            VerifyNewsResultDTO(**result)
            if isinstance(result, dict)
            else VerifyNewsResultDTO()
        ),
    )


@router.post("/upload-file", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_title: str = Form(...),
    collection: AsyncCollection = Depends(mongo_collection_dependency),
    storage: Storage = Depends(appwrite_storage_dependency),
) -> UploadFileResponse:
    created_file_id: str | None = None
    metadata_doc_id = None
    temp_path: str | None = None
    try:
        filename = file.filename or "uploaded_file"
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Only PDF uploads are supported"
            )

        file_content = await file.read()
        created_file = await upload_file_to_bucket(
            storage=storage,
            file_bytes=file_content,
            filename=filename,
        )
        created_file_id = created_file["$id"]
        now = datetime.datetime.now(datetime.timezone.utc)
        file_size = len(file_content)

        insert_result = await collection.insert_one(
            {
                "record_type": "file_upload",
                "status": "processing",
                "file_id": created_file_id,
                "file_name": filename,
                "file_title": file_title,
                "file_size": file_size,
                "uploaded_at": now,
            }
        )
        metadata_doc_id = insert_result.inserted_id

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            temp_path = tmp.name

        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        processed_chunks = [
            Document(
                page_content=chunk.page_content,
                metadata={
                    **chunk.metadata,
                    "doc_id": str(metadata_doc_id),
                    "file_id": created_file_id,
                    "source": "user_upload",
                    "file_title": file_title,
                },
            )
            for chunk in chunks
        ]

        vector_store = get_vector_store()
        vector_store.add_documents(processed_chunks)

        await collection.update_one(
            {"_id": metadata_doc_id},
            {
                "$set": {
                    "status": "ready",
                    "chunk_count": len(processed_chunks),
                    "processed_at": datetime.datetime.now(datetime.timezone.utc),
                }
            },
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
        if metadata_doc_id is not None:
            await collection.update_one(
                {"_id": metadata_doc_id},
                {"$set": {"status": "failed", "error": str(e)}},
            )
        if created_file_id is not None:
            try:
                await delete_file_from_bucket(storage=storage, file_id=created_file_id)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.delete("/files/{file_id}", response_model=DeleteFileResponse)
async def delete_file(
    file_id: str,
    collection: AsyncCollection = Depends(mongo_collection_dependency),
    storage: Storage = Depends(appwrite_storage_dependency),
) -> DeleteFileResponse:
    metadata = await collection.find_one(
        {"file_id": file_id, "record_type": "file_upload"}
    )
    if metadata is None:
        raise HTTPException(status_code=404, detail="File metadata not found")

    try:
        delete_result = await collection.delete_one(
            {"file_id": file_id, "record_type": "file_upload"}
        )
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
        filter_query = {"record_type": "file_upload"}
        total = await collection.count_documents(filter_query)
        cursor = (
            collection.find(
                filter_query,
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
