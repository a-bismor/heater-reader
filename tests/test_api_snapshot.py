from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_snapshot_endpoint_returns_jpeg(monkeypatch):
    def fake_snapshot(rtsp_url):
        return b"jpeg", 10, 10

    app = create_app("data/readings.db", rtsp_url="rtsp://example")
    app.state.get_snapshot = fake_snapshot
    client = TestClient(app)

    response = client.get("/api/snapshot")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")
