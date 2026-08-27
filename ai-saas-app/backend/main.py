from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from . import db
from .summarizer import summarize

app = FastAPI(title="Summarize-as-a-Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).parent.parent / "frontend"
if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.on_event("startup")
def _init():
    db.init()


class SignupIn(BaseModel):
    email: EmailStr


class SignupOut(BaseModel):
    email: str
    api_key: str


class SummarizeIn(BaseModel):
    text: str = Field(..., min_length=20)
    sentences: int = Field(5, ge=1, le=15)


class SummarizeOut(BaseModel):
    id: int
    summary: list[str]


def require_user(x_api_key: str | None = Header(default=None)):
    if not x_api_key:
        raise HTTPException(401, "Missing X-API-Key header")
    user = db.user_from_key(x_api_key)
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user


@app.get("/")
def index():
    idx = FRONTEND / "index.html"
    if idx.exists():
        return FileResponse(idx)
    return {"service": "Summarize-as-a-Service", "docs": "/docs"}


@app.post("/signup", response_model=SignupOut)
def signup(payload: SignupIn):
    try:
        _, key = db.create_user(payload.email)
    except Exception:
        raise HTTPException(400, "Email already registered")
    return SignupOut(email=payload.email, api_key=key)


@app.post("/summarize", response_model=SummarizeOut)
def do_summarize(payload: SummarizeIn, user=Depends(require_user)):
    result = summarize(payload.text, n=payload.sentences)
    joined = " ".join(result)
    sid = db.save_summary(user["id"], payload.text, joined)
    return SummarizeOut(id=sid, summary=result)


@app.get("/summaries")
def list_mine(user=Depends(require_user), limit: int = 20):
    rows = db.list_summaries(user["id"], limit=limit)
    return [{"id": r["id"], "summary": r["summary"], "created_at": r["created_at"]} for r in rows]


@app.get("/health")
def health():
    return {"ok": True}
