from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from heater_reader.ocr import ReadingText


@dataclass
class Database:
    path: Path

    def _connect(self) -> sqlite3.Connection:
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

    def get_reading(self, reading_id: int) -> sqlite3.Row:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM readings WHERE id = ?", (reading_id,))
            return cur.fetchone()
