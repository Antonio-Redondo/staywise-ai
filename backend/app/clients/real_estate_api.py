import os
import asyncio
from typing import Any, Dict, List, Optional
import httpx

API_KEY = os.getenv("REAL_ESTATE_API_KEY")
BASE_URL = os.getenv("REAL_ESTATE_API_URL", "https://api.realestate.example")


class RealEstateAPIClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        self.api_key = api_key or API_KEY
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def fetch_listings_for_neighborhood(self, neighborhood: str, limit: int = 50) -> List[Dict[str, Any]]:
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
