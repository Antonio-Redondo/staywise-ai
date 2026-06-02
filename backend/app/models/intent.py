from typing import List, Optional
from pydantic import BaseModel, Field


class Intent(BaseModel):
    budget_min: Optional[int] = Field(None, ge=0)
    budget_max: Optional[int] = Field(None, ge=0)
    bedrooms_min: Optional[int] = Field(None, ge=0)
    bedrooms_max: Optional[int] = Field(None, ge=0)
    lifestyle_tags: List[str] = Field(default_factory=list)
    must_haves: List[str] = Field(default_factory=list)
    nice_to_haves: List[str] = Field(default_factory=list)
    commute_target: Optional[str] = None

    @property
    def budget_mid(self) -> Optional[float]:
        if self.budget_min is None or self.budget_max is None:
            return None
        return (self.budget_min + self.budget_max) / 2

    @property
    def bedrooms_mid(self) -> Optional[float]:
        if self.bedrooms_min is None or self.bedrooms_max is None:
            return None
        return (self.bedrooms_min + self.bedrooms_max) / 2

    @property
    def budget_range(self) -> Optional[float]:
        if self.budget_min is None or self.budget_max is None:
            return None
        return max(1.0, self.budget_max - self.budget_min)

    @property
    def bedrooms_range(self) -> Optional[float]:
        if self.bedrooms_min is None or self.bedrooms_max is None:
            return None
        return max(1.0, self.bedrooms_max - self.bedrooms_min)
