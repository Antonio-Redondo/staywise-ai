"""Test fixtures and configuration."""

import pytest


@pytest.fixture
def mock_user_query() -> str:
    """Sample user query for testing."""
    return "3 bedroom house under $1M near transit in San Francisco"


@pytest.fixture
def mock_intent() -> dict:
    """Sample parsed intent."""
    return {
        "budget_min": 500000,
        "budget_max": 1000000,
        "bedrooms_min": 3,
        "bedrooms_max": 5,
        "lifestyle_tags": ["urban", "walkable", "transit"],
        "must_haves": [],
        "nice_to_haves": ["modern_amenities"],
        "commute_target": None,
    }


@pytest.fixture
def mock_listing() -> dict:
    """Sample normalized listing."""
    return {
        "id": "listing-001",
        "source_url": "https://example.com/listing/001",
        "address": "123 Main St, San Francisco, CA 94102",
        "price": 850000,
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1200,
        "photo_url": "https://example.com/photos/001.jpg",
        "source": "realestate-api",
        "listed_date": "2026-05-01",
        "amenities": ["parking", "gym", "laundry_in_unit"],
    }
