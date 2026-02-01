from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_ui_does_not_include_version_label():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "id=\"version\"" not in response.text
