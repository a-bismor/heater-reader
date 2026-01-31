from datetime import datetime
from pathlib import Path


def image_path_for(root: Path, ts: datetime) -> Path:
    return root / ts.strftime("%Y/%m/%d/%H%M%S.jpg")
