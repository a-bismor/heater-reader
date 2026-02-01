import os
from heater_reader.capture import build_opencv_capture_options, set_opencv_capture_options


def test_build_opencv_capture_options_tcp():
    assert build_opencv_capture_options("tcp") == "rtsp_transport;tcp"


def test_set_opencv_capture_options_sets_env(monkeypatch):
    monkeypatch.delenv("OPENCV_FFMPEG_CAPTURE_OPTIONS", raising=False)

    set_opencv_capture_options("tcp")

    assert os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS") == "rtsp_transport;tcp"
