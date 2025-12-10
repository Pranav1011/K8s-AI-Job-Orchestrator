from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes import jobs, queues, clusters, metrics
from app.core.config import settings

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup Tracing
resource = Resource.create(attributes={"service.name": "ai-job-api"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# OAuth2 scheme and dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify JWT Token (Mocked for now)
    if token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": "user", "role": "admin"}

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

app = FastAPI(title="AI Job Scheduler API", version="1.0.0")

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Routers
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(queues.router, prefix="/api/v1/queues", tags=["queues"])
app.include_router(clusters.router, prefix="/api/v1/clusters", tags=["clusters"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

# Health Checks
@app.get("/health/live")
async def health_live():
    return {"status": "alive"}

@app.get("/health/ready")
async def health_ready():
    # Check DB and Redis connection
    # (Simplified for now, in real prod check actual connectivity)
    return {"status": "ready"}

@app.on_event("startup")
async def startup_event():
    # Helper to clean up on startup if needed
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Graceful shutdown logic (e.g. close DB pools)
    # The dependency injection usually handles session closure but explicit cleanup is good
    pass

@app.get("/health")
async def health_check():
    return {"status": "ok"}
