import asyncio

import httpx


def test_real_estate_client_fetch():
    from app.clients.real_estate_api import RealEstateAPIClient

    client = RealEstateAPIClient(api_key="x")

    async def fake_get(url, params=None, headers=None):
        return httpx.Response(200, json={"listings": [{"id": "listing-1", "price": 100}]})

    client._client.get = fake_get
    listings = asyncio.run(client.fetch_listings_for_neighborhood("SoMa"))
    assert listings[0]["id"] == "listing-1"
    asyncio.run(client.close())


def test_walkscore_client_fetch():
    from app.clients.walk_score import WalkScoreClient

    client = WalkScoreClient(api_key="x")

    async def fake_get(url, params=None):
        return httpx.Response(200, json={"walkscore": 90})

    client._client.get = fake_get
    data = asyncio.run(client.fetch_walkscore(37.77, -122.41))
    assert "walkscore" in data
    asyncio.run(client.close())


def test_google_places_fetch():
    from app.clients.google_places import GooglePlacesClient

    client = GooglePlacesClient(api_key="x")

    async def fake_get(url, params=None):
        return httpx.Response(200, json={"result": {"place_id": "pid"}})

    client._client.get = fake_get
    data = asyncio.run(client.fetch_place_details("pid"))
    assert "result" in data
    asyncio.run(client.close())
