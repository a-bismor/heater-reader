from __future__ import annotations

import json
from pathlib import Path

from heater_reader.db import Database


def seed_readings_from_json(db_path: str | Path, json_path: str | Path) -> int:
    db = Database(Path(db_path))
    db.init_schema()
    payload = json.loads(Path(json_path).read_text())
    inserted = 0
    for row in payload:
        db.insert_seed_reading(
            captured_at=row["captured_at"],
            boiler_current=row.get("boiler_current"),
            boiler_set=row.get("boiler_set"),
            radiator_current=row.get("radiator_current"),
            radiator_set=row.get("radiator_set"),
            mode=row["mode"],
            image_path=row["image_path"],
        )
        inserted += 1
    return inserted
