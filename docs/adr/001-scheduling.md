# ADR 001: Hybrid Scheduling Architecture

## Status
Accepted

## Context
We need to schedule high-throughput AI jobs while maintaining Kubernetes-native status and robust persistence.

## Decision
We chose a hybrid model:
1. **API + Redis**: Handles high-frequency job ingestion and queueing. Provides "fast path" feedback to users.
2. **K8s Controller + CRDs**: Acts as the authoritative state machine for long-running jobs. Syncs with Redis for queue processing status.

## Consequences
- **Pros**: 
    - Decouples ingestion scalability from K8s API server limits.
    - Allows using Redis for sophisticated O(1) queue operations (priority, preemption).
- **Cons**:
    - Dual state (Redis + K8s) requires careful reconciliation logic.
