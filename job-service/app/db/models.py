from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, ForeignKey, Boolean, Float, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base
import uuid
import enum

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, enum.Enum):
    INFERENCE = "inference"
    TRAINING = "training"
    EVALUATION = "evaluation"
    SIMULATION = "simulation"
    BATCH = "batch"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    priority = Column(Integer, nullable=False, default=50)
    queue_id = Column(UUID(as_uuid=True), ForeignKey("job_queues.id"))

    # Job configuration
    image = Column(String(500), nullable=False)
    command = Column(ARRAY(Text))
    args = Column(ARRAY(Text))
    env_vars = Column(JSON, default={})

    # Resource requirements
    cpu_request = Column(String(50))
    memory_request = Column(String(50))
    gpu_request = Column(Integer, default=0)

    # Input/Output
    input_config = Column(JSON)
    output_config = Column(JSON)
    model_config = Column(JSON)

    # Execution metadata
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=3600)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    queued_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Results
    result = Column(JSON)
    error_message = Column(Text)

    # Kubernetes metadata
    k8s_namespace = Column(String(255))
    k8s_pod_name = Column(String(255))
    k8s_node_name = Column(String(255))

    # Metrics relation
    metrics = relationship("JobMetric", back_populates="job", uselist=False, cascade="all, delete-orphan")


class JobQueue(Base):
    __tablename__ = "job_queues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    max_concurrent_jobs = Column(Integer, default=100)
    is_paused = Column(Boolean, default=False)
    scheduling_algorithm = Column(String(50), default='priority')

    # Resource quotas
    max_gpus = Column(Integer)
    max_cpus = Column(Integer)
    max_memory_gb = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ComputeCluster(Base):
    __tablename__ = "compute_clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    k8s_context = Column(String(255))

    # Capacity
    total_nodes = Column(Integer, default=0)
    available_nodes = Column(Integer, default=0)
    total_gpus = Column(Integer, default=0)
    available_gpus = Column(Integer, default=0)

    # Status
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class JobMetric(Base):
    __tablename__ = "job_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    
    # Performance metrics
    latency_p50_ms = Column(Float)
    latency_p95_ms = Column(Float)
    latency_p99_ms = Column(Float)
    throughput_rps = Column(Float)

    # Resource usage
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    gpu_usage_percent = Column(Float)
    gpu_memory_usage_mb = Column(Float)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="metrics")
