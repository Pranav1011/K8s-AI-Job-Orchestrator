from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.api import dependencies
from app.db import models
from app.db.models import Job, JobStatus
from app.services.redis_queue import RedisJobQueue, JobMessage
from pydantic import BaseModel

router = APIRouter()

# Pydantic Models (Move to schemas.py in real app)
class JobCreate(BaseModel):
    external_id: str
    job_type: str
    priority: int = 50
    image: str
    command: List[str] = []
    args: List[str] = []
    input_config: dict = {}
    output_config: dict = {}
    
class JobResponse(BaseModel):
    id: UUID
    external_id: str
    status: str
    priority: int
    created_at: str

@router.post("/", response_model=JobResponse)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    redis_client = Depends(dependencies.get_redis)
):
    # 1. Save to DB
    job = Job(
        external_id=job_in.external_id,
        job_type=job_in.job_type,
        priority=job_in.priority,
        image=job_in.image,
        command=job_in.command,
        args=job_in.args,
        input_config=job_in.input_config,
        output_config=job_in.output_config,
        status=JobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 2. Enqueue in Redis
    queue = RedisJobQueue(redis_client)
    
    # Backpressure / Rate Limiting Check
    # Hardcoded limit for demo, ideally fetch from Queue Config or Redis
    if not await queue.check_concurrency(limit=1000):
        # Raise 429 Too Many Requests
        raise HTTPException(
            status_code=429,
            detail="System is overloaded, please try again later",
            headers={"Retry-After": "60"}
        )

    msg = JobMessage(
        job_id=str(job.id),
        job_type=job.job_type,
        priority=job.priority,
        payload={
            "image": job.image,
            "command": job.command,
            "args": job.args
        },
        submitted_at=str(job.created_at)
    )
    await queue.enqueue(msg)
    
    # Update status to Queued
    job.status = JobStatus.QUEUED
    await db.commit()
    
    return JobResponse(
        id=job.id,
        external_id=job.external_id,
        status=job.status.value,
        priority=job.priority,
        created_at=str(job.created_at)
    )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(dependencies.get_db)
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobResponse(
        id=job.id,
        external_id=job.external_id,
        status=job.status.value,
        priority=job.priority,
        created_at=str(job.created_at)
    )

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(dependencies.get_db)
):
    query = select(Job).offset(skip).limit(limit)
    if status:
        query = query.where(Job.status == status)
        
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [
        JobResponse(
            id=job.id,
            external_id=job.external_id,
            status=job.status.value,
            priority=job.priority,
            created_at=str(job.created_at)
        ) for job in jobs
    ]
