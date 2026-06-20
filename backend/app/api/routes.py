from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.graph.graph import arun_pipeline
from app.db import SessionLocal, Click

router = APIRouter()


class RecommendRequest(BaseModel):
    userQuery: str
    threadId: Optional[str] = None


class TrackClickRequest(BaseModel):
    listingId: str
    source: str
    affiliateNetwork: Optional[str] = None


@router.get("/api/health")
async def health():
    return {"status": "ok"}


@router.post("/api/recommend")
async def recommend(req: RecommendRequest):
    if not req.userQuery:
        raise HTTPException(status_code=400, detail="userQuery required")
    state = await arun_pipeline(req.userQuery, thread_id=req.threadId)
    return state


@router.post("/api/track-click")
async def track_click(req: TrackClickRequest):
    # Insert into DB; use sessionmaker
    try:
        db = SessionLocal()
        click = Click(listing_id=req.listingId, source=req.source, affiliate_network=req.affiliateNetwork)
        db.add(click)
        db.commit()
        db.refresh(click)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            db.close()
        except Exception:
            pass
