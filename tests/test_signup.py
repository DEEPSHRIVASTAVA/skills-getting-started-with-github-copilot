"""
Tests for the POST /activities/{activity_name}/signup endpoint
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
    # Arrange - save original state
    original = deepcopy(activities)
    
    yield
    
    # Cleanup - restore original state
    activities.clear()
    activities.update(original)


class TestSignupSuccess:
    """Test cases for successful signups"""

    def test_signup_success(self, client):
        """Test successfully signing up a new participant"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_adds_to_empty_participants_list(self, client):
        """Test signing up for an activity with no participants"""
        # Arrange
        email = "first@mergington.edu"
        activity_name = "Swimming Club"
        # Clear existing participants
        activities[activity_name]["participants"] = []
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == 1
        assert activities[activity_name]["participants"][0] == email


class TestSignupFailures:
    """Test cases for signup failures and edge cases"""

    def test_duplicate_signup_returns_400(self, client):
        """Test that duplicate signups are rejected"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Chess Club"  # Contains space
        endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

