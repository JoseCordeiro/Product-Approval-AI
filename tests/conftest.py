"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.review_service import ReviewService


@pytest.fixture
def test_client():
    """Create a test client with proper app state."""
    # Ensure the app state is set up for testing
    app.state.review_service = ReviewService()

    with TestClient(app) as client:
        yield client


@pytest.fixture
def review_service():
    """Create a review service instance for testing."""
    return ReviewService()
