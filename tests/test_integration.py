"""
Integration tests for the complete signup and unregister flow
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


class TestCompleteFlows:
    """Integration tests for complete user journeys"""

    def test_signup_then_unregister_flow(self, client):
        """Test the complete flow of signing up and then unregistering"""
        # Arrange
        email = "testuser@mergington.edu"
        activity_name = "Programming Class"
        initial_count = len(activities[activity_name]["participants"])
        signup_endpoint = f"/activities/{quote(activity_name)}/signup"
        unregister_endpoint = f"/activities/{quote(activity_name)}/unregister"

        # Act - Sign up
        signup_response = client.post(signup_endpoint, params={"email": email})
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

        # Act - Unregister
        unregister_response = client.delete(unregister_endpoint, params={"email": email})

        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_multiple_activities_same_user(self, client):
        """Test one user signing up for multiple activities"""
        # Arrange
        email = "multi@mergington.edu"
        activity_names = ["Chess Club", "Programming Class", "Gym Class"]

        # Act - Sign up for all activities
        for activity_name in activity_names:
            endpoint = f"/activities/{quote(activity_name)}/signup"
            response = client.post(endpoint, params={"email": email})
            assert response.status_code == 200

        # Assert - User is in all activities
        for activity_name in activity_names:
            assert email in activities[activity_name]["participants"]

        # Act - Unregister from first activity
        unregister_endpoint = f"/activities/{quote(activity_names[0])}/unregister"
        response = client.delete(unregister_endpoint, params={"email": email})

        # Assert - Removed from first, still in others
        assert response.status_code == 200
        assert email not in activities[activity_names[0]]["participants"]
        assert email in activities[activity_names[1]]["participants"]
        assert email in activities[activity_names[2]]["participants"]

    def test_get_activities_reflects_signup_changes(self, client):
        """Test that GET /activities reflects signup changes in real-time"""
        # Arrange
        email = "reflect@mergington.edu"
        activity_name = "Drama Club"
        signup_endpoint = f"/activities/{quote(activity_name)}/signup"

        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]

        # Act - Sign up
        client.post(signup_endpoint, params={"email": email})

        # Act - Get updated state
        after_signup_response = client.get("/activities")
        after_signup_participants = after_signup_response.json()[activity_name]["participants"]

        # Assert
        assert email not in initial_participants
        assert email in after_signup_participants
        assert len(after_signup_participants) == len(initial_participants) + 1

    def test_concurrent_signups_different_activities(self, client):
        """Test multiple users signing up for different activities simultaneously"""
        # Arrange
        users = [
            {"email": "user1@mergington.edu", "activity": "Chess Club"},
            {"email": "user2@mergington.edu", "activity": "Programming Class"},
            {"email": "user3@mergington.edu", "activity": "Gym Class"},
        ]

        # Act - All users sign up
        responses = []
        for user in users:
            endpoint = f"/activities/{quote(user['activity'])}/signup"
            response = client.post(endpoint, params={"email": user["email"]})
            responses.append(response)

        # Assert - All signups successful
        assert all(r.status_code == 200 for r in responses)
        for user in users:
            assert user["email"] in activities[user["activity"]]["participants"]
