from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_crop_ui_includes_button():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Load Latest Snapshot" in response.text


def test_crop_ui_has_snapshot_wiring():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert "/api/snapshot" in response.text


def test_crop_ui_marks_click_mode():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert "data-crop-mode=\"click\"" in response.text


def test_crop_ui_styles_snapshot_to_fit():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert "max-width: 100%" in response.text
