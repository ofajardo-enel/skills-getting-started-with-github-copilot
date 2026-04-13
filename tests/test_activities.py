"""
Tests for GET /activities endpoint.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Client fixture provides TestClient with pre-populated activities
        Act: Call GET /activities
        Assert: Response should contain all activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data
        assert len(data) == 9

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: Client fixture ready
        Act: Call GET /activities
        Assert: Each activity should have required fields
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify each activity has the required structure
        for activity_name, activity_details in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """
        Arrange: Client fixture with activities containing participants
        Act: Call GET /activities
        Assert: Participants should be returned as a list of emails
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Chess Club has 2 participants
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_respects_max_participants(self, client):
        """
        Arrange: Client fixture ready
        Act: Call GET /activities
        Assert: Each activity should have max_participants field > 0
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()

        for activity_details in data.values():
            assert activity_details["max_participants"] > 0
            assert activity_details["max_participants"] >= len(
                activity_details["participants"]
            )

    def test_get_activities_response_is_json(self, client):
        """
        Arrange: Client fixture ready
        Act: Call GET /activities
        Assert: Response should be valid JSON
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        # Should not raise an exception
        data = response.json()
        assert isinstance(data, dict)
