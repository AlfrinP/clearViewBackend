"""Document loaders for policy PDFs."""
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    """Load a PDF file and return document chunks."""
    loader = PyPDFLoader(file_path)
    return loader.load()


def load_documents_from_dir(documents_dir: str = "documents") -> list[Document]:
    """Load all PDFs from a directory."""
    path = Path(documents_dir)
    if not path.exists():
        return []

    docs: list[Document] = []
    for pdf_path in path.glob("*.pdf"):
        try:
            docs.extend(load_pdf(str(pdf_path)))
        except Exception:
            continue
    return docs
