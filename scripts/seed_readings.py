from __future__ import annotations

import argparse
from pathlib import Path

from heater_reader.seed_readings import seed_readings_from_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed readings from JSON.")
    parser.add_argument(
        "--db",
        default="data/readings.db",
        help="Path to sqlite db to seed (default: data/readings.db).",
    )
    parser.add_argument(
        "--json",
        default="fixtures/readings.json",
        help="Path to readings json (default: fixtures/readings.json).",
    )
    args = parser.parse_args()
    inserted = seed_readings_from_json(Path(args.db), Path(args.json))
    print(f"Seeded {inserted} readings into {args.db}.")


if __name__ == "__main__":
    main()
