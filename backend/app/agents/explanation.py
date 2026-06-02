from typing import List
from app.models.listing import NormalizedListing


def generate_explanation(listing: NormalizedListing, intent) -> str:
    reasons: List[str] = []
    if getattr(intent, "budget_mid", None) and listing.price:
        if listing.price <= intent.budget_mid:
            reasons.append("within budget")
        else:
            reasons.append("above budget")
    must = getattr(intent, "must_haves", []) or []
    matched = [m for m in must if m in (listing.amenities or [])]
    if matched:
        reasons.append("has " + ", ".join(matched))
    if listing.bedrooms:
        reasons.append(f"{listing.bedrooms} bedrooms")
    if not reasons:
        return "Potential match based on basic filters."
    return ". ".join(reasons) + "."
