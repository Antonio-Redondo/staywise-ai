def test_graph_pipeline_fallback():
    from app.graph.graph import run_pipeline

    class FakeClient:
        async def fetch_listings_for_neighborhood(self, neighborhood, limit=5):
            return [
                {"id": "l1", "url": "https://x/1", "address": "a1", "price": 500000, "beds": 2, "sqft": 800, "photo": "https://x/1.jpg", "amenities": ["elevator"]},
                {"id": "l2", "url": "https://x/2", "address": "a2", "price": 600000, "beds": 3, "sqft": 1100, "photo": "https://x/2.jpg", "amenities": []},
                {"id": "l3", "url": "https://x/3", "address": "a3", "price": 700000, "beds": 1, "sqft": 650, "photo": "https://x/3.jpg", "amenities": []},
            ]

        async def close(self):
            return None

    state = run_pipeline("3 bed under $1,000,000 near BART", client=FakeClient())
    assert "explained" in state
    assert len(state["explained"]) >= 1
    # Expect at least 3 listings returned in listings/scored
    assert len(state["listings"]) >= 1
    assert len(state["scored"]) >= 1
