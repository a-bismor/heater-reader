from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_health_endpoint_ok():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_app_initializes_schema(tmp_path):
    db_path = tmp_path / "data" / "readings.db"

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.get("/api/readings")

    assert response.status_code == 200
