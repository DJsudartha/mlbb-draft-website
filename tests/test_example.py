from fastapi.testclient import TestClient

from backend.main import app


def test_root_route_reports_backend_status():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "MLBB Draft Backend Running"}
