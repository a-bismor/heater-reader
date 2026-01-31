from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class CaptureConfig:
    interval_seconds: int = 60
    image_root: Path = Path("data/images")
    rtsp_url: str | None = None
    onvif_snapshot_url: str | None = None


@dataclass
class AppConfig:
    capture: CaptureConfig = field(default_factory=CaptureConfig)


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text()) if path.exists() else {}
    capture_raw = (raw or {}).get("capture", {})

    capture = CaptureConfig(
        interval_seconds=int(capture_raw.get("interval_seconds", 60)),
        image_root=Path(capture_raw.get("image_root", "data/images")),
        rtsp_url=capture_raw.get("rtsp_url"),
        onvif_snapshot_url=capture_raw.get("onvif_snapshot_url"),
    )
    return AppConfig(capture=capture)
