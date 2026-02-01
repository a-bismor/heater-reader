from fastapi.testclient import TestClient
from heater_reader.app import create_app
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_readings_endpoint_returns_effective_values(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db = Database(db_path)
    db.init_schema()
    reading_id = db.insert_reading(ReadingText(45, 55, 42, 50, "PRACA"), image_path="path.jpg")
    db.insert_edit(reading_id, boiler_current=47, edited_by="adam")

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.get("/api/readings")
    assert response.status_code == 200
    assert response.json()[0]["boiler_current"] == 47


def test_readings_endpoint_includes_image_path(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db = Database(db_path)
    db.init_schema()
    db.insert_reading(ReadingText(45, 55, 42, 50, "PRACA"), image_path="path.jpg")

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.get("/api/readings")

    assert response.status_code == 200
    assert response.json()[0]["image_path"] == "path.jpg"
