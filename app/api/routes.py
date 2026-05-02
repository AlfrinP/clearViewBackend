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
    get_file_download_url,
    get_file_view_url,
    upload_file_to_bucket,
)
from app.schemas.files import (
    DeleteFileResponse,
    FileMetadataDTO,
    FilesPageResponse,
    UploadFileResponse,
)
from app.schemas.news import (
    ExternalSource,
    VerifyNewsEvaluationDTO,
    VerifyNewsRequest,
    VerifyNewsResponse,
    VerifyNewsResultDTO,
)
from app.services.verification_service import verify_claim
from langchain_community.document_loaders import PyPDFLoader

router = APIRouter(prefix="/api/v1", tags=["clearview-api"])


@router.post(
    "/verify-news",
    response_model=VerifyNewsResponse,
    summary="Verify a news claim against internal + external evidence",
    description=(
        "Runs the ClearView verification pipeline against the supplied claim.\n\n"
        "**Pipeline:**\n"
        "1. Retrieve relevant chunks from the internal vector store.\n"
        "2. Evaluate the claim strictly against that internal evidence.\n"
        "3. If internal evidence is insufficient, weak, or low-confidence, "
        "fall back to an external web search (Tavily).\n"
        "4. Synthesize a final, evidence-grounded verdict.\n\n"
        "When external search is used, the response includes the **metadata of "
        "each external source** (title, URL, description, relevance score, "
        "publication date) under `external_sources`. When the internal "
        "evidence was sufficient, `external_sources` is an empty list."
    ),
    responses={
        200: {
            "description": "Verification completed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "claim": "NASA confirmed liquid water on the surface of Mars in 2025.",
                        "evaluation": {
                            "verdict": "insufficient",
                            "confidence": 0.4,
                            "needs_external_search": True,
                            "evidence_strength": "weak",
                            "reason": "Internal documents do not directly address the claim.",
                        },
                        "result": {
                            "final_verdict": "Misleading",
                            "confidence": 0.66,
                            "justification": (
                                "External source [1] indicates NASA reported "
                                "subsurface water signatures, not confirmed "
                                "surface liquid water. The claim overstates "
                                "the announcement..."
                            ),
                            "sources_used": ["external"],
                        },
                        "external_sources": [
                            {
                                "title": "NASA Mars Exploration Program: 2025 Update",
                                "url": "https://mars.nasa.gov/news/2025-update",
                                "description": (
                                    "NASA scientists released a 2025 report "
                                    "summarising findings on subsurface water "
                                    "signatures observed by the Perseverance "
                                    "rover..."
                                ),
                                "score": 0.87,
                                "published_date": "2025-08-14",
                            }
                        ],
                    }
                }
            },
        },
        500: {"description": "Verification pipeline failed."},
    },
)
def verify_news(payload: VerifyNewsRequest) -> VerifyNewsResponse:
    try:
        final_state = verify_claim(payload.claim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    evaluation_data = final_state.get("evaluation") or {}
    result_data = final_state.get("result") or {}
    raw_external_sources = final_state.get("external_sources") or []

    external_sources = [
        ExternalSource(**src)
        for src in raw_external_sources
        if isinstance(src, dict)
    ]

    return VerifyNewsResponse(
        claim=payload.claim,
        evaluation=(
            VerifyNewsEvaluationDTO(**evaluation_data)
            if isinstance(evaluation_data, dict)
            else VerifyNewsEvaluationDTO()
        ),
        result=(
            VerifyNewsResultDTO(**result_data)
            if isinstance(result_data, dict)
            else VerifyNewsResultDTO()
        ),
        external_sources=external_sources,
    )


@router.post(
    "/upload-file",
    response_model=UploadFileResponse,
    summary="Upload a PDF file to the internal evidence store",
    description=(
        "Uploads a PDF, stores the binary in Appwrite, persists metadata in "
        "MongoDB, splits the document into chunks, and indexes the chunks "
        "into the vector store so they become available as internal evidence "
        "for `/verify-news`.\n\n"
        "The response includes a `view_url` (inline browser viewing) and a "
        "`download_url` for the uploaded file. Both URLs require the Appwrite "
        "bucket to allow read access."
    ),
)
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
        created_file = upload_file_to_bucket(
            storage=storage,
            file_bytes=file_content,
            filename=filename,
        )
        created_file_id = created_file.id
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
            file_id=created_file_id,
            file_title=file_title,
            file_size=file_size,
            file_created_at=now,
            view_url=get_file_view_url(created_file_id),
            download_url=get_file_download_url(created_file_id),
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


@router.delete(
    "/files/{file_id}",
    response_model=DeleteFileResponse,
    summary="Delete a file from Appwrite + MongoDB",
    description=(
        "Removes the file metadata from MongoDB and the binary from Appwrite. "
        "If Appwrite deletion fails, the MongoDB metadata is restored to keep "
        "the two stores consistent."
    ),
)
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


@router.get(
    "/files",
    response_model=FilesPageResponse,
    summary="List uploaded files (paginated)",
    description=(
        "Returns a paginated list of files that have been uploaded to the "
        "internal evidence store, sorted by upload time (newest first).\n\n"
        "Each item includes a `view_url` (inline browser viewing) and a "
        "`download_url` pointing at the file in Appwrite storage."
    ),
)
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
        items: list[FileMetadataDTO] = []
        for doc in docs:
            file_id_value = doc.get("file_id")
            items.append(
                FileMetadataDTO(
                    **doc,
                    view_url=(
                        get_file_view_url(file_id_value) if file_id_value else None
                    ),
                    download_url=(
                        get_file_download_url(file_id_value)
                        if file_id_value
                        else None
                    ),
                )
            )
        return FilesPageResponse(items=items, page=page, limit=limit, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
