from pathlib import Path
from heater_reader.config import load_config


def test_load_config_parses_crop_settings(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
        capture:
          crop:
            x: 10
            y: 20
            w: 300
            h: 200
        """
    )

    cfg = load_config(config_path)

    assert cfg.capture.crop == {"x": 10, "y": 20, "w": 300, "h": 200}
