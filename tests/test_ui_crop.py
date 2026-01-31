from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_crop_ui_includes_button():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Load Latest Snapshot" in response.text
