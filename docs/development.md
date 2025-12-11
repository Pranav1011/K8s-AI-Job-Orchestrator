# Development Guide

This guide covers setting up a local development environment for the K8s AI Job Orchestrator.

## Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Go | 1.21+ | [golang.org/dl](https://golang.org/dl/) |
| Python | 3.11+ | [python.org](https://www.python.org/) |
| Docker | 24+ | [docker.com](https://www.docker.com/) |
| Kind | 0.20+ | `go install sigs.k8s.io/kind@latest` |
| kubectl | 1.25+ | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.0+ | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Pranav1011/K8s-AI-Job-Orchestrator.git
cd K8s-AI-Job-Orchestrator

# Setup local Kind cluster with dependencies
make dev-setup

# Start all services
make dev-run
```

## Environment Setup

### 1. Install Dependencies

**Go (Controller):**

```bash
cd controller
go mod download
```

**Python (Job Service & Workers):**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r job-service/requirements.txt
pip install -r worker/requirements.txt

# Install dev tools
pip install black isort mypy pytest pytest-asyncio
```

### 2. Setup Local Kubernetes Cluster

```bash
./scripts/setup-kind.sh
kubectl cluster-info
```

### 3. Start Dependencies

```bash
docker-compose up -d redis postgres
```

### 4. Apply CRDs

```bash
kubectl apply -f controller/config/crd/bases/
```

## Running Services Locally

### Job Service (FastAPI)

```bash
cd job-service
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/aijobs"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="dev-secret-key"

uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Controller

```bash
cd controller
go run cmd/controller/main.go --leader-elect=false
```

### Workers

```bash
cd worker
export REDIS_URL="redis://localhost:6379"
python inference_worker.py
```

## Testing

### Python Tests

```bash
cd job-service
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=html
```

### Go Tests

```bash
cd controller
go test ./... -v
go test ./... -v -coverprofile=coverage.out
```

## Code Quality

### Python

```bash
black app/ tests/
isort app/ tests/
mypy app/
```

### Go

```bash
go fmt ./...
golangci-lint run
```

## Building Docker Images

```bash
make docker-build

# Load into Kind
kind load docker-image ai-job-controller:dev
kind load docker-image ai-job-service:dev
kind load docker-image ai-job-worker:dev
```

## Makefile Reference

| Command | Description |
|---------|-------------|
| `make dev-setup` | Setup local Kind cluster |
| `make dev-run` | Start all services locally |
| `make test` | Run all tests |
| `make lint` | Run linters |
| `make docker-build` | Build Docker images |
| `make deploy` | Deploy to Kind cluster |
| `make clean` | Clean up artifacts |

## Debugging

### Controller

```bash
go run cmd/controller/main.go --zap-log-level=debug
```

### Inspecting CRDs

```bash
kubectl get aijobs -A
kubectl describe aijob <job-name> -n <namespace>
kubectl get aijobs -A -w
```

## Common Issues

### Port Already in Use

```bash
lsof -i :8000
kill -9 <PID>
```

### Redis Connection Failed

```bash
docker-compose ps redis
docker-compose restart redis
redis-cli ping
```

### Kind Cluster Issues

```bash
kind delete cluster
./scripts/setup-kind.sh
```
