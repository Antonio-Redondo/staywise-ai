def test_observability_imports():
    # Ensure observability module imports without raising and doesn't block
    from app import observability

    # init_observability should be callable
    assert hasattr(observability, "init_observability")

def test_run_pipeline_smoke():
    from app.graph.graph import run_pipeline

    class FakeClient:
        async def fetch_listings_for_neighborhood(self, neighborhood, limit=5):
            return [{"id": "l1", "url": "https://x/1", "address": "a", "price": 100}]

        async def close(self):
            return None

    state = run_pipeline("1 bed under $500,000", client=FakeClient())
    assert "intent" in state
    assert "listings" in state
