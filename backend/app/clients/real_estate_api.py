import os
import asyncio
from typing import Any, Dict, List, Optional
import httpx

API_KEY = os.getenv("REAL_ESTATE_API_KEY")
BASE_URL = os.getenv("REAL_ESTATE_API_URL", "https://api.realestate.example")


# Curated demo catalog used when no real-estate API key is set. Photo selection
# happens on the frontend (it assigns an example image per listing id), so
# photo_url is left as a placeholder here.
_DEMO_CATALOG: List[Dict[str, Any]] = [
    {"street": "412 Valencia St", "area": "Mission", "price": 3200, "bedrooms": 1, "bathrooms": 1.0, "square_feet": 680, "amenities": ["near_transit", "in_unit_laundry", "dishwasher"]},
    {"street": "88 Townsend St", "area": "South Beach", "price": 4100, "bedrooms": 2, "bathrooms": 2.0, "square_feet": 980, "amenities": ["near_transit", "parking", "gym", "doorman"]},
    {"street": "1500 Page St", "area": "Haight-Ashbury", "price": 2950, "bedrooms": 1, "bathrooms": 1.0, "square_feet": 720, "amenities": ["quiet", "pet_friendly", "hardwood_floors"]},
    {"street": "350 Mission Bay Blvd", "area": "Mission Bay", "price": 4650, "bedrooms": 2, "bathrooms": 2.0, "square_feet": 1100, "amenities": ["near_transit", "gym", "parking", "rooftop_deck", "in_unit_laundry"]},
    {"street": "22 Cole St", "area": "Cole Valley", "price": 3550, "bedrooms": 2, "bathrooms": 1.0, "square_feet": 860, "amenities": ["quiet", "hardwood_floors", "pet_friendly"]},
    {"street": "701 Folsom St", "area": "SoMa", "price": 3850, "bedrooms": 1, "bathrooms": 1.0, "square_feet": 760, "amenities": ["near_transit", "gym", "in_unit_laundry", "parking"]},
    {"street": "1234 Castro St", "area": "Noe Valley", "price": 5200, "bedrooms": 3, "bathrooms": 2.0, "square_feet": 1450, "amenities": ["quiet", "backyard", "parking", "in_unit_laundry"]},
    {"street": "555 Hayes St", "area": "Hayes Valley", "price": 3300, "bedrooms": 1, "bathrooms": 1.0, "square_feet": 700, "amenities": ["near_transit", "dishwasher", "hardwood_floors"]},
    {"street": "980 Bush St", "area": "Nob Hill", "price": 2800, "bedrooms": 1, "bathrooms": 1.0, "square_feet": 620, "amenities": ["near_transit", "doorman", "elevator"]},
    {"street": "47 Irving St", "area": "Inner Sunset", "price": 3650, "bedrooms": 2, "bathrooms": 1.0, "square_feet": 910, "amenities": ["quiet", "pet_friendly", "parking", "near_park"]},
    {"street": "260 King St", "area": "South Beach", "price": 4400, "bedrooms": 2, "bathrooms": 2.0, "square_feet": 1050, "amenities": ["near_transit", "gym", "pool", "doorman", "parking"]},
    {"street": "1701 Octavia St", "area": "Pacific Heights", "price": 6100, "bedrooms": 3, "bathrooms": 2.5, "square_feet": 1700, "amenities": ["quiet", "backyard", "parking", "in_unit_laundry", "fireplace"]},
]


def _demo_listings(neighborhood: str, limit: int) -> List[Dict[str, Any]]:
    """Deterministic sample listings used when no real-estate API key is set."""
    count = max(1, min(limit, len(_DEMO_CATALOG)))
    return [
        {
            "id": f"demo-{i}",
            "source_url": "https://example.com/listing",
            "address": f"{item['street']}, {item['area']}",
            "price": item["price"],
            "bedrooms": item["bedrooms"],
            "bathrooms": item["bathrooms"],
            "square_feet": item["square_feet"],
            "photo_url": "https://example.com/photo.jpg",
            "source": "demo",
            "amenities": item["amenities"],
        }
        for i, item in enumerate(_DEMO_CATALOG[:count])
    ]


class RealEstateAPIClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        self.api_key = api_key or API_KEY
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def fetch_listings_for_neighborhood(self, neighborhood: str, limit: int = 50) -> List[Dict[str, Any]]:
        # Demo mode: with no API key configured there is no real provider to call,
        # so return deterministic sample listings instead of hitting the placeholder
        # host (which would raise getaddrinfo and 500 the recommend endpoint).
        if not self.api_key:
            return _demo_listings(neighborhood, limit)

        url = f"{BASE_URL}/listings"
        params = {"neighborhood": neighborhood, "limit": limit}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        retries = 2
        backoff = 0.5
        for attempt in range(retries + 1):
            try:
                resp = await self._client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data.get("listings", [])
            except httpx.HTTPStatusError as e:
                if resp.status_code == 429 and attempt < retries:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise
            except Exception:
                if attempt < retries:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise

    async def close(self):
        await self._client.aclose()
