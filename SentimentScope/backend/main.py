"""
main.py — SentimentScope FastAPI backend
Endpoints:
  POST /analyse        – single text
  POST /analyse/batch  – list of texts
  GET  /health         – liveness check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, conlist
from typing import Annotated
from pathlib import Path
from model import analyse_text, analyse_batch

# Path to the frontend folder (one level up from backend/)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(
    title="SentimentScope API",
    description="Social-media sentiment & emotion analysis powered by HuggingFace Transformers.",
    version="1.0.0",
)

# ── CORS (allow the frontend served from any local origin) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────

class SingleRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000,
                      example="I absolutely love this product! It changed my life.")

class BatchRequest(BaseModel):
    texts: Annotated[list[str], Field(min_length=1, max_length=50)] = Field(
        ..., example=["I'm so happy today!", "This is terrible."])


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health():
    return {"status": "ok", "service": "SentimentScope"}


@app.post("/analyse", tags=["Analysis"])
def analyse_single(req: SingleRequest):
    """Analyse a single text for sentiment and emotions."""
    result = analyse_text(req.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/analyse/batch", tags=["Analysis"])
def analyse_batch_endpoint(req: BatchRequest):
    """Analyse up to 50 texts in one request."""
    results = analyse_batch(req.texts)
    return {"count": len(results), "results": results}


# ── Serve frontend (must be LAST — after all API routes) ─────────────────────
# StaticFiles with html=True serves index.html at / and all assets at their
# original relative paths (/style.css, /app.js etc.)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
