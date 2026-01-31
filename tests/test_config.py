from heater_reader.config import AppConfig, load_config


def test_load_config_uses_defaults_when_missing_fields(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("capture:\n  interval_seconds: 60\n")

    cfg = load_config(config_path)

    assert cfg.capture.interval_seconds == 60
    assert cfg.capture.image_root.name == "images"
