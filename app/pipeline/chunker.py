"""Text chunking with metadata for policy documents."""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

DEFAULT_METADATA = {
    "source_type": "gov_policy",
    "department": "MVD",
    "country": "India",
    "trust_score": 0.99,
}


def chunk_documents(
    docs: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    metadata_override: dict | None = None,
) -> list[Document]:
    """Split documents into chunks and add metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)

    meta = {**DEFAULT_METADATA, **(metadata_override or {})}
    for c in chunks:
        c.metadata = {**c.metadata, **meta}

    return chunks
