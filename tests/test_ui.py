from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_index_html_served():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Boiler" in response.text
