from pathlib import Path
import pytesseract
import cv2
import numpy as np


def apply_crop(image: np.ndarray, crop: dict[str, int] | None) -> np.ndarray:
    if not crop:
        return image
    x = crop.get("x", 0)
    y = crop.get("y", 0)
    w = crop.get("w", 0)
    h = crop.get("h", 0)
    return image[y : y + h, x : x + w]


def extract_text_from_image(path: Path, config_path: Path | None = None) -> str:
    image = cv2.imread(str(path))
    if config_path:
        from heater_reader.config import load_config

        cfg = load_config(config_path)
        image = apply_crop(image, cfg.capture.crop)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)
