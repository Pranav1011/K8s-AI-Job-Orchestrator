# K8s AI Job Orchestrator

[![Build Status](https://github.com/Pranav1011/K8s-AI-Job-Orchestrator/actions/workflows/ci.yaml/badge.svg)](https://github.com/Pranav1011/K8s-AI-Job-Orchestrator/actions)
[![Go Report Card](https://goreportcard.com/badge/github.com/Pranav1011/K8s-AI-Job-Orchestrator)](https://goreportcard.com/report/github.com/Pranav1011/K8s-AI-Job-Orchestrator)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Kubernetes-native distributed job scheduler for AI/ML inference, training, and simulation workloads. Built for **high-throughput, low-latency** job orchestration across distributed GPU clusters.

## Features

- **Priority-based Scheduling** with Gang Scheduling support for distributed training
- **Sub-100ms** job dispatch latency using an optimized Redis-backed queue
- **Reliable Execution** with automatic retries, exponential backoff, and Dead Letter Queues (DLQ)
- **Full Observability** with Prometheus metrics, Grafana dashboards, and OpenTelemetry tracing
- **AI Agentic Workflows** for automated CI/CD and issue triage pipelines
- **Production-ready** with High Availability (HA), RBAC, and Network Policies

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Control Plane                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   K8s Controller │    │    Scheduler    │    │  Agent Registry │         │
│  │       (Go)       │◄──►│  (Gang/Priority)│    │   (Workflows)   │         │
│  └────────┬────────┘    └─────────────────┘    └─────────────────┘         │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    Kubernetes API (CRDs)                         │       │
│  │              AIJob | AIJobQueue | ComputeCluster                 │       │
│  └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Data Plane                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Job Service   │    │      Redis      │    │   PostgreSQL    │         │
│  │    (FastAPI)    │◄──►│  (Queue/Lock)   │    │  (Persistence)  │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Compute Plane                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ Inference Worker│    │Simulation Worker│    │  Training Worker│         │
│  │    (PyTorch)    │    │  (Sensor Sim)   │    │   (DDP/FSDP)    │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

The system consists of three main planes:

1. **Control Plane**: Kubernetes Controller (Go) managing `AIJob`, `AIJobQueue`, and `AgentWorkflow` CRDs
2. **Data Plane**: FastAPI Service + Redis (Queue/Locking) + PostgreSQL (Persistence)
3. **Compute Plane**: Python Workers (PyTorch) executing inference, training, and simulation workloads

## Quick Start

### Prerequisites

- Kubernetes 1.25+ (Kind, Minikube, or Cloud)
- Helm 3+
- Docker
- Go 1.21+
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone https://github.com/Pranav1011/K8s-AI-Job-Orchestrator.git
cd K8s-AI-Job-Orchestrator

# Setup local development cluster (Kind)
make dev-setup

# Deploy the platform
make deploy
```

### Submit a Job

```bash
# Submit an inference job
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "job_type": "inference",
    "priority": 80,
    "image": "pytorch-inference:latest",
    "config": {
      "model": "resnet50",
      "batch_size": 32
    }
  }'

# Check job status
curl http://localhost:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer $API_TOKEN"
```

### Submit a Gang-Scheduled Training Job

```bash
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "job_type": "training",
    "priority": 100,
    "image": "pytorch-ddp:latest",
    "gang": {
      "enabled": true,
      "min_members": 4,
      "topology": "ring"
    }
  }'
```

## Performance Benchmarks

Tested on a 3-node Kubernetes cluster (8 vCPU, 32GB RAM each):

| Metric | Value |
|--------|-------|
| **Throughput** | 5,000 jobs/sec |
| **Dispatch Latency (P50)** | 12ms |
| **Dispatch Latency (P99)** | 45ms |
| **Max Concurrent Jobs** | 10,000+ |
| **Gang Scheduling Overhead** | <5ms |

## Project Structure

```
.
├── controller/          # Kubernetes controller (Go)
│   ├── cmd/            # Entry points
│   ├── pkg/            # Core packages
│   │   ├── apis/       # CRD type definitions
│   │   ├── controller/ # Reconciliation logic
│   │   ├── scheduler/  # Gang & priority scheduling
│   │   └── agent/      # AI agent registry
│   └── config/         # CRD manifests
├── job-service/         # REST API service (Python)
│   ├── app/
│   │   ├── api/        # Route handlers
│   │   ├── core/       # Configuration
│   │   ├── db/         # Database models
│   │   └── services/   # Business logic
│   └── tests/
├── worker/              # Job workers (Python)
├── helm/                # Helm charts
├── monitoring/          # Prometheus & Grafana configs
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## Documentation

- [Architecture](docs/architecture.md) - System design and component overview
- [API Reference](docs/api.md) - REST API documentation
- [Deployment Guide](docs/deployment.md) - Production deployment instructions
- [Development Guide](docs/development.md) - Local development setup
- [Operations Guide](docs/operations.md) - Monitoring, alerting, and troubleshooting

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Hybrid Queue (Redis + K8s)** | Decouples high-throughput ingestion from K8s API server limits |
| **Gang Scheduling** | Ensures distributed training jobs get all required resources atomically |
| **CRD-based State** | Kubernetes-native, GitOps-friendly, self-healing through reconciliation |
| **Leader Election** | Single active controller prevents race conditions in scheduling |

See [ADR-001: Scheduling Architecture](docs/adr/001-scheduling.md) for detailed rationale.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
