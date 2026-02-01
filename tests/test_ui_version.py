from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_ui_includes_version_label():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "id=\"version\"" in response.text
    assert "v0.1+feat/version-label" in response.text
