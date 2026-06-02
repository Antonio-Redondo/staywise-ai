from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class State:
    user_query: str
    thread_id: Optional[str] = None
    intent: Optional[Dict[str, Any]] = None
    neighborhood_scores: List[Dict[str, Any]] = field(default_factory=list)
    listings: List[Dict[str, Any]] = field(default_factory=list)
    scored: List[Dict[str, Any]] = field(default_factory=list)
    explained: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "user_query": self.user_query,
            "thread_id": self.thread_id,
            "intent": self.intent,
            "neighborhood_scores": self.neighborhood_scores,
            "listings": self.listings,
            "scored": self.scored,
            "explained": self.explained,
            "errors": self.errors,
        }
