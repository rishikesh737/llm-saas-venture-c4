# 🛡️ Security & Governance Model

## 1. PII Detection Pipeline
Before any user prompt reaches the LLM, it passes through a cleaning layer (`services/pii_detection.py`).

- **Engine**: Microsoft Presidio + Custom Regex.
- **Entities Detected**:
  - Email Addresses
  - Phone Numbers
  - Credit Card Numbers
  - US SSN / Indian Aadhaar (Configurable)
- **Action**: High-risk prompts are blocked immediately (403 Forbidden).

## 2. Content Safety
Evaluates prompts for:
- Prompt Injection attacks ("Ignore previous instructions...")
- Toxicity and Hate Speech
- Jailbreak attempts

## 3. Cryptographic Audit Trail
We ensure non-repudiation of all AI interactions.

| Field | Description |
|-------|-------------|
| `request_id` | UUID v4 unique trace ID. |
| `log_hash` | SHA-256 hash of the payload + metadata. |
| `signature` | HMAC signature using a rotating secret. |
| `chain_hash` | Hash of the *previous* log entry (Blockchain-style linking). |

## 4. Infrastructure Isolation
- The **LLM Container** (Ollama) has NO internet access.
- It can only communicate with the Backend API via an internal Docker network.
- No user data ever leaves your controlled environment.
