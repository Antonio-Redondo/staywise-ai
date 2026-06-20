from typing import List, Optional, Tuple
from app.models.listing import NormalizedListing


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def score_listing(listing: NormalizedListing, intent, neighborhood_score: float) -> float:
    # Price component (30%) — closer to intent.budget_mid scores higher
    price_score = 50.0
    if getattr(intent, "budget_mid", None) and listing.price:
        try:
            mid = float(intent.budget_mid)
            diff = abs(listing.price - mid)
            price_score = _clamp(100.0 - (diff / mid * 100.0))
        except Exception:
            price_score = 50.0

    # Size component (20%) — normalized by 1000 sqft baseline
    size_score = 50.0
    if listing.square_feet:
        size_score = _clamp((listing.square_feet / 1000.0) * 100.0)

    # Neighborhood component (25%) — expects 0.0-1.0
    neighborhood_component = 50.0
    if neighborhood_score is not None:
        neighborhood_component = _clamp(neighborhood_score * 100.0)

    # Amenities (15%) — fraction of must_haves matched
    amenities_score = 0.0
    must = getattr(intent, "must_haves", []) or []
    if must:
        matched = len([m for m in must if m in (listing.amenities or [])])
        amenities_score = _clamp((matched / max(1, len(must))) * 100.0)

    # Freshness (10%) — TODO: use listed_date; placeholder 50
    freshness_score = 50.0

    final = (
        0.3 * price_score
        + 0.2 * size_score
        + 0.25 * neighborhood_component
        + 0.15 * amenities_score
        + 0.1 * freshness_score
    )
    return round(_clamp(final), 1)


def _norm(value: Optional[float], lo: float, hi: float) -> float:
    """Normalize value to 0..1 within [lo, hi]; 0.5 when undefined."""
    if value is None or hi <= lo:
        return 0.5
    return _clamp((value - lo) / (hi - lo), 0.0, 1.0)


def rank_listings(
    listings: List[NormalizedListing], intent, neighborhood_score
) -> List[Tuple[NormalizedListing, float]]:
    """Filter listings by hard constraints (budget, bedrooms) and rank them by a
    preference-weighted score so the results reorder with the query. Returns
    (listing, score) tuples sorted best-first. Never returns empty if any
    listings were supplied (falls back to ranking all when filters exclude all).
    """
    if not listings:
        return []

    tags = set(getattr(intent, "lifestyle_tags", []) or [])
    budget_max = getattr(intent, "budget_max", None)
    beds_min = getattr(intent, "bedrooms_min", None)

    def passes(l: NormalizedListing) -> bool:
        if budget_max and l.price and l.price > budget_max * 1.1:
            return False
        if beds_min and l.bedrooms is not None and l.bedrooms < beds_min:
            return False
        return True

    candidates = [l for l in listings if passes(l)] or list(listings)

    prices = [l.price for l in candidates if l.price]
    sqfts = [l.square_feet for l in candidates if l.square_feet]
    p_lo, p_hi = (min(prices), max(prices)) if prices else (0.0, 0.0)
    s_lo, s_hi = (min(sqfts), max(sqfts)) if sqfts else (0.0, 0.0)

    ranked: List[Tuple[NormalizedListing, float]] = []
    for l in candidates:
        score = score_listing(l, intent, neighborhood_score)
        price_pos = _norm(l.price, p_lo, p_hi)
        size_pos = _norm(l.square_feet, s_lo, s_hi)
        amenities = set(l.amenities or [])

        if "cheaper" in tags:
            score += (1.0 - price_pos) * 18.0
        if "premium" in tags:
            score += price_pos * 18.0
        if "spacious" in tags:
            score += size_pos * 18.0
        if "quiet" in tags:
            score += 12.0 if "quiet" in amenities else -5.0
        if "transit" in tags or "near_bart" in tags:
            score += 12.0 if "near_transit" in amenities else -5.0

        ranked.append((l, round(_clamp(score), 1)))

    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return ranked
