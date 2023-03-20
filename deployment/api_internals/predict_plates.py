from pathlib import Path
import numpy as np

import cv2
from ultralytics import YOLO
import easyocr

# --- INIT PLATE MODEL

lpd_model_name = "license_plate_detect_model.pt"
model_lpd = YOLO(Path("models", lpd_model_name))

# --- INIT EASY OCR MODEL

reader = easyocr.Reader(["en"])

# --- FUNCTIONS


def get_text(image: np.array, coords: np.array) -> str:
    """
    Try to obtain the license plate number from the license plate image.

    Parameters
    ----------
    image: np.array
        the array of the original image
    coords: np.array / torch.Tensor
        the coordinates of the damage detected on the original image by the license_plate_detect model

    Returns
    -------
    str:
        The estimated plate number
    """

    # Extract plate coordinates
    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])

    # Preprocess plate image (crop / gray / ...)
    nimg = np.array(image)
    img = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_precise = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(img_precise, cv2.COLOR_RGB2GRAY)
    # cv2.imwrite("plate.png", gray)

    # Try to read text from image
    result = reader.readtext(gray)

    # Parse results
    text = "NOT READABLE"
    for res in result:
        if len(res[1]) in [8, 9] and res[2] > 0.1:
            text = res[1]

    return text


# --- MAIN FUNCTION


def predict_plates(
    filtered_files: list, preprocessed_files: list, original_ratios: list
) -> list:

    results = model_lpd.predict(preprocessed_files, agnostic_nms=True)
    predictions = []

    for i, r in enumerate(results):

        boxes = r.boxes
        for box in boxes:

            # get box coordinates in (top, left, bottom, right) format
            coords = box.xyxy[0]

            coords_ratio = coords.tolist()
            coords_ratio[0] *= original_ratios[i][1]
            coords_ratio[1] *= original_ratios[i][0]
            coords_ratio[2] *= original_ratios[i][1]
            coords_ratio[3] *= original_ratios[i][0]

            text = get_text(preprocessed_files[i], coords)

            pred_dict = {
                "text": text,
                "coords": coords_ratio,
                "file": filtered_files[i].filename,
            }
            predictions.append(pred_dict)

    return predictions
