import asyncio


def test_parse_intent_simple():
    from app.agents.intent import parse_intent
+
    intent = parse_intent("2 bed under $1,200,000 near BART")
    assert intent.bedrooms_min == 2
    assert intent.budget_max == 1200000


def test_neighborhood_scoring():
    from app.agents.neighborhood import score_neighborhoods
+
    neighborhoods = [{"name": "N1", "median_price": 800000, "walk_score": 90}]
    scored = score_neighborhoods(neighborhoods)
    assert len(scored) == 1
    assert 0.0 <= scored[0].score <= 1.0


def test_scoring_engine_simple():
    from app.agents.scoring import score_listing
    from app.models.listing import NormalizedListing
    from app.models.intent import Intent

    listing = NormalizedListing(
        id="1",
        source_url="https://example.com/1",
        address="123",
        price=900000,
        bedrooms=2,
        bathrooms=1.5,
        square_feet=900,
        photo_url="https://example.com/img.jpg",
        source="src",
        listed_date="2024-01-01",
        amenities=["elevator"],
    )
    intent = Intent(budget_min=800000, budget_max=1000000, must_haves=["elevator"]) 
    score = score_listing(listing, intent, neighborhood_score=0.8)
    assert 0.0 <= score <= 100.0


def test_explanation_generation():
    from app.agents.explanation import generate_explanation
    from app.models.listing import NormalizedListing
    from app.models.intent import Intent

    listing = NormalizedListing(
        id="1",
        source_url="https://example.com/1",
        address="123",
        price=900000,
        bedrooms=2,
        bathrooms=1.5,
        square_feet=900,
        photo_url="https://example.com/img.jpg",
        source="src",
        listed_date="2024-01-01",
        amenities=["elevator"],
    )
    intent = Intent(budget_min=800000, budget_max=1000000, must_haves=["elevator"]) 
    explanation = generate_explanation(listing, intent)
    assert "elevator" in explanation or "within budget" in explanation


def test_retrieval_normalize():
    from app.agents.retrieval import fetch_and_normalize_listings
    from app.clients.real_estate_api import RealEstateAPIClient

    class FakeClient:
        async def fetch_listings_for_neighborhood(self, neighborhood, limit=5):
            return [{"id": "l1", "url": "https://x/1", "address": "a", "price": 100}]

        async def close(self):
            return None

    client = FakeClient()
    listings = asyncio.run(fetch_and_normalize_listings(["N1"], client, limit_per=1))
    assert len(listings) == 1
    assert listings[0].id == "l1"

*** End Patch