.PHONY: all build test lint docker helm deploy clean

all: lint test build

# Build targets
build-controller:
	cd controller && go build -o bin/controller ./cmd/controller

build-api:
	cd job-service && pip install -e .

build-worker:
	cd worker && pip install -e .

build: build-controller build-api build-worker

# Test targets
test-controller:
	cd controller && go test -v -race -coverprofile=coverage.out ./...

test-api:
	cd job-service && pytest -v --cov=app --cov-report=html

test-worker:
	cd worker && python -m pytest -v --cov=. --cov-report=html

test: test-controller test-api test-worker

# Lint targets
lint-go:
	cd controller && golangci-lint run

lint-python:
	cd job-service && black --check . && isort --check . && mypy app
	cd worker && black --check . && isort --check . && mypy .

lint: lint-go lint-python

# Docker targets
docker-build:
	docker build -t ai-job-controller:latest -f controller/Dockerfile .
	docker build -t ai-job-api:latest -f job-service/Dockerfile .
	docker build -t ai-job-worker:latest -f worker/Dockerfile .

# Kubernetes targets
install-crds:
	kubectl apply -f controller/config/crd/bases/

deploy:
	helm upgrade --install ai-scheduler ./helm/ai-job-orchestrator

# Local development
dev-controller:
	cd controller && go run ./cmd/controller/main.go

dev-api:
	cd job-service && uvicorn app.main:app --reload --port 8000

dev-worker:
	cd worker && python main.py

# Local Setup
dev-setup:
	@echo "🚀 Setting up development environment..."
	docker-compose up -d postgres redis prometheus grafana jaeger
	@echo "⏳ Waiting for services..."
	sleep 10
	@echo "📦 Running migrations..."
	cd job-service && alembic upgrade head
	@echo "✅ Ready! Run 'make dev-api' and 'make dev-controller'"

# Cleanup
clean:
	rm -rf controller/bin
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
