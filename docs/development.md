# Development Guide

## Environment Setup
1. **Clone Repo**: `git clone ...`
2. **Install Dependencies**:
   ```bash
   pip install -r job-service/requirements.txt
   go mod download
   ```

## Running Locally

### Job Service
```bash
cd job-service
uvicorn app.main:app --reload
```

### Controller
Ensure Kubeconfig is set to a local cluster (Kind/Minikube).
```bash
cd controller
go run cmd/controller/main.go
```

## Testing
- **Python**: `pytest job-service/tests`
- **Go**: `go test ./controller/...`

## Contribution Workflow
1. Create a feature branch.
2. Ensure new features have logic in `task.md`.
3. Submit PR.
