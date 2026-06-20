from typing import List, Optional
from pydantic import BaseModel
from .listing import NormalizedListing
from .intent import Intent
from .neighborhood import NeighborhoodScore


class RecommendRequest(BaseModel):
    user_query: str
    thread_id: Optional[str] = None


class RecommendUpdate(BaseModel):
    intent: Optional[Intent]
    neighborhoods: Optional[List[NeighborhoodScore]] = None
    listings: Optional[List[NormalizedListing]] = None
    errors: Optional[List[str]] = None


class RecommendResponse(BaseModel):
    listings: List[NormalizedListing]
    errors: Optional[List[str]] = None


class TrackClickRequest(BaseModel):
    listing_id: str
    source: str
    affiliate_network: Optional[str] = None
    timestamp: Optional[str] = None
