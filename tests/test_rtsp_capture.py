from heater_reader.capture import encode_frame_to_jpeg


def test_encode_frame_to_jpeg_returns_bytes():
    import numpy as np

    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    data = encode_frame_to_jpeg(frame)

    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 0
