import json
from pathlib import Path

from heater_reader.db import Database
from heater_reader.seed_readings import seed_readings_from_json


def test_seed_readings_inserts_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "readings.db"
    image_path = tmp_path / "sample.jpg"
    image_path.write_bytes(b"fake")
    payload = [
        {
            "captured_at": "2026-02-01T20:15:00",
            "boiler_current": 52,
            "boiler_set": 60,
            "radiator_current": 38,
            "radiator_set": 45,
            "mode": "eco",
            "image_path": str(image_path),
        }
    ]
    json_path = tmp_path / "readings.json"
    json_path.write_text(json.dumps(payload))

    inserted = seed_readings_from_json(db_path, json_path)

    assert inserted == 1
    db = Database(db_path)
    rows = db.list_effective_readings()
    assert len(rows) == 1
    row = rows[0]
    assert row["captured_at"] == "2026-02-01T20:15:00"
    assert row["boiler_current"] == 52
    assert row["boiler_set"] == 60
    assert row["radiator_current"] == 38
    assert row["radiator_set"] == 45
    assert row["mode"] == "eco"
