# Deployment Guide

## Prerequisites
- **Kubernetes Cluster**: Version 1.25+
- **Helm**: Version 3.0+
- **Database**: PostgreSQL 14+ (or use the internal Helm chart dependency)
- **Redis**: Redis 7.0+ (with Sentinel for HA)

## Configuration
The `values.yaml` file controls the deployment. Key parameters:

### Replicas
```yaml
replicaCount:
  controller: 2  # Active-Passive for Leader Election
  api: 3         # Horizontal scaling
  worker: 5      # Compute pool size
```

### Resources
Adjust resource limits based on your node types (e.g., set GPU limits for workers).
```yaml
resources:
  worker:
    limits:
      nvidia.com/gpu: "1"
```

## Installation Steps
1. **Add Helm Repo**:
   ```bash
   helm repo add ai-scheduler https://charts.example.com
   helm repo update
   ```

2. **Install Chart**:
   ```bash
   helm install my-scheduler ./helm/ai-job-orchestrator --namespace ai-platform --create-namespace
   ```

3. **Verify Deployment**:
   ```bash
   kubectl get pods -n ai-platform
   ```

## Upgrading
```bash
helm upgrade my-scheduler ./helm/ai-job-orchestrator --set replicaCount.worker=10
```
