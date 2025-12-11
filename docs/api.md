# API Reference

## Overview

The Job Service exposes a REST API for managing AI jobs, queues, and clusters. All endpoints are served at `http://<host>:8000/api/v1/`.

## Authentication

All endpoints (except health checks) require a Bearer token.

```
Authorization: Bearer <token>
```

Tokens are JWTs issued by your identity provider. The API validates the token signature and extracts user claims for authorization.

## Base URL

```
Production: https://api.your-domain.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Jobs

### Create Job

Submit a new AI job for execution.

**Endpoint:** `POST /jobs/`

**Request Body:**

```json
{
  "job_type": "inference",
  "priority": 80,
  "image": "pytorch-inference:v1.0",
  "config": {
    "model": "resnet50",
    "batch_size": 32
  },
  "resources": {
    "cpu": "2",
    "memory": "8Gi",
    "gpu": 1
  },
  "gang": {
    "enabled": false,
    "min_members": 1
  },
  "timeout_seconds": 3600,
  "retry_policy": {
    "max_retries": 3,
    "backoff_multiplier": 2
  }
}
```

**Response:** `201 Created`

```json
{
  "id": "job-abc123",
  "job_type": "inference",
  "priority": 80,
  "status": "pending",
  "created_at": "2024-01-15T10:00:00Z",
  "queue_position": 5
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `400` | Invalid request body |
| `401` | Missing or invalid token |
| `403` | Insufficient permissions |
| `429` | Rate limit exceeded |

---

### List Jobs

Retrieve a paginated list of jobs.

**Endpoint:** `GET /jobs/`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter by status: `pending`, `queued`, `running`, `succeeded`, `failed` |
| `job_type` | string | - | Filter by job type |
| `priority_min` | int | 0 | Minimum priority |
| `limit` | int | 50 | Results per page (max 100) |
| `offset` | int | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "job-abc123",
      "job_type": "inference",
      "priority": 80,
      "status": "running",
      "created_at": "2024-01-15T10:00:00Z",
      "started_at": "2024-01-15T10:00:05Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### Get Job

Retrieve details of a specific job.

**Endpoint:** `GET /jobs/{job_id}`

**Response:** `200 OK`

```json
{
  "id": "job-abc123",
  "job_type": "inference",
  "priority": 80,
  "status": "running",
  "image": "pytorch-inference:v1.0",
  "config": {
    "model": "resnet50",
    "batch_size": 32
  },
  "resources": {
    "cpu": "2",
    "memory": "8Gi",
    "gpu": 1
  },
  "created_at": "2024-01-15T10:00:00Z",
  "started_at": "2024-01-15T10:00:05Z",
  "completed_at": null,
  "retry_count": 0,
  "worker_id": "worker-xyz789",
  "logs_url": "/api/v1/jobs/job-abc123/logs"
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `404` | Job not found |

---

### Cancel Job

Cancel a pending or running job.

**Endpoint:** `DELETE /jobs/{job_id}`

**Response:** `200 OK`

```json
{
  "id": "job-abc123",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:05:00Z"
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `404` | Job not found |
| `409` | Job already completed or cancelled |

---

### Get Job Logs

Stream logs from a running or completed job.

**Endpoint:** `GET /jobs/{job_id}/logs`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `follow` | bool | false | Stream logs in real-time |
| `tail` | int | 100 | Number of lines from end |
| `timestamps` | bool | true | Include timestamps |

**Response:** `200 OK` (text/plain or text/event-stream)

```
2024-01-15T10:00:05Z Loading model resnet50...
2024-01-15T10:00:10Z Model loaded successfully
2024-01-15T10:00:11Z Processing batch 1/100...
```

---

## Queues

### Get Queue Status

Retrieve the current status of job queues.

**Endpoint:** `GET /queues/`

**Response:** `200 OK`

```json
{
  "queues": [
    {
      "name": "default",
      "depth": 42,
      "processing": 10,
      "max_concurrency": 100,
      "oldest_job_age_seconds": 120
    },
    {
      "name": "high-priority",
      "depth": 5,
      "processing": 8,
      "max_concurrency": 50,
      "oldest_job_age_seconds": 15
    }
  ],
  "total_pending": 47,
  "total_processing": 18
}
```

---

### Get Queue Details

Get detailed information about a specific queue.

**Endpoint:** `GET /queues/{queue_name}`

**Response:** `200 OK`

```json
{
  "name": "high-priority",
  "depth": 5,
  "processing": 8,
  "max_concurrency": 50,
  "jobs": [
    {
      "id": "job-abc123",
      "priority": 100,
      "queued_at": "2024-01-15T10:00:00Z"
    }
  ],
  "stats": {
    "jobs_processed_1h": 250,
    "avg_wait_time_seconds": 12.5,
    "avg_processing_time_seconds": 45.2
  }
}
```

---

## Clusters

### List Compute Clusters

Retrieve available compute clusters.

**Endpoint:** `GET /clusters/`

**Response:** `200 OK`

```json
{
  "clusters": [
    {
      "name": "gpu-cluster",
      "status": "healthy",
      "total_nodes": 10,
      "available_gpus": 24,
      "total_gpus": 40,
      "running_jobs": 16
    }
  ]
}
```

---

### Get Cluster Details

Get detailed information about a compute cluster.

**Endpoint:** `GET /clusters/{cluster_name}`

**Response:** `200 OK`

```json
{
  "name": "gpu-cluster",
  "status": "healthy",
  "nodes": [
    {
      "name": "gpu-node-01",
      "status": "ready",
      "gpus": {
        "total": 4,
        "available": 2,
        "type": "nvidia-a100"
      },
      "cpu": {
        "total": "32",
        "available": "16"
      },
      "memory": {
        "total": "256Gi",
        "available": "128Gi"
      }
    }
  ],
  "capacity": {
    "max_jobs": 500,
    "current_jobs": 156
  }
}
```

---

## Metrics

### Get System Metrics

Retrieve aggregated system metrics.

**Endpoint:** `GET /metrics/`

**Response:** `200 OK`

```json
{
  "jobs": {
    "total_submitted_24h": 12500,
    "total_completed_24h": 12350,
    "total_failed_24h": 150,
    "success_rate": 0.988
  },
  "latency": {
    "dispatch_p50_ms": 12,
    "dispatch_p99_ms": 45,
    "execution_p50_seconds": 120,
    "execution_p99_seconds": 450
  },
  "throughput": {
    "jobs_per_second": 4.2,
    "peak_jobs_per_second": 8.5
  }
}
```

---

## Health Checks

### Liveness Probe

Indicates if the service is running.

**Endpoint:** `GET /health/live`

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

---

### Readiness Probe

Indicates if the service is ready to accept traffic.

**Endpoint:** `GET /health/ready`

**Response:** `200 OK`

```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "kubernetes": "ok"
  }
}
```

**Response:** `503 Service Unavailable`

```json
{
  "status": "degraded",
  "checks": {
    "database": "ok",
    "redis": "error",
    "kubernetes": "ok"
  }
}
```

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid job configuration",
    "details": [
      {
        "field": "priority",
        "message": "Priority must be between 0 and 100"
      }
    ],
    "request_id": "req-xyz789"
  }
}
```

## Error Codes

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| `400` | `VALIDATION_ERROR` | Request body validation failed |
| `401` | `UNAUTHORIZED` | Missing or invalid authentication |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `404` | `NOT_FOUND` | Resource not found |
| `409` | `CONFLICT` | Operation conflicts with current state |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Internal server error |
| `503` | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

## Rate Limiting

The API enforces rate limits per client:

| Endpoint | Limit |
|----------|-------|
| `POST /jobs/` | 100 requests/minute |
| `GET /jobs/` | 300 requests/minute |
| Other endpoints | 600 requests/minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705315260
```
