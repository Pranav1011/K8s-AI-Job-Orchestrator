# ADR 001: Hybrid Scheduling Architecture

## Status

Accepted

## Date

2024-01-15

## Context

We need to build a job scheduling system for AI/ML workloads that can:

1. Handle high-throughput job submission (5,000+ jobs/second)
2. Provide sub-100ms dispatch latency
3. Support gang scheduling for distributed training
4. Maintain Kubernetes-native declarative state management
5. Ensure reliability through self-healing reconciliation

The Kubernetes API server and etcd have known limitations for high-write workloads. Directly creating one Custom Resource per job would stress etcd and increase API server latency at scale.

## Decision

We chose a **hybrid scheduling architecture** that combines:

1. **Redis for fast-path operations**: High-frequency job ingestion, priority queueing, and distributed locking
2. **Kubernetes CRDs for authoritative state**: Long-running job state, gang scheduling decisions, and declarative management
3. **PostgreSQL for persistence**: Job history, audit logs, and recovery data

### Architecture

```
User Request
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  FastAPI    │────►│   Redis     │◄────│  Controller │
│  (Ingestion)│     │  (Queue)    │     │  (Scheduler)│
└─────────────┘     └─────────────┘     └─────────────┘
     │                                         │
     ▼                                         ▼
┌─────────────┐                         ┌─────────────┐
│ PostgreSQL  │                         │ Kubernetes  │
│ (Persist)   │                         │ (CRDs/Pods) │
└─────────────┘                         └─────────────┘
```

### Data Flow

1. **Job Submission**: API validates request, writes to PostgreSQL, pushes job ID to Redis ZSET
2. **Scheduling**: Controller watches Redis queue, makes scheduling decisions, creates AIJob CRs
3. **Execution**: Controller creates worker pods based on AIJob spec
4. **Completion**: Controller updates AIJob status, removes from Redis queue

### Gang Scheduling

For distributed training jobs requiring multiple coordinated pods:

1. Controller checks if `minMembers` capacity is available
2. If yes, atomically creates all pods and updates CRD
3. If no, job remains in queue until capacity is available
4. Preemption logic can evict lower-priority jobs if configured

## Consequences

### Positive

- **Decoupled Ingestion**: Redis handles high-throughput writes without stressing Kubernetes API server
- **Sub-millisecond Queue Operations**: Redis ZSET provides O(log N) priority operations
- **Kubernetes-Native**: CRDs enable GitOps, kubectl management, and ecosystem integration
- **Resilient**: PostgreSQL + CRDs provide dual persistence for disaster recovery

### Negative

- **Dual State Management**: Must carefully reconcile Redis queue state with Kubernetes CRD state
- **Increased Complexity**: More components to operate (Redis, PostgreSQL, Controller, API)
- **Eventual Consistency**: Small window where Redis and CRD state may diverge

### Mitigations

| Risk | Mitigation |
|------|------------|
| State divergence | Periodic reconciliation loop syncs Redis with CRD state |
| Redis failure | Jobs recoverable from PostgreSQL; Sentinel provides HA |
| Controller crash | Leader election ensures quick failover; CRD state preserved |

## Alternatives Considered

### 1. Pure Kubernetes (One CRD per Job)

**Rejected**: etcd write throughput limited (~1000 writes/sec), not suitable for 5000+ jobs/second.

### 2. Pure Queue-Based (No CRDs)

**Rejected**: Loses Kubernetes-native benefits (kubectl, GitOps, RBAC, ecosystem integration).

### 3. Kueue / Volcano

**Considered**: Less flexibility for custom scheduling logic; wanted full control over scheduler behavior.

## References

- [Kubernetes Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
- [Redis Sorted Sets](https://redis.io/docs/data-types/sorted-sets/)
- [Gang Scheduling in Kubernetes](https://github.com/kubernetes-sigs/scheduler-plugins/tree/master/pkg/coscheduling)
