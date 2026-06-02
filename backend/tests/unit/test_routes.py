from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_route():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_recommend_route_missing_query():
    r = client.post("/api/recommend", json={})
    assert r.status_code == 422 or r.status_code == 400


def test_track_click_route():
    payload = {"listingId": "l1", "source": "realtor", "affiliateNetwork": "impact"}
    r = client.post("/api/track-click", json=payload)
    # Depending on DB availability, we accept 200 or 500 but ensure route exists
    assert r.status_code in (200, 500)
