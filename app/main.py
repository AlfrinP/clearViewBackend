"""FastAPI application entry point."""
from fastapi import FastAPI, Request

from app.api.routes import verification, ingest, health
from app.rule_engine.decision_engine import decision_engine

app = FastAPI(title="Fake News Verification API", version="1.0.0")

app.include_router(verification.router)
app.include_router(ingest.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"message": "Fake News Verification API", "docs": "/docs"}


@app.post("/verify-news")
async def verify_news_legacy(request: Request):
    """Legacy endpoint: accepts {"news": "..."} and returns VerificationResponse."""
    data = await request.json()
    news = data.get("news") or data.get("claim", "")
    if not news:
        return {"response": "Error: provide 'news' or 'claim' in request body"}
    result = await decision_engine(news)
    return {"response": result.reasoning, "verification": result.model_dump()}
