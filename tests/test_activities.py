"""
Tests for the GET /activities endpoint
"""
import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


class TestGetActivities:
    """Test cases for retrieving activities"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_expected_keys(self, client):
        """Test that activities have expected structure"""
        # Arrange
        endpoint = "/activities"
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get(endpoint)
        data = response.json()
        first_activity = next(iter(data.values()))

        # Assert
        for field in required_fields:
            assert field in first_activity, f"Missing required field: {field}"

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(
                activity_data["participants"],
                list
            ), f"Participants for {activity_name} should be a list"

    def test_activities_have_valid_data_types(self, client):
        """Test that activity fields have correct data types"""
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0
