from pathlib import Path
import pytesseract
import cv2


def extract_text_from_image(path: Path) -> str:
    image = cv2.imread(str(path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)
