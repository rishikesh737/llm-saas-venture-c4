from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
import time
import asyncio
import hashlib
import uuid
import structlog
import tiktoken  # <--- New Import
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.models import AuditLog

load_dotenv()

# ---- Logging Setup ----
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger()

# ---- Config ----
API_KEYS = set(filter(None, os.getenv("API_KEYS", "").split(",")))
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
OLLAMA_BASE_URL = "http://ollama:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
ALLOWED_MODELS = {"mistral:7b-instruct-q4_K_M", "tinyllama"}

# Initialize Tokenizer (cl100k_base is used by GPT-4/3.5, good proxy for Mistral)
try:
    encoding = tiktoken.get_encoding("cl100k_base")
except Exception:
    encoding = tiktoken.get_encoding("gpt2")  # Fallback


# ---- App Lifecycle ----
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Local LLM Gateway",
    description="Enterprise-grade AI Gateway with strict governance.",
    version="2.1.0-beta",  # Bumped for Token Accounting
    lifespan=lifespan,
)

# ---- State ----
clients = {}
semaphore = asyncio.Semaphore(1)
security_scheme = HTTPBearer()


# ---- Helpers ----
def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:8]


def count_tokens(text: str) -> int:
    """Estimate token count for a string."""
    try:
        return len(encoding.encode(text))
    except Exception:
        return 0


# ---- Middleware ----
@app.middleware("http")
async def add_request_id_and_audit(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---- Auth ----
def authenticate(creds: HTTPAuthorizationCredentials = Depends(security_scheme)):
    key = creds.credentials.strip()
    if key not in API_KEYS:
        log.warning("auth_failed", reason="invalid_key")
        raise HTTPException(status_code=403, detail="Invalid API key")

    now = time.time()
    key_hash = hash_key(key)

    hits = clients.get(key_hash, [])
    hits = [t for t in hits if now - t < 60]
    if len(hits) >= RATE_LIMIT:
        log.warning("rate_limit_exceeded", client_id=key_hash)
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    hits.append(now)
    clients[key_hash] = hits
    return {"user_hash": key_hash}


# ---- Models ----
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]


class LogEntry(BaseModel):
    request_id: str
    timestamp: float
    user_hash: str
    model: str
    status_code: int
    latency_ms: float
    # New Fields
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    class Config:
        from_attributes = True


# ---- Endpoints ----
@app.get("/health/live", tags=["Health"])
async def health_live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def health_ready():
    return {"status": "ready"}


@app.get("/v1/audit/logs", response_model=List[LogEntry], tags=["Governance"])
async def get_audit_logs(
    limit: int = 50,
    auth_ctx: dict = Depends(authenticate),
    db: Session = Depends(get_db),
):
    """Fetch the latest audit logs for governance review."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs


@app.post("/v1/chat/completions", tags=["Inference"])
async def chat_completions(
    request: Request,
    body: ChatRequest,
    background_tasks: BackgroundTasks,
    auth_ctx: dict = Depends(authenticate),
    db: Session = Depends(get_db),
):
    request_id = request.state.request_id
    start_time = time.time()

    if body.model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail="Model not allowed")

    # 1. Calculate Prompt Tokens
    prompt_text = "".join([m.content for m in body.messages])
    p_tokens = count_tokens(prompt_text)

    log.info(
        "chat_request",
        user=auth_ctx["user_hash"],
        model=body.model,
        prompt_tokens=p_tokens,
    )

    status_code = 200
    c_tokens = 0
    content = ""

    try:
        async with semaphore:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    OLLAMA_CHAT_URL,
                    json={
                        "model": body.model,
                        "messages": [
                            {"role": m.role, "content": m.content}
                            for m in body.messages
                        ],
                        "stream": False,
                    },
                )
        if r.status_code != 200:
            status_code = 502
            raise HTTPException(status_code=502, detail="Ollama failed")

        result = r.json()
        content = result.get("message", {}).get("content", "")

        # 2. Calculate Completion Tokens
        c_tokens = count_tokens(content)

    except Exception as e:
        status_code = 500
        log.error("inference_failed", error=str(e))
        raise e
    finally:
        latency = (time.time() - start_time) * 1000

        # 3. Save to DB with Token Counts
        audit_entry = AuditLog(
            request_id=request_id,
            user_hash=auth_ctx["user_hash"],
            model=body.model,
            endpoint="/v1/chat/completions",
            status_code=status_code,
            latency_ms=latency,
            prompt_tokens=p_tokens,  # Saved
            completion_tokens=c_tokens,  # Saved
            total_tokens=p_tokens + c_tokens,
        )
        db.add(audit_entry)
        db.commit()

        log.info(
            "audit_log_persisted",
            request_id=request_id,
            latency_ms=latency,
            total_tokens=p_tokens + c_tokens,
        )

    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.model,
        "usage": {
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": p_tokens + c_tokens,
        },
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }
