import os
from typing import Any, Dict, List, Optional
import httpx

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/place"


class GooglePlacesClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        self.api_key = api_key or API_KEY
        self._client = httpx.AsyncClient(timeout=timeout)

    async def fetch_place_details(self, place_id: str) -> Dict[str, Any]:
        url = f"{BASE_URL}/details/json"
        params = {"place_id": place_id, "key": self.api_key}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
