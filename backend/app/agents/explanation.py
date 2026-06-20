from typing import List
from app.models.listing import NormalizedListing


def generate_explanation(listing: NormalizedListing, intent) -> str:
    reasons: List[str] = []
    tags = set(getattr(intent, "lifestyle_tags", []) or [])
    amenities = set(listing.amenities or [])

    budget_max = getattr(intent, "budget_max", None)
    if budget_max and listing.price:
        reasons.append("within budget" if listing.price <= budget_max else "above budget")
    elif getattr(intent, "budget_mid", None) and listing.price:
        reasons.append("within budget" if listing.price <= intent.budget_mid else "above budget")

    must = getattr(intent, "must_haves", []) or []
    matched = [m.replace("_", " ") for m in must if m in amenities]
    if matched:
        reasons.append("has " + ", ".join(matched))

    if "quiet" in tags and "quiet" in amenities:
        reasons.append("on a quiet street")
    if ("transit" in tags or "near_bart" in tags) and "near_transit" in amenities:
        reasons.append("close to transit")
    if "spacious" in tags and listing.square_feet and listing.square_feet >= 1000:
        reasons.append("spacious layout")
    if "cheaper" in tags and "within budget" in reasons:
        reasons.append("great value")

    if listing.bedrooms:
        plural = "s" if listing.bedrooms != 1 else ""
        reasons.append(f"{listing.bedrooms} bedroom{plural}")
    if not reasons:
        return "Potential match based on basic filters."
    return ". ".join(r[0].upper() + r[1:] for r in reasons) + "."
