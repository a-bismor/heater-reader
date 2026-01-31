from pathlib import Path
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_insert_and_fetch_reading(tmp_path):
    db_path = tmp_path / "readings.db"
    db = Database(db_path)
    db.init_schema()

    reading_id = db.insert_reading(
        ReadingText(45, 55, 42, 50, "PRACA"),
        image_path="data/images/2026/01/31/100506.jpg",
    )

    row = db.get_reading(reading_id)
    assert row["boiler_current"] == 45
    assert row["mode"] == "PRACA"
