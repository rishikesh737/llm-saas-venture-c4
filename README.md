# 🛡️ SĀBHYA AI - Governance Gateway

> **A Secure, Governed AI Platform for Regulated Industries**
>
> _Built with Next.js 14, FastAPI, ChromaDB, and Ollama._

---

## 🚀 Features

- **🧠 Governed Inference**: Real-time PII detection and content safety checks before the LLM sees data.
- **📚 RAG Pipeline**: Secure document ingestion (PDF) with vector search (ChromaDB).
- **📝 Immutable Audit Logs**: Blockchain-style SHA-256 hashing for every request/response.
- **🔐 RBAC Authentication**: JWT-based access control with Admin/User roles.
- **⚡ Reactive UI**: Modern Next.js dashboard with "Thinking Process" visualization.

---

## 🏗️ Architecture

### Data Flow
`User → Next.js UI → FastAPI Gateway → (Security Layer) → Vector DB / LLM → Audit Log`

### Tech Stack
| Component | Technology | Role |
|-----------|------------|------|
| **Frontend** | Next.js 14, TypeScript, Tailwind | Dashboard & Chat UI |
| **Backend** | FastAPI, Python 3.11 | API Gateway, Logic |
| **AI Engine** | Ollama (Mistral 7B) | Local Inference |
| **Memory** | ChromaDB | Vector Search (RAG) |
| **Database** | PostgreSQL 15 | Immutable Logs |
| **Security** | Presidio, Microsoft NLP | PII Detection |

---

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)

### 1. Start the Stack
We provide a single script to orchestrate the entire container stack.

```bash
chmod +x start-sabhya.sh
./start-sabhya.sh
```

This will:
1. Build the Backend & Frontend images.
2. Start PostgreSQL, ChromaDB, and Ollama.
3. Launch the API (Port 8000) and UI (Port 3000).

### 2. Access the Dashboard
Open **[http://localhost:3000](http://localhost:3000)**
- **Login**: `rishikesh@sabhya.ai`
- **Password**: `mypassword123`

---

## 📁 Directory Structure

```
llm-saas-venture/
├── backend/
│   └── llm-api/        # FastAPI Application
│       ├── app/services/   # RAG, Audit, PII Logic
│       └── app/routes/     # API Endpoints
├── frontend/           # Next.js Application
│   ├── components/     # InteractionPanel, GovernanceLogs
│   └── app/            # Pages & Layouts
├── infra/              # Kubernetes & Docker Configs
└── docs/               # System Documentation
```

---

## 🛡️ Security Model

1.  **PII Stripping**: All prompts are scanned for emails, phones, and credit cards. High-risk prompts are blocked.
2.  **Audit Trail**: Every interaction is logged with a cryptographic signature (`HMAC-SHA256`).
3.  **Isolation**: The LLM runs in a separate container and never accesses the internet directly.

---

## 📜 License
MIT License. See [LICENSE](./LICENSE) for details.
