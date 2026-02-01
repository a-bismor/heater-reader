from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from heater_reader.ocr import ReadingText
from heater_reader.paths import ensure_dir


@dataclass
class Database:
    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    def _connect(self) -> sqlite3.Connection:
        ensure_dir(self.path.parent)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY,
                    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
                    boiler_current INTEGER,
                    boiler_set INTEGER,
                    radiator_current INTEGER,
                    radiator_set INTEGER,
                    mode TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    verified INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS edits (
                    id INTEGER PRIMARY KEY,
                    reading_id INTEGER NOT NULL,
                    boiler_current INTEGER,
                    boiler_set INTEGER,
                    radiator_current INTEGER,
                    radiator_set INTEGER,
                    mode TEXT,
                    edited_by TEXT NOT NULL,
                    edited_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (reading_id) REFERENCES readings(id)
                );

                CREATE TABLE IF NOT EXISTS capture_errors (
                    id INTEGER PRIMARY KEY,
                    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
                    error TEXT NOT NULL
                );
                """
            )

    def insert_reading(self, reading: ReadingText, image_path: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO readings (
                    boiler_current, boiler_set, radiator_current, radiator_set, mode, image_path
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    reading.boiler_current,
                    reading.boiler_set,
                    reading.radiator_current,
                    reading.radiator_set,
                    reading.mode,
                    image_path,
                ),
            )
            return int(cur.lastrowid)

    def insert_seed_reading(
        self,
        captured_at: str,
        boiler_current: int | None,
        boiler_set: int | None,
        radiator_current: int | None,
        radiator_set: int | None,
        mode: str,
        image_path: str,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO readings (
                    captured_at, boiler_current, boiler_set, radiator_current, radiator_set, mode, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    captured_at,
                    boiler_current,
                    boiler_set,
                    radiator_current,
                    radiator_set,
                    mode,
                    image_path,
                ),
            )
            return int(cur.lastrowid)

    def get_reading(self, reading_id: int) -> sqlite3.Row:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM readings WHERE id = ?", (reading_id,))
            return cur.fetchone()

    def insert_edit(
        self,
        reading_id: int,
        boiler_current: int | None = None,
        boiler_set: int | None = None,
        radiator_current: int | None = None,
        radiator_set: int | None = None,
        mode: str | None = None,
        edited_by: str = "adam",
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO edits (reading_id, boiler_current, boiler_set, radiator_current, radiator_set, mode, edited_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reading_id,
                    boiler_current,
                    boiler_set,
                    radiator_current,
                    radiator_set,
                    mode,
                    edited_by,
                ),
            )
            return int(cur.lastrowid)

    def get_effective_reading(self, reading_id: int):
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT
                    r.id,
                    COALESCE(e.boiler_current, r.boiler_current) AS boiler_current,
                    COALESCE(e.boiler_set, r.boiler_set) AS boiler_set,
                    COALESCE(e.radiator_current, r.radiator_current) AS radiator_current,
                    COALESCE(e.radiator_set, r.radiator_set) AS radiator_set,
                    COALESCE(e.mode, r.mode) AS mode,
                    r.image_path
                FROM readings r
                LEFT JOIN edits e ON e.reading_id = r.id
                WHERE r.id = ?
                ORDER BY e.edited_at DESC
                LIMIT 1
                """,
                (reading_id,),
            )
            return cur.fetchone()

    def list_effective_readings(self):
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT
                    r.id,
                    COALESCE(e.boiler_current, r.boiler_current) AS boiler_current,
                    COALESCE(e.boiler_set, r.boiler_set) AS boiler_set,
                    COALESCE(e.radiator_current, r.radiator_current) AS radiator_current,
                    COALESCE(e.radiator_set, r.radiator_set) AS radiator_set,
                    COALESCE(e.mode, r.mode) AS mode,
                    r.captured_at
                FROM readings r
                LEFT JOIN edits e ON e.reading_id = r.id
                ORDER BY r.captured_at ASC
                """
            )
            return cur.fetchall()
