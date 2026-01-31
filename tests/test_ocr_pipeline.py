from pathlib import Path
from heater_reader.ocr_pipeline import extract_text_from_image


def test_extract_text_from_image_returns_string(tmp_path):
    image_path = Path("tests/fixtures/sample_lcd.jpg")
    if not image_path.exists():
        return  # placeholder until fixture added

    text = extract_text_from_image(image_path)

    assert isinstance(text, str)
    assert text.strip() != ""
