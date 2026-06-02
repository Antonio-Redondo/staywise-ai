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
