import redis.asyncio as redis
import json
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, asdict

@dataclass
class JobMessage:
    job_id: str
    job_type: str
    priority: int
    payload: dict
    submitted_at: str
    retry_count: int = 0

class RedisJobQueue:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.queue_key = "ai_jobs:queue:{priority}"
        self.processing_key = "ai_jobs:processing"
        self.completed_key = "ai_jobs:completed"
        self.failed_key = "ai_jobs:failed"
        self.job_data_key = "ai_jobs:data:{job_id}"
    
    async def enqueue(self, job: JobMessage) -> str:
        """Add job to priority queue with O(log N) insertion"""
        # Store job data
        await self.redis.hset(
            self.job_data_key.format(job_id=job.job_id),
            mapping=asdict(job)
        )
        # Add to sorted set with priority as score
        await self.redis.zadd(
            "ai_jobs:priority_queue",
            {job.job_id: job.priority},
            nx=True
        )
        # Publish event for real-time updates
        await self.redis.publish("ai_jobs:events", json.dumps({
            "event": "job_submitted",
            "job_id": job.job_id
        }))
        return job.job_id
    
    async def dequeue(self, count: int = 1) -> List[JobMessage]:
        """Atomically dequeue highest priority jobs"""
        # Use ZPOPMAX for O(log N) removal of highest priority
        jobs = await self.redis.zpopmax("ai_jobs:priority_queue", count)
        result = []
        for job_id, priority in jobs:
            # redis-py returns bytes, need to decode if needed, but zpopmax returns (member, score)
            # job_id might be bytes or str depending on client decoding
            if isinstance(job_id, bytes):
                job_id = job_id.decode('utf-8')
                
            job_data = await self.redis.hgetall(
                self.job_data_key.format(job_id=job_id)
            )
            if job_data:
                # Decode byte keys/values from hgetall if needed
                decoded_data = {k.decode('utf-8'): v.decode('utf-8') if isinstance(v, bytes) else v for k, v in job_data.items()}
                
                # Payload is stored as string/dict, if it was serialized before. 
                # In enqueue asdict(job) -> payload is a dict. hset might fail if it's a dict unless serialized?
                # Actually hset mapping checks types. Simple types ok. Dict needs serialization.
                # Assuming payload in JobMessage is handled or serialized before passed to enqueue or we serialize it here.
                # Use json.loads for payload if it's a string
                if 'payload' in decoded_data and isinstance(decoded_data['payload'], str):
                     try:
                         decoded_data['payload'] = json.loads(decoded_data['payload'])
                     except:
                         pass
                
                # Move to processing set
                await self.redis.sadd(self.processing_key, job_id)
                result.append(JobMessage(**decoded_data))
        return result
    
    async def complete(self, job_id: str, result: dict):
        """Mark job as completed"""
        await self.redis.srem(self.processing_key, job_id)
        await self.redis.sadd(self.completed_key, job_id)
        await self.redis.hset(
            self.job_data_key.format(job_id=job_id),
            mapping={
                "result": json.dumps(result),
                "completed_at": datetime.utcnow().isoformat()
            }
        )
    
    async def fail(self, job_id: str, error: str, retry: bool = True):
        """Handle job failure with optional retry"""
        job_data = await self.redis.hgetall(
            self.job_data_key.format(job_id=job_id)
        )
        if not job_data:
            return

        decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in job_data.items()}
        retry_count = int(decoded_data.get("retry_count", 0))
        max_retries = 3
        
        if retry and retry_count < max_retries:
            # Re-enqueue with incremented retry count (Exponential Backoff could be here)
            await self.redis.hincrby(
                self.job_data_key.format(job_id=job_id),
                "retry_count", 1
            )
            # Add back to queue with slightly lower priority
            original_priority = int(decoded_data.get("priority", 50))
            await self.redis.zadd(
                "ai_jobs:priority_queue",
                {job_id: original_priority - 10}
            )
        else:
            # Move to Dead Letter Queue (DLQ)
            await self.redis.srem(self.processing_key, job_id)
            await self.redis.sadd(self.failed_key, job_id) # Failed set
            await self.redis.lpush("ai_jobs:dlq", job_id)  # DLQ List
            
            await self.redis.hset(
                self.job_data_key.format(job_id=job_id),
                mapping={
                    "error": error,
                    "failed_at": datetime.utcnow().isoformat(),
                    "status": "dead_letter"
                }
            )

    async def check_concurrency(self, limit: int) -> bool:
        """Check if global concurrency limit is reached"""
        count = await self.redis.scard(self.processing_key)
        return count < limit

    async def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """Acquire a distributed lock"""
        return await self.redis.set(f"lock:{lock_name}", "1", nx=True, ex=timeout)

