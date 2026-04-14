"""
Shared pytest fixtures and configuration
"""
import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(scope="function")
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def reset_activities():
    """Fixture to reset activities before and after each test"""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)
