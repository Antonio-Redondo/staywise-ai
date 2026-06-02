import os
from typing import Any, Dict, Optional
import httpx

API_KEY = os.getenv("WALK_SCORE_API_KEY")
BASE_URL = "https://api.walkscore.com"


class WalkScoreClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        self.api_key = api_key or API_KEY
        self._client = httpx.AsyncClient(timeout=timeout)

    async def fetch_walkscore(self, lat: float, lon: float) -> Dict[str, Any]:
        # Placeholder implementation; Walk Score API requires specific params
        url = f"{BASE_URL}/score"
        params = {"format": "json", "lat": lat, "lon": lon, "wsapikey": self.api_key}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
