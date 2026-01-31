from pathlib import Path
from heater_reader.capture import capture_and_ocr
from heater_reader.ocr import ReadingText


def test_capture_and_ocr_handles_missing_frame(tmp_path):
    image_path = tmp_path / "missing.jpg"

    result = capture_and_ocr(image_path)

    assert result is None
