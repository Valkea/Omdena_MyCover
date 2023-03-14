#! /usr/bin/env python3
# coding: utf-8

import os
from pathlib import Path

from flask import Flask, flash, request, redirect, jsonify, url_for, session, abort
from apiflask import APIFlask, Schema
from apiflask.fields import Integer, String, File, List, Nested
from apiflask.validators import Length
from flask_cors import CORS

from ultralytics import YOLO
import easyocr

# from PIL import Image
import cv2
import numpy as np
from json2html import json2html

import onnxruntime as rt

# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE, SIG_DFL)

print("ONX:", rt.get_device())

# --- Define input and outputs for APIFlask documentation ---


class Image(Schema):
    file = File()


damage_sample = [
    {
        "action": "REPLACE",
        "type": "headlight_damage",
        "coords": [420.0, 206.0, 552.0, 294.0],
        "severity": "0.5441662",
        "severity_model": "severity_model_001.onnx",
        "price": "111$",
        "file": "my_photo.jpg",
    },
]

plate_sample = [
    {
        "coords": [294.0, 215.0, 440.0, 262.0],
        "text": "NOT READABLE",
        "file": "my_photo.jpg",
    }
]


class DamagesOut(Schema):
    type = String()
    coords = List(Integer(), many=True, validate=Length(4, 4))
    severity = String()
    severity_model = String()
    action = String()
    price = String()
    file = String()


class DamagesFullOut(Schema):
    damage_model = String(load_default="car_damage_detect.pt")
    damages = List(Nested(DamagesOut), load_default=damage_sample)


class PlatesOut(Schema):
    coords = List(Integer(), many=True, validate=Length(4, 4))
    text = String()
    file = String()


class PlatesFullOut(Schema):
    plate_model = String(load_default="car_damage_detect.pt")
    plates = List(Nested(PlatesOut), load_default=plate_sample)


# --- Load Models ---

cdd_model_name = "car_damage_detect_2.pt"
lpd_model_name = "license_plate_detect_model.pt"
sev_model_name = "severity_model.onnx"

model_cdd = YOLO(Path("models", cdd_model_name))
model_lpd = YOLO(Path("models", lpd_model_name))

providers = [
    "TensorrtExecutionProvider",
    "CUDAExecutionProvider",
    "CPUExecutionProvider",
]
model_severity = rt.InferenceSession(
    str(Path("models", sev_model_name)), providers=providers
)
model_severity_input_name = "sequential_2_input"
model_severity_output_name = "output_layer"

# --- API Flask app ---
# app = Flask(__name__)
app = APIFlask(__name__)
app.secret_key = "super secret key"
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 20

CORS(app)

