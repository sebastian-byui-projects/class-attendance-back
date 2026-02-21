from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_qr_code_structure():
    response = client.get("/generate-qr")

    # Assert successful connection
    assert response.status_code == 200

    data = response.json()

    # Assert that all necessary keys are present
    assert "qr_image" in data
    assert "token" in data
    assert "seconds_remaining" in data

    # Assert that the token is a string
    assert isinstance(data["token"], str)


def test_verify_attendance_success_flow():
    # Step 1: Get a valid token from the generator
    gen_response = client.get("/generate-qr")
    valid_token = gen_response.json()["token"]

    # Step 2: Send that token to the verification endpoint
    payload = {
        "student_id": "Test_Student_001",
        "token": valid_token
    }

    verify_response = client.post("/verify-attendance", json=payload)

    # Step 3: Assert that the backend accepts it
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "success"
    # Ensure the student ID is reflected in the welcome message
    assert "Test_Student_001" in verify_response.json()["message"]


def test_verify_attendance_invalid_token():
    payload = {
        "student_id": "Test_Student_002",
        "token": "000000"
    }

    response = client.post("/verify-attendance", json=payload)

    assert response.status_code == 400


def test_verify_attendance_missing_data():
    # Payload missing 'student_id'
    payload = {
        "token": "123456"
    }

    response = client.post("/verify-attendance", json=payload)

    assert response.status_code == 422
