"""
Tests for POST /activities/{activity_name}/signup endpoint.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_returns_200(self, client, valid_activity_name, valid_email):
        """
        Arrange: Valid activity and email prepared
        Act: POST request to signup endpoint
        Assert: Should return 200 with success message
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/signup?email={valid_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert valid_email in data["message"]
        assert valid_activity_name in data["message"]

    def test_signup_adds_participant_to_activity(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: Valid activity and email prepared
        Act: POST request to signup endpoint
        Assert: Participant should be added to activity's participants list
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/signup?email={valid_email}"
        )

        # Assert
        assert response.status_code == 200

        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert valid_email in activities_data[valid_activity_name]["participants"]

    def test_signup_invalid_activity_returns_404(self, client, invalid_activity_name, valid_email):
        """
        Arrange: Invalid activity name and valid email
        Act: POST request with non-existent activity
        Assert: Should return 404 error
        """
        # Act
        response = client.post(
            f"/activities/{invalid_activity_name}/signup?email={valid_email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student_returns_400(
        self, client, valid_activity_name, enrolled_student
    ):
        """
        Arrange: Student already enrolled in the activity
        Act: POST request to signup the same student again
        Assert: Should return 400 with duplicate enrollment error
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/signup?email={enrolled_student}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_at_capacity_returns_400(self, client):
        """
        Arrange: Activity is at full capacity (mock a full activity)
        Act: POST request to signup to a full activity
        Assert: Should return 400 with capacity error
        """
        # Arrange: Tennis Club has max 12 and currently has 1
        # Add 11 more participants to reach capacity
        activity_name = "Tennis Club"
        for i in range(11):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email=another@mergington.edu"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "full capacity" in data["detail"]

    def test_signup_multiple_students_different_activities(
        self, client, valid_email
    ):
        """
        Arrange: Valid email prepared
        Act: Sign up same student to multiple different activities
        Assert: Student should be able to join multiple activities
        """
        # Act
        response1 = client.post(
            f"/activities/Chess Club/signup?email={valid_email}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={valid_email}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert valid_email in activities_data["Chess Club"]["participants"]
        assert valid_email in activities_data["Programming Class"]["participants"]

    def test_signup_increments_participant_count(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: Get initial participant count
        Act: POST request to signup
        Assert: Participant count should increase by 1
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(
            initial_response.json()[valid_activity_name]["participants"]
        )

        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/signup?email={valid_email}"
        )

        # Assert
        assert response.status_code == 200

        # Verify count increased
        final_response = client.get("/activities")
        final_count = len(
            final_response.json()[valid_activity_name]["participants"]
        )
        assert final_count == initial_count + 1
