from urllib.parse import quote


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_and_remove_participant(client):
    email = "teststudent@mergington.edu"
    activity = "Basketball Team"
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")

    signup_response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )

    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity}"

    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]

    delete_response = client.delete(
        f"/activities/{encoded_activity}/participants/{encoded_email}"
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity}"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "duplicate@mergington.edu"
    activity = "Soccer Club"
    encoded_activity = quote(activity, safe="")

    first_response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_nonexistent_participant_returns_404(client):
    activity = "Basketball Team"
    encoded_activity = quote(activity, safe="")
    email = "missing@mergington.edu"
    encoded_email = quote(email, safe="")

    response = client.delete(
        f"/activities/{encoded_activity}/participants/{encoded_email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_unknown_activity_returns_404(client):
    activity = "Unknown Activity"
    email = "test@mergington.edu"
    encoded_activity = quote(activity, safe="")
    encoded_email = quote(email, safe="")

    response = client.delete(
        f"/activities/{encoded_activity}/participants/{encoded_email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
