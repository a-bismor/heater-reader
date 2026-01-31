from fastapi.testclient import TestClient
from heater_reader.app import create_app
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_post_edit_updates_effective_values(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db = Database(db_path)
    db.init_schema()
    db.insert_reading(ReadingText(45, 55, 42, 50, "PRACA"), image_path="path.jpg")

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.post(
        "/api/readings/1/edit",
        json={"boiler_current": 48, "edited_by": "adam"},
    )

    assert response.status_code == 200
    assert response.json()["boiler_current"] == 48
