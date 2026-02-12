# 🏗️ System Architecture

## High-Level Data Flow

```mermaid
graph LR
    User[User Browser] -->|HTTPS| NextJS[Next.js Frontend]
    NextJS -->|JSON| API[FastAPI Gateway]
    
    subgraph "Secure Enclave"
        API -->|1. Intercept| Sec[Security Middleware]
        Sec -->|2. Scan PII| PII[Presidio Engine]
        Sec -->|3. Check Safety| Guard[Content Guard]
    end
    
    API -->|4. Retrieve| Vector[ChromaDB]
    API -->|5. Inference| Ollama[Ollama / Mistral 7B]
    
    API -->|6. Log| DB[(PostgreSQL Audit Log)]
```

## Key Components

### 1. The Gateway (FastAPI)
The central nervous system. It handles:
- **Authentication**: JWT validation via `auth/security.py`.
- **Rate Limiting**: Token bucket algorithm via `SlowAPI`.
- **Orchestration**: Manages the flow between Security, RAG, and LLM services.

### 2. The Memory (RAG Pipeline)
Located in `services/rag.py`.
- **Ingestion**: pdf -> text -> chunks (512 tokens) -> embeddings.
- **Retrieval**: Semantic search using Cosine Similarity.
- **Storage**: ChromaDB (persistent local vector store).

### 3. The Audit Chain (Immutable Logs)
Located in `services/audit.py`.
- Every request is hashed (`SHA-256`) and signed (`HMAC`).
- Logs are stored in PostgreSQL with a unique constraint on the hash.
- This creates a tamper-evident chain of custody for compliance.
