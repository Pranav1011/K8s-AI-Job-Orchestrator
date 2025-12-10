# Operations Guide

## Monitoring
The system exposes Prometheus metrics at `/metrics` (API) and `:8080/metrics` (Controller).

### Key Metrics
- **Queue Depth**: `aijob_queue_depth_total`
- **Job Status**: `aijob_status_total`
- **Inference Latency**: `inference_latency_seconds`
- **Simulation Pass Rate**: `simulation_pass_rate`

### Alerting
Default alerts are configured in `monitoring/prometheus/alerts/job_alerts.yml`:
- **HighQueueDepth**: > 1000 pending jobs
- **HighFailureRate**: > 10% failure rate
- **HighLatency**: P99 > 500ms

## Troubleshooting

### Job Stuck in Pending
1. Check Cluster Capacity: Is there enough GPU/CPU?
2. Check Gang Scheduling: Are `minMembers` available?
3. Check Controller Logs: `kubectl logs -l app=ai-job-controller`

### API Slow / 429 Errors
1. Check `aijob_queue_depth`.
2. Check Redis Latency.
3. Scale up API replicas or increase concurrency limits in `AIJobQueue` CRD.

### Disaster Recovery
- **Database**: Perform regular PostgreSQL backups.
- **Job State**: If Redis is lost, the Source of Truth is PostgreSQL + K8s CRDs. Reconcilers should eventually self-heal, though in-flight queue positions might be lost.
