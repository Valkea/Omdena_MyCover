from pathlib import Path

from api_internals.config_postgres import get_db_price

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
        The recommended action based on the severity level and class name.
        Possible values are "REPLACE" or "REPAIR".
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
        the coordinates of the damage detected on the original image by the car_damage_detect model,
        the coordinates should be in the format (x1, y1, x2, y2).
    class_name: str
        the name of the class detected by the car_damage_detect model

    Returns
    -------
    float:
        A number indicating the severity level of the issue.
        The value should be between 0 and 1.
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


def get_price(part: str, action: str, customer_car_info: dict) -> int:
    """
    This function is a temporary function that is supposed to be replaced with
    a function connecting to the database in order to get real prices

    Parameters
    ----------
    part: string
        the name of the detected damage
    action: string
        the name of the recommanded action (REPAIR / REPLACE)
    customer_car_info: dict
        a dictionnary containng the 'trade', 'model', 'year' send along with the POST request

    Returns
    -------
    int:
        The estimated price
    """

    trade = customer_car_info['trade']
    model = customer_car_info['model']
    year = customer_car_info['year']

    db_price = get_db_price(trade, model, year, part, action)
    return db_price


class RestrictDamagesPerClass:
    """
    A class that restricts the number of damages per class, selecting 
    the highest scored damages to be added to the final result.

    Attributes
    ----------
    dmg_dict : dict
        A dictionary containing the name of each damage class and the maximum number of damages
        that can be selected from that class.

    Methods
    -------
    add_damage(dmg_class, data, score)
        Adds the data and score of a new damage to the list of the corresponding damage class.
    get_selected()
        Returns a list with the data of the top scored damages for each class,
        up to the maximum number of damages allowed for each class.
    """

    dmg_dict = {
        "hood_damage": {"max": 1},
        "front_bumper_damage": {"max": 1},
        "front_fender_damage": {"max": 1},
        "headlight_damage": {"max": 1},
        "front_windscreen_damage": {"max": 1},
        "sidemirror_damage": {"max": 1},
        "sidedoor_panel_damage": {"max": 1},
        "roof_damage": {"max": 1},
        "runnigboard_damage": {"max": 1},
        "pillar_damage": {"max": 1},
        "sidedoor_window_damage": {"max": 1},
        "rear_fender_damage": {"max": 1},
        "rear_windscreen_damage": {"max": 1},
        "taillight_damage": {"max": 1},
        "rear_bumper_damage": {"max": 1},
        "backdoor_panel_damage": {"max": 1},
    }

    def __init__(self):
        for dmg_class in self.dmg_dict:
            self.dmg_dict[dmg_class]["data"] = []

    def add_damage(self, dmg_class, data, score):
        """
        Adds a new damage data to the specified damage class list.

        Parameters
        ----------
        dmg_class : str
            The damage class to add the data to.
        data : dict
            The predicted damage data.
        score : float
            The score associated with the damage data. This score is used
            to return the top entry according to the dmg_dict limitation.
        """

        self.dmg_dict[dmg_class]["data"].append((data, score))

    def get_selected(self):
        """
        Returns selected damage data.

        Returns
        -------
        list:
            A list of the TOP damages (with their data) for each car parts,
            according to the dmg_dict limitations.
        """

        out_dict = self.dmg_dict.copy()

        # --- SORT & TRIM
        for k in out_dict:
            out_dict[k] = sorted(out_dict[k]["data"], key=lambda x: x[1], reverse=True)

            # --- REMOVE EXTA DAMAGES
            # out_dict[k] = out_dict[k][: self.dmg_dict[k]["max"]] # cut to MAX

            # --- ADD DUPLICATED TAGS
            if len(out_dict[k]) > 0:
                for j in range(self.dmg_dict[k]["max"], len(out_dict[k])):
                    out_dict[k][j][0]["probable_duplicate"] = True

        # --- FLATTEN THE TUPLES
        flatten = []
        [flatten.extend(x) for x in out_dict.values()]

        # --- KEEP ONLY JSON DATA
        jsons = [x[0] for x in flatten]

        return jsons


# --- MAIN FUNCTION


def predict_damages(
        filtered_files: list, preprocessed_files: list, original_ratios: list, customer_car_info: dict
) -> list:
    """
    Predicts damages and their severity levels for given preprocessed files.

    Parameters
    ----------
    filtered_files: list
        A list of the filtered files so that we can return the name of the original files.
    preprocessed_files: list
        A list of preprocessed files so that we can predict damages and severity.
    original_ratios: list
        A list of original ratios of the filtered files so that we can return damages
        coordinates that match the original file shape.
    customer_car_info: dict
        A dictionary containing information about the customer's car (trade, model, year)
        so that we can fetch a more precise estimated price.

    Returns
    -------
    list
        A list of predicted damages, where each item is a dictionary containing the following information:
            - severity_model: (str) The name of the severity model used for prediction.
            - type: (str) The type of damage.
            - coords: (list) The coordinates of the damage in (top, left, bottom, right) format.
            - severity: (str) The severity level of the damage.
            - price: (float) The estimated price to repair the damage.
            - action: (str) The recommended action to take for the damage.
            - file: (str) The name of the file the damage was predicted from.
            - probable_duplicate: (bool) True if the predicted damage for a given class
            already reached the limit in the BATCH of images (they are ordered by severity score)
    """

    results = model_cdd.predict(preprocessed_files, agnostic_nms=True)
    predictions = RestrictDamagesPerClass()

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
                "coords": coords_ratio,
                "severity": str(severity),
                "price": get_price(class_name, action, customer_car_info),
                "action": action,
                "file": filtered_files[i].filename,
                "probable_duplicate": False,
            }

            predictions.add_damage(class_name, pred_dict, severity)

    return predictions.get_selected()
