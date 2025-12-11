# Deployment Guide

This guide covers deploying the K8s AI Job Orchestrator to production Kubernetes environments.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Kubernetes | 1.25+ | EKS, GKE, AKS, or self-managed |
| Helm | 3.0+ | For chart deployment |
| PostgreSQL | 14+ | Managed or self-hosted |
| Redis | 7.0+ | With Sentinel for HA |
| kubectl | 1.25+ | Configured for target cluster |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Controller  │  │  Controller  │  │   API Pod    │ x3   │
│  │   (Leader)   │  │  (Standby)   │  │  (FastAPI)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                              │               │
│  ┌──────────────────────────────────────────┼─────────┐    │
│  │                 Service Mesh              │         │    │
│  └──────────────────────────────────────────┼─────────┘    │
│                                              │               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────▼───────┐      │
│  │ Worker Pods  │  │ Worker Pods  │  │    Redis     │      │
│  │   (GPU)      │  │   (CPU)      │  │  (Sentinel)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │   (Managed RDS)  │
                    └──────────────────┘
```

## Configuration

### Helm Values

The deployment is configured via `values.yaml`. Key parameters:

#### Replica Configuration

```yaml
replicaCount:
  controller: 2    # Active-Passive with Leader Election
  api: 3           # Horizontal scaling behind load balancer
  worker: 5        # Base compute pool size

autoscaling:
  api:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilization: 70
  worker:
    enabled: true
    minReplicas: 5
    maxReplicas: 50
    targetCPUUtilization: 80
```

#### Resource Limits

```yaml
resources:
  controller:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"

  api:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "2000m"
      memory: "2Gi"

  worker:
    requests:
      cpu: "2000m"
      memory: "8Gi"
      nvidia.com/gpu: "1"
    limits:
      cpu: "4000m"
      memory: "16Gi"
      nvidia.com/gpu: "1"
```

#### Database Configuration

```yaml
database:
  host: "postgres.example.com"
  port: 5432
  name: "aijobs"
  username: "aijobs_user"
  existingSecret: "postgres-credentials"
  secretKey: "password"
  pool:
    minSize: 5
    maxSize: 20
```

#### Redis Configuration

```yaml
redis:
  sentinel:
    enabled: true
    masterName: "mymaster"
    nodes:
      - "redis-sentinel-0.redis-sentinel:26379"
      - "redis-sentinel-1.redis-sentinel:26379"
      - "redis-sentinel-2.redis-sentinel:26379"
  existingSecret: "redis-credentials"
  secretKey: "password"
```

## Installation

### 1. Create Namespace

```bash
kubectl create namespace ai-platform
```

### 2. Create Secrets

```bash
# Database credentials
kubectl create secret generic postgres-credentials \
  --namespace ai-platform \
  --from-literal=password='your-secure-password'

# Redis credentials
kubectl create secret generic redis-credentials \
  --namespace ai-platform \
  --from-literal=password='your-redis-password'

# API JWT secret
kubectl create secret generic api-jwt-secret \
  --namespace ai-platform \
  --from-literal=secret='your-jwt-signing-key'
```

### 3. Install CRDs

```bash
kubectl apply -f controller/config/crd/bases/
```

### 4. Deploy with Helm

```bash
helm install ai-orchestrator ./helm/ai-job-orchestrator \
  --namespace ai-platform \
  --values values-production.yaml
```

### 5. Verify Deployment

```bash
# Check pod status
kubectl get pods -n ai-platform

# Check CRDs are installed
kubectl get crds | grep aiplatform

# Check services
kubectl get svc -n ai-platform
```

### 6. Configure Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-job-api
  namespace: ai-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.your-domain.com
      secretName: api-tls
  rules:
    - host: api.your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ai-job-api
                port:
                  number: 8000
```

## Upgrading

```bash
# Update with new values
helm upgrade ai-orchestrator ./helm/ai-job-orchestrator \
  --namespace ai-platform \
  --values values-production.yaml

# Scale workers
helm upgrade ai-orchestrator ./helm/ai-job-orchestrator \
  --namespace ai-platform \
  --set replicaCount.worker=10
```

## Production Checklist

### Security
- [ ] TLS enabled for all external endpoints
- [ ] Network Policies configured
- [ ] Secrets stored in external secret manager
- [ ] RBAC configured with least privilege

### High Availability
- [ ] Controller replicas: 2+ (leader election)
- [ ] API replicas: 3+
- [ ] Redis Sentinel or Cluster mode
- [ ] Pod Disruption Budgets configured

### Observability
- [ ] Prometheus ServiceMonitor configured
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] Log aggregation enabled

## Uninstallation

```bash
helm uninstall ai-orchestrator -n ai-platform
kubectl delete -f controller/config/crd/bases/
kubectl delete namespace ai-platform
```
