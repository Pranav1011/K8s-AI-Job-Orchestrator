from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_clusters():
    return [{"name": "cluster-1", "nodes": 5}]
