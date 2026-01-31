from datetime import datetime
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
