import logging
from fastapi import APIRouter, Depends, Header, HTTPException
from app import config
from app.dependencies import get_resources
from app.services.ingest import build_index

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_admin(x_admin_token: str = Header(...)):
    if x_admin_token != config.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")

@router.post("/admin/reindex", dependencies=[Depends(verify_admin)])
async def reindex(recreate: bool = True, res=Depends(get_resources)):
    try:
        count = build_index(res.milvus, res.embedding, recreate=recreate)
        return {"status": "ok", "count": count}
    except Exception as e:
        logger.exception("reindex failed")
        raise HTTPException(status_code=500, detail=str(e))