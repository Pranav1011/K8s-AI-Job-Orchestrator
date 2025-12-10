from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_queues():
    return [{"name": "default", "priority": "high"}]
