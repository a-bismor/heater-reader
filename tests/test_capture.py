from datetime import datetime, timezone
from pathlib import Path
from heater_reader.capture import image_path_for


def test_image_path_for_creates_timestamped_path():
    root = Path("data/images")
    ts = datetime(2026, 1, 31, 10, 5, 6, tzinfo=timezone.utc)

    path = image_path_for(root, ts)

    assert str(path).endswith("/2026/01/31/100506.jpg")
