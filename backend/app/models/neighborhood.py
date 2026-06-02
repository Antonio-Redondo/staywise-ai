from typing import Optional
from pydantic import BaseModel


class NeighborhoodScore(BaseModel):
    name: str
    score: float
    median_price: Optional[int]
    walk_score: Optional[int]

    class Config:
        orm_mode = True
