from fastapi.testclient import TestClient
from pathlib import Path
from heater_reader.app import create_app


def test_crop_endpoint_persists_config(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("capture:\n  interval_seconds: 60\n")

    app = create_app("data/readings.db")
    app.state.config_path = config_path
    client = TestClient(app)

    response = client.post("/api/crop", json={"x": 1, "y": 2, "w": 3, "h": 4})
    assert response.status_code == 200

    text = config_path.read_text()
    assert "crop" in text