ALLOWED_EXTENSIONS = {
    "bmp",
    "dng",
    "jpeg",
    "jpg",
    "mpo",
    "png",
    "tif",
    "tiff",
    "webp",
    "pfm",  # images
    # "asf",
    # "avi",
    # "gif",
    # "m4v",
    # "mkv",
    # "mov",
    # "mp4",
    # "mpeg",
    # "mpg",
    # "ts",
    # "wmv",
    # "webm",  # videos
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def filter_images(f):
    # filename = secure_filename(file.filename)
    return allowed_file(f.filename)


# ########## API ENTRY POINTS (BACKEND) ##########


@app.route("/")
# @app.doc(hide=True)
def index():
    """ Define the content of the main fontend page of the API server """

    return """
    <h1>The 'MyCover Inference API' server is up.</h1>
    <h2>You can use the frontend</h2>
    <p><a href='upload_damages' target='_self'>Send image to detect damages</a></p>
    <p><a href='upload_plate' target='_self'>Send image to detect plate</a></p>
    <h2>Or you can query the entry points to get JSON answers</h2>
    """


# ----- PREDICT DAMAGES -----

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


def preprocess_image(f):

    # Open POST file with PIL
    # image_bytes = Image.open(io.BytesIO(file.read()))

    # Open POST file with CV2
    nparr = np.fromstring(f.read(), np.uint8)
    image_bytes = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image_bytes


# Handling error 404 and displaying relevant web page
@app.errorhandler(400)
def not_found_error(error):
    return {"error": str(error)}, 400


@app.route("/predict_damages", methods=["POST"])
@app.input(Image, location="files")
@app.output(DamagesFullOut)
def predict_damages(data):
    """
    Define the API endpoint to get damages predictions from one or more images.
    This entrypoint awaits a POST request along with a 'file' parameter containing image(s).
    """

    # --- CHECK IF THE POST REQUEST HAS THE FILE PART

    if "file" not in request.files:
        print("No file part")
        abort(400, description="The 'file' form-data field is missing in the request.")

    # --- CHECK IF THE FILEPART CONTAINS DATA

    files = request.files.getlist("file")
    if len(files) == 1 and files[0].filename == "":
        print("No data into the filepart")
        abort(400, description="There is no data in the 'file' form-data field.")
    else:
        print(f"There are {len(files)} files in the filepart")

    # --- CHECK IF THERE IS AT LEAST ONE FILE WITH A COMPATIBLE FORMAT

    filtered_files = list(filter(filter_images, files))
    if len(filtered_files) == 0:
        abort(400, description="The provided file(s) format is not supported.")

    preprocessed_files = [preprocess_image(x) for x in filtered_files]

    # --- PREDICT

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

    # --- RETURN ANSWER

    json_dict = {"damage_model": cdd_model_name, "damages": predictions.get_selected()}

    args = request.args
    if args.get("isfrontend") is None:
        print(jsonify(json_dict))
        return jsonify(json_dict)

    else:
        session["json2html"] = json2html.convert(json_dict)
        return redirect(url_for("upload_damages"))


# ----- PREDICT PLATE NUMBER -----

reader = easyocr.Reader(["en"])


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


@app.route("/predict_plate", methods=["POST"])
@app.input(Image, location="files")
@app.output(PlatesFullOut)
def predict_plate(data):
    """
    Define the API endpoint to get plate text (if any) from an image.
    This entrypoint awaits a POST request along with a 'file' parameter containing an image.
    """

    # --- CHECK IF THE POST REQUEST HAS THE FILE PART

    if "file" not in request.files:
        print("No file part")
        abort(400, description="The 'file' form-data field is missing in the request.")

    # --- CHECK IF THE FILEPART CONTAINS DATA

    files = request.files.getlist("file")
    if len(files) == 1 and files[0].filename == "":
        print("No data into the filepart")
        abort(400, description="There is no data in the 'file' form-data field.")
    else:
        print(f"There are {len(files)} files in the filepart")

    # --- CHECK IF THERE IS AT LEAST ONE FILE WITH A COMPATIBLE FORMAT

    filtered_files = list(filter(filter_images, files))
    if len(filtered_files) == 0:
        abort(400, description="The provided file(s) format is not supported.")

    preprocessed_files = [preprocess_image(x) for x in filtered_files]

    # --- PREDICT

    results = model_cdd.predict(preprocessed_files, agnostic_nms=True)
    predictions = []

    for i, r in enumerate(results):

        boxes = r.boxes
        for box in boxes:

            coords = box.xyxy[
                0
            ]  # get box coordinates in (top, left, bottom, right) format
            text = get_text(preprocessed_files[i], coords)

            pred_dict = {
                "text": text,
                "coords": coords.tolist(),
                "file": filtered_files[i].filename,
            }
            predictions.append(pred_dict)

    json_dict = {"plate_model": lpd_model_name, "plates": predictions}

    args = request.args
    if args.get("isfrontend") is None:
        return jsonify(json_dict)

    else:
        session["json2html"] = json2html.convert(json_dict)
        return redirect(url_for("upload_plate"))


# ########## DEMO FRONTEND ##########
# This could be a different Flask script totally independant from the API!


def print_upload_form(API_URL: str, target: str, predictions_merged: str = None) -> str:
    """
    This function defines the content of the frontend pages with upload option.

    Parameters
    ----------
    API_URL: str
        the base url of the API
    target: str
        the endpoint name & parameters
    predictions_merged: str
        the predictions returned by the models

    Returns
    -------
    str:
        The HTML  content of the frontend page
    """

    if predictions_merged is not None:
        predictions_merged_display = f"<h1>Returned content</h1><p>(The JSON is converted to HTML)</p><p>{predictions_merged}</p>"
    else:
        predictions_merged_display = ""

    return f"""
    <!doctype html>
    <html>
        <head>
            <title>Upload new File</title>
        </head>
        <body>
            <a href='{API_URL}' target='_self'><< back</a><br>
            {predictions_merged_display}
            <h1>Upload new File</h1>
            <form action={API_URL}{target}/?isfrontend=True method=post enctype=multipart/form-data>
                <input type=file name=file>
                <input type=submit value=Predict>
            </form>
        </body>
    </html>
    """


@app.route("/upload_damages/")
# @app.doc(hide=True)
def upload_damages():
    """ A simple frontend page to upload image & try the predic_damages API endpoint. """

    API_URL = request.url_root
    predictions_merged = None
    if "json2html" in session:
        predictions_merged = session["json2html"]
    session["json2html"] = None

    return print_upload_form(API_URL, "predict_damages", predictions_merged)


@app.route("/upload_plate/")
# @app.doc(hide=True)
def upload_plate():
    """ A simple frontend page to upload image & try the predic_plate API endpoint. """

    API_URL = request.url_root
    predictions_merged = None
    if "json2html" in session:
        predictions_merged = session["json2html"]
    session["json2html"] = None

    return print_upload_form(API_URL, "predict_plate", predictions_merged)


# ########## START BOTH API & FRONTEND ##########

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT") or 5000)
    app.run(debug=True, host="0.0.0.0", port=current_port, threaded=True)
