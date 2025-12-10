from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
async def get_metrics_summary():
    return {"jobs_queued": 10, "processing": 5}
