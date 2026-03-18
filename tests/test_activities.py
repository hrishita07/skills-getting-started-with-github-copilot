"""Tests for the FastAPI activities API following Arrange-Act-Assert (AAA).

These tests use TestClient for synchronous requests and a fixture to
snapshot and restore the in-memory `activities` dict from `src.app`
to avoid cross-test pollution.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def activities_snapshot():
    """Snapshot and restore activities around each test (autouse).

    Uses deepcopy to capture the full structure and restores it after
    the test completes to ensure isolation.
    """
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities_returns_200_and_contains_known_activity(client):
    # Arrange: client fixture ready

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Basketball Team" in data
    assert "description" in data["Basketball Team"]
    assert "participants" in data["Basketball Team"]


def test_signup_adds_participant(client):
    # Arrange
    activity = "Art Studio"
    email = "test_signup@mergington.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for {activity}"


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Basketball Team"
    email = "james@mergington.edu"
    assert email in activities[activity]["participants"]
    before_count = len(activities[activity]["participants"])

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == before_count - 1
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"
