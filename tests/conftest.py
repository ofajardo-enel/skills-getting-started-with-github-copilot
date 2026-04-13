"""
Pytest configuration and shared fixtures for the API tests.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from copy import deepcopy

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities as original_activities


@pytest.fixture
def client():
    """
    Fixture providing a TestClient instance for API testing.
    Returns a test client that can be used to make requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def activities_db():
    """
    Fixture providing a fresh copy of activities data for each test.
    This ensures test isolation - modifications in one test don't affect others.
    """
    return deepcopy(original_activities)


@pytest.fixture(autouse=True)
def reset_activities(activities_db, monkeypatch):
    """
    Auto-use fixture that resets the activities database before each test.
    This ensures each test starts with a clean state.
    """
    monkeypatch.setattr("app.activities", activities_db)


@pytest.fixture
def valid_email():
    """Fixture providing a valid email for testing."""
    return "student@mergington.edu"


@pytest.fixture
def valid_activity_name():
    """Fixture providing a valid activity name from the database."""
    return "Chess Club"


@pytest.fixture
def invalid_activity_name():
    """Fixture providing an invalid activity name for error testing."""
    return "Nonexistent Activity"


@pytest.fixture
def enrolled_student():
    """Fixture providing an already-enrolled student email."""
    return "michael@mergington.edu"  # Enrolled in Chess Club
