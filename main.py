import json
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware

from crew import run_fake_news_pipeline

app = FastAPI(title="ClearView Fake News API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyNewsRequest(BaseModel):
    news: str = Field(..., min_length=1, description="News text to verify.")


class VerifyNewsResponse(BaseModel):
    classification: str
    confidence: float
    reasoning: str
    rag_evidence: list
    web_sources: list


@app.on_event("startup")
def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/verify-new", response_model=VerifyNewsResponse)
def verify_new(payload: VerifyNewsRequest) -> dict:
    news_text = payload.news.strip()
    if not news_text:
        raise HTTPException(status_code=400, detail="news must not be empty")

    try:
        result = run_fake_news_pipeline(news_text)
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return json.loads(json.dumps(result))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
