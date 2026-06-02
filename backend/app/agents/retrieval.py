from typing import List
from app.clients.real_estate_api import RealEstateAPIClient
from app.models.listing import NormalizedListing


async def fetch_and_normalize_listings(neighborhoods: List[str], client: RealEstateAPIClient, limit_per: int = 5) -> List[NormalizedListing]:
    results: List[NormalizedListing] = []
    for n in neighborhoods:
        raw_listings = await client.fetch_listings_for_neighborhood(n, limit=limit_per)
        for r in raw_listings:
            try:
                nl = NormalizedListing(
                    id=str(r.get("id") or r.get("listing_id") or ""),
                    source_url=r.get("url") or r.get("source_url") or "https://example.com",
                    address=r.get("address") or r.get("display_address") or "",
                    price=r.get("price"),
                    bedrooms=r.get("beds") or r.get("bedrooms"),
                    bathrooms=r.get("baths") or r.get("bathrooms"),
                    square_feet=r.get("sqft") or r.get("square_feet"),
                    photo_url=r.get("photo") or r.get("photo_url"),
                    source=r.get("source") or "realestateapi",
                    listed_date=r.get("listed_date"),
                    amenities=r.get("amenities") or [],
                )
                results.append(nl)
            except Exception:
                # Skip records that don't validate
                continue
    return results
