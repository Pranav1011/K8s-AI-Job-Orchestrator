# Operations Guide

This guide covers monitoring, alerting, and troubleshooting for production deployments.

## Monitoring

### Metrics Endpoints

| Component | Endpoint | Port |
|-----------|----------|------|
| Job Service | `/metrics` | 8000 |
| Controller | `/metrics` | 8080 |
| Workers | `/metrics` | 9090 |

### Key Metrics

#### Job Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `aijob_submitted_total` | Counter | Total jobs submitted |
| `aijob_completed_total` | Counter | Completed jobs by status |
| `aijob_queue_depth` | Gauge | Current queue depth |
| `aijob_dispatch_latency_seconds` | Histogram | Submission to pickup time |
| `aijob_execution_duration_seconds` | Histogram | Job execution time |

#### Controller Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `controller_reconcile_total` | Counter | Reconciliation attempts |
| `controller_reconcile_errors_total` | Counter | Failed reconciliations |
| `controller_workqueue_depth` | Gauge | Work queue size |
| `controller_leader_election_master` | Gauge | Leader status (1/0) |

#### Worker Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `worker_jobs_processed_total` | Counter | Jobs processed |
| `worker_job_duration_seconds` | Histogram | Processing time |
| `worker_gpu_utilization` | Gauge | GPU utilization % |

## Alerting

### Critical Alerts

```yaml
- alert: HighJobFailureRate
  expr: |
    sum(rate(aijob_completed_total{status="failed"}[5m]))
    / sum(rate(aijob_completed_total[5m])) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Job failure rate > 10%"

- alert: ControllerDown
  expr: absent(controller_leader_election_master == 1)
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "No active controller leader"

- alert: QueueBacklogCritical
  expr: aijob_queue_depth > 5000
  for: 10m
  labels:
    severity: critical
  annotations:
    summary: "Queue backlog > 5000 jobs"
```

### Warning Alerts

```yaml
- alert: HighDispatchLatency
  expr: histogram_quantile(0.99, rate(aijob_dispatch_latency_seconds_bucket[5m])) > 0.5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "P99 dispatch latency > 500ms"

- alert: QueueBacklogWarning
  expr: aijob_queue_depth > 1000
  for: 15m
  labels:
    severity: warning
```

## Troubleshooting

### Job Stuck in Pending

**Diagnosis:**

```bash
kubectl get aijob <job-name> -o yaml
kubectl logs -l app=ai-job-controller --tail=200 | grep <job-id>
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Insufficient resources | Scale up nodes or reduce requests |
| Gang scheduling waiting | Verify `minMembers` available |
| Queue limit reached | Increase `maxConcurrency` |
| Controller not running | Check controller pod status |

### Job Stuck in Running

**Diagnosis:**

```bash
kubectl get pods -l job-id=<job-id>
kubectl logs <worker-pod> --tail=200
kubectl describe pod <worker-pod>
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Worker deadlock | Kill pod, job will retry |
| Network issues | Check network policies |
| Resource starvation | Check for OOM events |

### API Returning 429

**Diagnosis:**

```bash
curl -s http://localhost:8000/api/v1/queues/ | jq '.total_pending'
kubectl top pods -l app=ai-job-api
```

**Solutions:**

```bash
# Scale API replicas
kubectl scale deployment ai-job-api --replicas=5

# Scale workers to drain queue
kubectl scale deployment ai-job-worker --replicas=20
```

### Redis Connection Issues

**Diagnosis:**

```bash
kubectl get pods -l app=redis
kubectl exec -it deploy/ai-job-api -- redis-cli -h redis ping
kubectl exec -it redis-0 -- redis-cli INFO memory
```

### Database Connection Pool Exhausted

**Diagnosis:**

```bash
kubectl exec -it deploy/ai-job-api -- \
  python -c "from app.db import engine; print(engine.pool.status())"
```

**Solution:** Increase pool size in configuration.

## Runbooks

### Scaling Workers

```bash
kubectl scale deployment ai-job-worker --replicas=<count>

# Enable HPA
kubectl autoscale deployment ai-job-worker \
  --min=5 --max=50 --cpu-percent=70
```

### Draining Jobs Before Maintenance

```bash
# Pause queue
kubectl patch aijobqueue default --type='merge' \
  -p='{"spec":{"suspended":true}}'

# Wait for completion
watch kubectl get aijobs --field-selector=status.phase=Running

# Resume
kubectl patch aijobqueue default --type='merge' \
  -p='{"spec":{"suspended":false}}'
```

### Controller Failover

```bash
kubectl delete pod ai-job-controller-0
kubectl get lease ai-job-controller -o yaml
```

## Disaster Recovery

### Database

```bash
# Backup
pg_dump -h <host> -U postgres aijobs > backup.sql

# Restore
psql -h <host> -U postgres aijobs < backup.sql
```

### Redis Data Loss

If Redis is lost, jobs can be recovered from PostgreSQL and K8s CRDs. The reconciler will self-heal, though in-flight queue positions may be lost.

## SLIs and SLOs

| SLI | Target | Measurement |
|-----|--------|-------------|
| Dispatch latency (P99) | < 100ms | `histogram_quantile(0.99, aijob_dispatch_latency_seconds)` |
| Job success rate | > 99% | `sum(aijob_completed{status="succeeded"}) / sum(aijob_completed)` |
| API availability | > 99.9% | Synthetic probes + error rate |
| Queue processing rate | > 1000/min | `rate(aijob_completed_total[1m])` |
