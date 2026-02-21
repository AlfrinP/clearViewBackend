"""Policy document ingestion entry point."""
from pathlib import Path

from app.pipeline.chunker import chunk_documents
from app.pipeline.loader import load_pdf
from app.pipeline.vector_store import vector_store


def run_ingestion(file_path: str | None = None, documents_dir: str | None = None) -> tuple[int, str]:
    """
    Ingest policy documents into the vector store.
    Either file_path (single file) or documents_dir can be provided.
    Returns (documents_ingested, message).
    """
    docs = []

    if file_path:
        path = Path(file_path)
        if not path.exists():
            return 0, f"File not found: {file_path}"
        try:
            docs = load_pdf(str(path))
        except Exception as e:
            return 0, f"Failed to load {file_path}: {e}"
    elif documents_dir:
        from app.pipeline.loader import load_documents_from_dir
        docs = load_documents_from_dir(documents_dir)
    else:
        return 0, "Provide file_path or documents_dir"

    if not docs:
        return 0, "No documents to ingest"

    chunks = chunk_documents(docs)
    vector_store.add_documents(chunks)
    return len(chunks), f"Ingested {len(chunks)} chunks from {len(docs)} pages"
