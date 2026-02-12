# 🚀 Deployment Guide

## Local Development (Docker Compose)

The easiest way to run Sābhya AI is using the included shell script.

### Prerequisites
- Docker Engine 24+
- Docker Compose v2+
- 8GB+ RAM (for Mistral 7B)

### Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/rishikesh737/llm-saas-venture-c4.git
   cd llm-saas-venture-c4
   ```

2. **Start the stack**
   ```bash
   chmod +x start-sabhya.sh
   ./start-sabhya.sh
   ```

3. **Verify Installation**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Production Deployment (Kubernetes)

For scalable production environments, use the manifests in `infra/k8s/`.

### 1. Secrets Management
Copy the example secret file and fill in your production values.
```bash
cp infra/k8s/secrets.example.yaml infra/k8s/secrets.yaml
# Edit secrets.yaml with real passwords
```

### 2. Deploy to Cluster
```bash
kubectl apply -f infra/k8s/secrets.yaml
kubectl apply -f infra/k8s/pvc.yaml
kubectl apply -f infra/k8s/ollama-init.yaml
kubectl apply -f infra/k8s/llm-stack.yaml
```

### 3. Verification
Check that the pod is running and the service is exposed.
```bash
kubectl get pods -l app=sabhya-stack
```
