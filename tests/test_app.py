import pytest


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Should return all activities"""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_structure(self, client):
        """Should return activities with correct structure"""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        for field in expected_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Should successfully sign up a new participant"""
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added to activity
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email(self, client):
        """Should reject duplicate signup for existing participant"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Should reject signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Should allow multiple students to sign up for same activity"""
        # Arrange
        activity_name = "Basketball Team"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Act
        for email in emails:
            client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
            )
        
        # Assert
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        for email in emails:
            assert email in participants
        assert len(participants) == len(emails)


class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Should successfully remove an existing participant"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email_to_remove not in activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant(self, client):
        """Should reject removal of participant not in activity"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nothere@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_remove_from_nonexistent_activity(self, client):
        """Should reject removal from non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity.replace(' ', '%20')}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_all_participants(self, client):
        """Should be able to remove all participants from an activity"""
        # Arrange
        activity_name = "Chess Club"
        participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        for email in participants_to_remove:
            client.delete(
                f"/activities/{activity_name.replace(' ', '%20')}/participants/{email}"
            )
        
        # Assert
        activities = client.get("/activities").json()
        assert len(activities[activity_name]["participants"]) == 0


class TestSignupAndRemove:
    """Integration tests combining signup and removal workflows"""
    
    def test_signup_then_remove(self, client):
        """Should be able to sign up and then remove a participant"""
        # Arrange
        activity_name = "Basketball Team"
        email = "integration@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Assert - Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants/{email}"
        )
        assert remove_response.status_code == 200
        
        # Assert - Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
    
    def test_signup_after_removal(self, client):
        """Should be able to sign up again after removal"""
        # Arrange
        activity_name = "Art Club"
        email = "regsignup@mergington.edu"
        
        # Act - First signup
        first_signup = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        assert first_signup.status_code == 200
        
        # Act - Remove
        remove = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants/{email}"
        )
        assert remove.status_code == 200
        
        # Act - Second signup
        second_signup = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert
        assert second_signup.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
    
    def test_concurrent_signups_and_removals(self, client):
        """Should handle multiple signups and removals correctly"""
        # Arrange
        activity_name = "Soccer Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act - Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert - Verify all signed up
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert len(participants) == len(emails)
        
        # Act - Remove first student
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants/{emails[0]}"
        )
        
        # Assert - Verify correct removal
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert len(participants) == 2
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants
