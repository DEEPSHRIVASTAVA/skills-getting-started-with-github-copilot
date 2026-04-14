"""
Edge case tests for the API
"""
from copy import deepcopy
from urllib.parse import quote
import pytest

from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities before and after each test"""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_root_endpoint_redirects_to_static(self, client):
        """Test that root endpoint redirects to static page"""
        # Arrange
        endpoint = "/"

        # Act
        response = client.get(endpoint, follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_activity_name_with_spaces(self, client):
        """Test activity names with spaces are handled correctly"""
        # Arrange
        email = "spacey@mergington.edu"
        activity_name = "Chess Club"  # Has a space
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_case_sensitive_activity_names(self, client):
        """Test that activity names are case-sensitive"""
        # Arrange
        email = "case@mergington.edu"
        activity_name = "chess club"  # lowercase (wrong case)
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_email_with_special_characters(self, client):
        """Test email with + sign and other valid special characters"""
        # Arrange
        email = "test+tag@mergington.edu"
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    @pytest.mark.parametrize("activity_name", [
        "Soccer Team",
        "Swimming Club",
        "Drama Club",
        "Art Studio",
        "Science Olympiad",
        "Debate Team",
    ])
    def test_signup_for_all_activities(self, client, activity_name):
        """Test that signup works for every activity (parameterized)"""
        # Arrange
        email = f"test_{activity_name.replace(' ', '_').lower()}@mergington.edu"
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
