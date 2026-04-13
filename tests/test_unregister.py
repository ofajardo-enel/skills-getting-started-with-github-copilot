"""
Tests for POST /activities/{activity_name}/unregister endpoint.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_returns_200(
        self, client, valid_activity_name, enrolled_student
    ):
        """
        Arrange: Student enrolled in activity
        Act: POST request to unregister endpoint
        Assert: Should return 200 with success message
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/unregister?email={enrolled_student}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert enrolled_student in data["message"]
        assert valid_activity_name in data["message"]

    def test_unregister_removes_participant_from_activity(
        self, client, valid_activity_name, enrolled_student
    ):
        """
        Arrange: Student enrolled in activity
        Act: POST request to unregister
        Assert: Participant should be removed from activity's participants list
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/unregister?email={enrolled_student}"
        )

        # Assert
        assert response.status_code == 200

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert enrolled_student not in activities_data[valid_activity_name]["participants"]

    def test_unregister_invalid_activity_returns_404(
        self, client, invalid_activity_name, enrolled_student
    ):
        """
        Arrange: Invalid activity name
        Act: POST request to unregister from non-existent activity
        Assert: Should return 404 error
        """
        # Act
        response = client.post(
            f"/activities/{invalid_activity_name}/unregister?email={enrolled_student}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_enrolled_returns_400(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: Student not enrolled in the activity
        Act: POST request to unregister a student who is not enrolled
        Assert: Should return 400 with error
        """
        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/unregister?email={valid_email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not enrolled" in data["detail"]

    def test_unregister_decrements_participant_count(
        self, client, valid_activity_name, enrolled_student
    ):
        """
        Arrange: Get initial participant count
        Act: POST request to unregister
        Assert: Participant count should decrease by 1
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(
            initial_response.json()[valid_activity_name]["participants"]
        )

        # Act
        response = client.post(
            f"/activities/{valid_activity_name}/unregister?email={enrolled_student}"
        )

        # Assert
        assert response.status_code == 200

        # Verify count decreased
        final_response = client.get("/activities")
        final_count = len(
            final_response.json()[valid_activity_name]["participants"]
        )
        assert final_count == initial_count - 1

    def test_unregister_allows_others_to_join(self, client):
        """
        Arrange: Activity at capacity, then unregister one student
        Act: Try to signup another student
        Assert: New student should be able to join due to freed spot
        """
        # Arrange: Get a full activity, then unregister someone
        # Tennis Club has 1 participant, max 12
        activity_name = "Tennis Club"
        enrolled_student = "sarah@mergington.edu"

        # Fill to capacity
        for i in range(11):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act: Unregister to free a spot
        response1 = client.post(
            f"/activities/{activity_name}/unregister?email={enrolled_student}"
        )

        # Assert: Unregister successful
        assert response1.status_code == 200

        # Act: Now another student should be able to join
        response2 = client.post(
            f"/activities/{activity_name}/signup?email=newstudent@mergington.edu"
        )

        # Assert: New student can join
        assert response2.status_code == 200

    def test_unregister_then_rejoin_allowed(self, client, valid_activity_name):
        """
        Arrange: Student enrolled in activity
        Act: Unregister and then signup again
        Assert: Both operations should succeed
        """
        # Arrange
        test_email = "testuser@mergington.edu"

        # Act & Assert: Sign up
        signup_response = client.post(
            f"/activities/{valid_activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200

        # Act & Assert: Unregister
        unregister_response = client.post(
            f"/activities/{valid_activity_name}/unregister?email={test_email}"
        )
        assert unregister_response.status_code == 200

        # Act & Assert: Sign up again
        rejoin_response = client.post(
            f"/activities/{valid_activity_name}/signup?email={test_email}"
        )
        assert rejoin_response.status_code == 200

        # Final verification
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[valid_activity_name]["participants"]
