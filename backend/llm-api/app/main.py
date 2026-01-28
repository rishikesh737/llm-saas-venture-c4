from fastapi import FastAPI, Request, HTTPException, Depends
import httpx
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
OLLAMA_URL = "http://localhost:11434/api/generate"

app = FastAPI()

# --- simple in-memory rate limit ---
clients = {}


def authenticate(request: Request):
    key = request.headers.get("Authorization")
    if key != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")

    ip = request.client.host
    now = time.time()
    window = 60

    hits = [t for t in clients.get(ip, []) if now - t < window]
    if len(hits) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    hits.append(now)
    clients[ip] = hits


@app.post("/v1/completions")
async def completions(request: Request, _: None = Depends(authenticate)):
    payload = await request.json()

    prompt = payload.get("prompt")
    model = payload.get("model", "mistral:7b-instruct-q4_K_M")

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}
        )

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Ollama error")

    result = r.json()

    return {
        "id": "local-ollama",
        "object": "text_completion",
        "choices": [{"text": result.get("response", ""), "index": 0}],
    }
