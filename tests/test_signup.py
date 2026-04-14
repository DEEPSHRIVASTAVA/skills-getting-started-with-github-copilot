from copy import deepcopy
from urllib.parse import quote
import unittest

from fastapi.testclient import TestClient

from src.app import app, activities


class SignupTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_activities = deepcopy(activities)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)

    def test_signup_success(self):
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        response = self.client.post(
            f"/activities/{quote(activity_name)}/signup", params={"email": email}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"], f"Signed up {email} for {activity_name}"
        )
        self.assertIn(email, activities[activity_name]["participants"])

    def test_duplicate_signup_returns_400(self):
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        response = self.client.post(
            f"/activities/{quote(activity_name)}/signup", params={"email": email}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Student is already signed up")


if __name__ == "__main__":
    unittest.main()
