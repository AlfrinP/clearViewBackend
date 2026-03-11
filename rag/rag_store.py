from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models import embeddings


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_documents() -> list[Document]:
    if not DATA_DIR.exists():
        return [
            Document(
                page_content=(
                    "No dataset found in data/ directory. Add source files to "
                    "improve retrieval quality."
                ),
                metadata={"source": "system"},
            )
        ]

    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="**/*",
        show_progress=False,
        use_multithreading=True,
        loader_cls=TextLoader,
        silent_errors=True,
    )
    docs = loader.load()
    if docs:
        return docs

    return [
        Document(
            page_content=(
                "Dataset directory is empty. Add documents under data/ for RAG."
            ),
            metadata={"source": "system"},
        )
    ]


def _build_vectorstore() -> FAISS:
    docs = _load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    return FAISS.from_documents(split_docs, embeddings)


vectorstore = _build_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
