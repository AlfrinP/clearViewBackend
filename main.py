from __future__ import annotations

from fastapi import FastAPI

from routes import router

app = FastAPI(title="ClearView Backend", version="2.0")
app.include_router(router)
