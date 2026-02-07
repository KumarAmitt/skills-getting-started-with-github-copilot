from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    snapshot = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(snapshot)


def test_get_activities_returns_data(client):
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant(client):
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    assert response.status_code == 200

    response = client.get("/activities")
    participants = response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_duplicate_rejected(client):
    email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    assert response.status_code == 400


def test_unregister_removes_participant(client):
    email = "daniel@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": email},
    )
    assert response.status_code == 200

    response = client.get("/activities")
    participants = response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": "missing@mergington.edu"},
    )
    assert response.status_code == 404
