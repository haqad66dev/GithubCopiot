import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Use a snapshot of the original activities to restore between tests
ORIGINAL = copy.deepcopy(activities)


def setup_function():
    # Reset activities to original before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"].get("participants"), list)


def test_signup_and_refresh():
    activity = "Chess Club"
    email = "new_student@mergington.edu"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Check participants now contains the email
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]


def test_signup_already_signed_up():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already present in initial data

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_unregister_success_and_failure():
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Ensure it's present to start
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Trying to unregister again should fail
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup?email=test@x.com")
    assert resp.status_code == 404

    resp = client.delete("/activities/NoSuchActivity/signup?email=test@x.com")
    assert resp.status_code == 404
