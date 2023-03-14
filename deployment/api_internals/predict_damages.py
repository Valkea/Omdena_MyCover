from pathlib import Path

import cv2
import numpy as np

from ultralytics import YOLO
import onnxruntime as rt

print("ONX:", rt.get_device())

# --- INIT DAMAGES MODEL

cdd_model_name = "car_damage_detect_2.pt"
model_cdd = YOLO(Path("models", cdd_model_name))

# --- INIT SEVERITY MODEL

sev_model_name = "severity_model.onnx"
model_severity_input_name = "sequential_2_input"
model_severity_output_name = "output_layer"

providers = [
    "TensorrtExecutionProvider",
    "CUDAExecutionProvider",
    "CPUExecutionProvider",
]

model_severity = rt.InferenceSession(
    str(Path("models", sev_model_name)), providers=providers
)

# --- DEFINE VARIABLES

DEFAULT_THRESHOLDS = {
    "hood_damage": 0.5,
    "front_bumper_damage": 0.5,
    "front_fender_damage": 0.5,
    "headlight_damage": 0.0,  # REPLACE
    "front_windscreen_damage": 0.0,  # REPLACE
    "sidemirror_damage": 0.0,  # REPLACE
    "sidedoor_panel_damage": 0.5,
    "roof_damage": 0.5,
    "runnigboard_damage": 0.5,
    "pillar_damage": 0.5,
    "sidedoor_window_damage": 0.0,  # REPLACE
    "rear_fender_damage": 0.5,
    "rear_windscreen_damage": 0.0,  # REPLACE
    "taillight_damage": 0.0,  # REPLACE
    "rear_bumper_damage": 0.5,
    "backdoor_panel_damage": 0.5,
}

# --- DEFINE FUNCTIONS


def get_action(severity: float, class_name: str) -> str:
    """
    Returns the proper action according to the severity and the given threshold.

    Parameters
    ----------
    severity: float
        the severity value returned by the severity model
    class_name: str
        the name of the class detected by the car_damage_detect model

    Returns
    -------
    str:
        The suggested action
    """

    threshold = DEFAULT_THRESHOLDS[class_name]

    if severity > threshold:
        return "REPLACE"
    else:
        return "REPAIR"


def get_severity(image: np.array, coords: np.array, class_name: str) -> float:
    """
    Returns the estimated severity for a given damage detected by the car_damage_detect model.

    Parameters
    ----------
    image: np.array
        the array of the original image
    coords: np.array / torch.Tensor
        the coordinates of the damage detected on the original image by the car_damage_detect model
    class_name: str
        the name of the class detected by the car_damage_detect model

    Returns
    -------
    float:
        The estimated severity
    """

    input_size = (224, 224)

    # Extract plate coordinates
    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])

    # Preprocess plate image (crop / gray / ...)
    nimg = np.array(image, dtype=np.float32)
    img_precise = nimg[y1:y2, x1:x2]
    img = cv2.resize(img_precise, dsize=(input_size), interpolation=cv2.INTER_CUBIC)
    # cv2.imwrite("severity.png", img)

    # -- Predict with ONNX
    return model_severity.run(
        [model_severity_output_name], {model_severity_input_name: [img]}
    )[0][0][0]


def get_price(class_name: str, action: str) -> str:
    """
    This function is a temporary function that is supposed to be replaced with
    a function connecting to the database in order to get real prices

    Parameters
    ----------
    class_name: string
        the name of the detected damage
    action: string
        the name of the recommanded action (REPAIR / REPLACE)

    Returns
    -------
    str:
        The estimated price
    """

    prices = {
        "REPAIR": {
            "front_bumper_damage": 435,
            "hood_damage": 492,
            "front_fender_damage": 330,
            "sidedoor_panel_damage": 368,
            "roof_damage": 418,
            "backdoor_panel_damage": 370,
            "rear_bumper_damage": 399,
            "rear_fender_damage": 323,
            "runnigboard_damage": 342,
            "pillar_damage": 322,
        },
        "REPLACE": {
            "front_bumper_damage": 547,
            "hood_damage": 711,
            "front_fender_damage": 517,
            "sidedoor_panel_damage": 688,
            "roof_damage": 799,
            "backdoor_panel_damage": 754,
            "rear_bumper_damage": 631,
            "rear_fender_damage": 588,
            "runnigboard_damage": 499,
            "pillar_damage": 476,
            "headlight_damage": 195,
            "front_windscreen_damage": 660,
            "sidemirror_damage": 175,
            "sidedoor_window_damage": 337,
            "rear_windscreen_damage": 575,
            "taillight_damage": 138,
        },
    }

    return f"{prices[action][class_name]}$"


class RestrictDamagesPerClass:

    dmg_dict = {
        "hood_damage": {"max": 1},
        "front_bumper_damage": {"max": 1},
        "front_fender_damage": {"max": 2},
        "headlight_damage": {"max": 2},
        "front_windscreen_damage": {"max": 1},
        "sidemirror_damage": {"max": 2},
        "sidedoor_panel_damage": {"max": 4},
        "roof_damage": {"max": 1},
        "runnigboard_damage": {"max": 2},
        "pillar_damage": {"max": 4},
        "sidedoor_window_damage": {"max": 4},
        "rear_fender_damage": {"max": 2},
        "rear_windscreen_damage": {"max": 1},
        "taillight_damage": {"max": 2},
        "rear_bumper_damage": {"max": 1},
        "backdoor_panel_damage": {"max": 1},
    }

    def __init__(self):
        for dmg_class in self.dmg_dict:
            self.dmg_dict[dmg_class]["data"] = []

    def add_damage(self, dmg_class, data, score):
        self.dmg_dict[dmg_class]["data"].append((data, score))

    def get_selected(self):
        out_dict = self.dmg_dict.copy()

        # sort & trim
        for k in out_dict:
            out_dict[k] = sorted(out_dict[k]["data"], key=lambda x: x[1], reverse=True)[
                : out_dict[k]["max"]
            ]

        # flatten the tuples
        flatten = []
        [flatten.extend(x) for x in out_dict.values()]

        # keep only json data
        jsons = [x[0] for x in flatten]

        return jsons


# --- MAIN FUNCTION


def predict_damages(filtered_files: list, preprocessed_files: list) -> list:

    results = model_cdd.predict(preprocessed_files, agnostic_nms=True)
    predictions = RestrictDamagesPerClass()

    for i, r in enumerate(results):

        boxes = r.boxes

        for box in boxes:

            # get box coordinates in (top, left, bottom, right) format
            coords = box.xyxy[0]

            classindex = box.cls
            class_name = model_cdd.names[int(classindex)]

            if DEFAULT_THRESHOLDS[class_name] == 0.0:
                model_name = None
                severity = 1.0
            else:
                model_name = sev_model_name
                severity = get_severity(preprocessed_files[i], coords, class_name)

            action = get_action(severity, class_name)

            pred_dict = {
                "severity_model": model_name,
                "type": class_name,
                "coords": coords.tolist(),
                "severity": str(severity),
                "price": get_price(class_name, action),
                "action": action,
                "file": filtered_files[i].filename,
            }

            predictions.add_damage(class_name, pred_dict, severity)

    return predictions.get_selected()
