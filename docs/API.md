# 🔌 API Reference

Base URL: `http://localhost:8000/v1`

## Authentication
All endpoints require a Bearer Token.
```bash
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Chat Completion (Governed)
**POST** `/chat/completions`
- **Input**: Standard OpenAI-compatible message format.
- **Features**: Triggers PII scan, RAG retrieval, and Audit logging.
- **Returns**: Streaming response + Governance Metadata.

### 2. Document Ingestion
**POST** `/documents`
- **Input**: `multipart/form-data` (PDF/TXT).
- **Process**: Chunks document and indexes into ChromaDB.

### 3. Governance Logs
**GET** `/audit/logs`
- **Query Params**: `limit`, `offset`.
- **Returns**: List of cryptographically signed audit entries.

### 4. Auth Token
**POST** `/auth/token`
- **Input**: `username`, `password`.
- **Returns**: JWT Access Token (30 min expiry).
