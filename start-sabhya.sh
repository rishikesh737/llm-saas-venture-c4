#!/bin/bash
echo "🚀 Starting Sabhya AI Stack..."

# 1. Define Paths
BASE_DIR="/mnt/fedora-partition/llm-saas-venture/backend/llm-api"
FRONTEND_DIR="/mnt/fedora-partition/llm-saas-venture/frontend"

# 2. Start Containers (The new "Sabhya" names)
# We use 'podman start' to resume the existing containers we just created
# 2. Start Containers
# Resume DB and Ollama
podman start sabhya-db ollama

# Always run API with explicit config to ensure latest image and env vars are used
echo "🚀 Launching API Container..."
podman run -d --name llm-api --network host --replace \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e API_KEYS=dev-key-1 \
  -e DATABASE_URL=postgresql://sabhya:***REMOVED***@localhost:5432/sabhya_db \
  -e "CORS_ORIGINS=*" \
  localhost/llm-api:stable

# 3. Check for errors
if [ $? -ne 0 ]; then
    echo "⚠️ Containers not found. Please run 'rebrand_stack.sh' first to initialize."
    exit 1
fi

echo "✅ Backend Services Up!"
echo "   - API: http://localhost:8000"
echo "   - DB:  Postgres:5432 (sabhya_db)"
echo "   - AI:  Ollama:11434"

# 4. Start Frontend
echo "🖥️ Starting Frontend..."
cd $FRONTEND_DIR
npm run dev
