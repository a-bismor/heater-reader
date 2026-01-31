from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from heater_reader.ocr_pipeline import extract_text_from_image
from heater_reader.ocr import parse_reading, ReadingText


def image_path_for(root: Path, ts: datetime) -> Path:
    return root / ts.strftime("%Y/%m/%d/%H%M%S.jpg")


def capture_and_ocr(image_path: Path) -> ReadingText | None:
    if not image_path.exists():
        return None

    text = extract_text_from_image(image_path)
    return parse_reading(text)


@dataclass
class Snapshot:
    bytes: bytes
    width: int
    height: int
    captured_at: datetime


class SnapshotCache:
    def __init__(self, ttl_seconds: int = 10) -> None:
        self._ttl = ttl_seconds
        self._snapshot: Snapshot | None = None

    def get(self, now: datetime) -> Snapshot | None:
        if self._snapshot is None:
            return None
        age = (now - self._snapshot.captured_at).total_seconds()
        if age > self._ttl:
            return None
        return self._snapshot

    def set(self, data: bytes, width: int, height: int, captured_at: datetime | None = None) -> None:
        if captured_at is None:
            captured_at = datetime.now(timezone.utc)
        self._snapshot = Snapshot(data, width, height, captured_at)
