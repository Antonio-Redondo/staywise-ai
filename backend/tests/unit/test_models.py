from datetime import date


def test_intent_properties():
    from app.models.intent import Intent

    i = Intent(budget_min=500000, budget_max=1000000, bedrooms_min=1, bedrooms_max=3)
    assert i.budget_mid == 750000
    assert i.bedrooms_mid == 2
    assert i.budget_range == 500000
    assert i.bedrooms_range == 2


def test_normalized_listing_validation():
    from app.models.listing import NormalizedListing

    data = {
        "id": "1",
        "source_url": "https://example.com/1",
        "address": "123 Main St",
        "price": 900000,
        "bedrooms": 2,
        "bathrooms": 1.5,
        "square_feet": 900,
        "photo_url": "https://example.com/img.jpg",
        "source": "RealEstate",
        "listed_date": "2024-01-01",
        "amenities": ["elevator"],
    }
    nl = NormalizedListing(**data)
    assert nl.id == "1"
    assert nl.source_url.scheme == "https"
    assert nl.listed_date == date(2024, 1, 1)


def test_neighborhood_model():
    from app.models.neighborhood import NeighborhoodScore

    n = NeighborhoodScore(name="SoMa", score=0.85, median_price=1000000, walk_score=95)
    assert n.score == 0.85
