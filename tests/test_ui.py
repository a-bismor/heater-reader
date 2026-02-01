from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_index_html_served():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Boiler" in response.text


def test_index_html_includes_label_strip():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "id=\"label-strip\"" in response.text


def test_index_html_hides_chart_x_ticks():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "ticks: { display: false }" in response.text
