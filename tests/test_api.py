from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_health_endpoint_ok():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
