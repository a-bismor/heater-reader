import numpy as np
from heater_reader.ocr_pipeline import apply_crop


def test_apply_crop_slices_image():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    crop = {"x": 10, "y": 5, "w": 50, "h": 20}

    sliced = apply_crop(img, crop)

    assert sliced.shape[0] == 20
    assert sliced.shape[1] == 50
