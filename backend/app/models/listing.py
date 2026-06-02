from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from datetime import date


class NormalizedListing(BaseModel):
    id: str
    source_url: HttpUrl
    address: str
    price: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_feet: Optional[int]
    photo_url: Optional[HttpUrl]
    source: str
    listed_date: Optional[date]
    amenities: List[str] = []

    class Config:
        orm_mode = True
