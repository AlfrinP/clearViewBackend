"""Ingestion API routes."""
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.auth.jwt import User, get_current_active_user
from app.core.schemas import IngestRequest, IngestResponse
from app.pipeline.ingest import run_ingestion

router = APIRouter(prefix="/api/v1", tags=["ingest"])

_ingest_status: dict = {"last_run": None, "documents_ingested": 0, "message": ""}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    req: IngestRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> IngestResponse:
    """
    Ingest policy documents. Provide file_path in JSON body.
    Example: {"file_path": "documents/demo.pdf"}
    """
    try:
        count, msg = run_ingestion(file_path=req.file_path)
        _ingest_status["last_run"] = "success"
        _ingest_status["documents_ingested"] = count
        _ingest_status["message"] = msg
        return IngestResponse(
            status="success",
            documents_ingested=count,
            message=msg,
        )
    except Exception as e:
        _ingest_status["last_run"] = "error"
        _ingest_status["message"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    _: Annotated[User, Depends(get_current_active_user)] = None,
) -> IngestResponse:
    """Upload and ingest a PDF file."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF file required")
    from pathlib import Path
    import tempfile
    import shutil
    upload_dir = Path("documents")
    upload_dir.mkdir(exist_ok=True)
    dest = upload_dir / file.filename
    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        count, msg = run_ingestion(file_path=str(dest))
        _ingest_status["last_run"] = "success"
        _ingest_status["documents_ingested"] = count
        _ingest_status["message"] = msg
        return IngestResponse(status="success", documents_ingested=count, message=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/status")
async def ingest_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """Get last ingestion job status."""
    return _ingest_status
