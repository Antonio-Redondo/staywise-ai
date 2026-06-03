import importlib
import sys
import types
import os


def test_init_observability_sets_langsmith_client(monkeypatch):
    # Create a fake langsmith module with a Client class
    fake = types.ModuleType("langsmith")

    class Client:
        def __init__(self, api_key: str):
            self.api_key = api_key

        def set_project(self, project: str):
            self.project = project

    fake.Client = Client

    sys.modules["langsmith"] = fake

    # Ensure environment variables are set
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls_test_key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setenv("LANGSMITH_TRACING", "true")

    # Reload the observability module to pick up the fake module
    import backend.app.observability as obs
    importlib.reload(obs)

    # Call the initializer
    obs.init_observability()

    assert "langsmith_client" in obs.__dict__
    client = obs.__dict__["langsmith_client"]
    assert hasattr(client, "api_key") and client.api_key == "ls_test_key"
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
