from typing import List, Dict
from app.models.neighborhood import NeighborhoodScore


def score_neighborhoods(neighborhoods: List[Dict]) -> List[NeighborhoodScore]:
    """Given a list of neighborhood dicts with optional `median_price` and
    `walk_score`, produce a `NeighborhoodScore` list with a simple heuristic.
    """
    results: List[NeighborhoodScore] = []
    for n in neighborhoods:
        name = n.get("name") or n.get("neighborhood") or ""
        median_price = n.get("median_price")
        walk_score = n.get("walk_score") or 50
        # Compute score: 60% walk_score normalized, 40% inverse median price
        walk_component = (walk_score / 100.0) * 0.6
        price_component = 0.0
        if median_price:
            capped = min(median_price / 1_000_000, 1.0)
            price_component = (1.0 - capped) * 0.4
        score = round(walk_component + price_component, 2)
        results.append(
            NeighborhoodScore(name=name, score=score, median_price=median_price, walk_score=walk_score)
        )
    return results
