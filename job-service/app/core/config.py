from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Job Scheduler"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/aijobs"
    REDIS_URL: str = "redis://localhost:6379"
    KUBERNETES_IN_CLUSTER: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
