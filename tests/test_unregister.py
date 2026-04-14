"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint
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


class TestUnregisterSuccess:
    """Test cases for successful unregistration"""

    def test_unregister_existing_participant(self, client):
        """Test successfully unregistering a participant"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/unregister"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_after_signup(self, client):
        """Test unregistering a participant who just signed up"""
        # Arrange
        email = "newuser@mergington.edu"
        activity_name = "Programming Class"
        signup_endpoint = f"/activities/{quote(activity_name)}/signup"
        unregister_endpoint = f"/activities/{quote(activity_name)}/unregister"
        
        # Sign up first
        client.post(signup_endpoint, params={"email": email})
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(unregister_endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]


class TestUnregisterFailures:
    """Test cases for unregister failures"""

    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who isn't signed up"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/unregister"

        # Act
        response = client.delete(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        endpoint = f"/activities/{quote(activity_name)}/unregister"

        # Act
        response = client.delete(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_twice_fails(self, client):
        """Test that unregistering twice fails on second attempt"""
        # Arrange
        email = "daniel@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        endpoint = f"/activities/{quote(activity_name)}/unregister"
        
        # First unregister succeeds
        first_response = client.delete(endpoint, params={"email": email})
        assert first_response.status_code == 200

        # Act - second unregister
        second_response = client.delete(endpoint, params={"email": email})

        # Assert
        assert second_response.status_code == 400
        assert second_response.json()["detail"] == "Student is not signed up for this activity"
