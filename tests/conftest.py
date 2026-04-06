import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to clean state before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in local games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train for soccer matches and improve teamwork",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and creative expression",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays, learn theater skills, and perform",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation skills and debate current topics",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        }
    }
    
    # Clear and repopulate
    activities.clear()
    activities.update(original)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original)
