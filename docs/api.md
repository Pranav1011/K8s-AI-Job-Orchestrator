# API Documentation

## Authentication
All endpoints require a Bearer Token (JWT).
Header: `Authorization: Bearer <token>`

## Endpoints

### Jobs
- **POST** `/api/v1/jobs/`: Submit a new job.
  - Body: `{"job_type": "string", "priority": 50, "image": "string"}`
- **GET** `/api/v1/jobs/`: List jobs.
- **GET** `/api/v1/jobs/{id}`: Get job details.

### Queues
- **GET** `/api/v1/queues/`: Get queue status and depth.

### Health
- **GET** `/health/live`: Liveness probe.
- **GET** `/health/ready`: Readiness probe.

## Error Codes
- **429**: Too Many Requests (System overloaded).
- **401**: Unauthorized.
- **403**: Forbidden (Insufficient permissions).
- **500**: Internal Server Error.
