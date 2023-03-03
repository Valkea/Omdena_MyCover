#! /usr/bin/env python3
# coding: utf-8

import os
import io
from pathlib import Path

from flask import Flask, flash, request, redirect, jsonify, url_for
from ultralytics import YOLO
import easyocr

# from PIL import Image
import cv2
import numpy as np

# ########## API ##########

# --- Load Models ---

cdd_model_name = "car_damage_detect_2.pt"
lpd_model_name = "license_plate_detect_model.pt"

model_cdd = YOLO(Path("models", cdd_model_name))
model_lpd = YOLO(Path("models", lpd_model_name))

# --- API Flask app ---

app = Flask(__name__)
app.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ########## API ENTRY POINTS (BACKEND) ##########


@app.route("/")
def index():
    return """
    <h1>The 'MyCover Inference API' server is up.</h1>
    <h2>You can use the frontend</h2>
    <p><a href='upload_damages' target='_self'>Send image to detect damages</a></p>
    <p><a href='upload_plate' target='_self'>Send image to detect plate</a></p>
    <h2>Or you can query the entry points to get JSON answers</h2>
    """


# ##### PREDICT DAMAGES #####


@app.route("/predict_damages/", methods=["GET", "POST"])
def predict_damages():

    if request.method == "POST":

        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            print("No file part")
            return redirect(request.url)
        file = request.files["file"]

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and (allowed_file(file.filename) or file.filename == "file"):
            print(os.getcwd())
            # filename = secure_filename(file.filename)

            # Open POST file with PIL
            # image_bytes = Image.open(io.BytesIO(file.read()))

            # Open POST file with CV2
            nparr = np.fromstring(file.read(), np.uint8)
            image_bytes = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Predict
            results = model_cdd.predict(image_bytes)  # obtain predictions

            predictions_classes = []
            predictions_coords = []

            for r in results:

                boxes = r.boxes
                for box in boxes:

                    coords = box.xyxy[
                        0
                    ]  # get box coordinates in (top, left, bottom, right) format
                    classindex = box.cls

                    predictions_classes.append(model_cdd.names[int(classindex)])
                    predictions_coords.append(coords.tolist())

            json_dict = {
                "model": cdd_model_name,
                "classes": predictions_classes,
                "coords": predictions_coords,
                "prices": ["PRICE-TODO"] * len(predictions_classes),
                "actions": ["REPAIR-REPLACE-TODO"] * len(predictions_classes),
            }

            args = request.args
            if args.get("isfrontend"):

                predictions_merged = "<br>".join(
                    [
                        str(x)
                        for x in zip(
                            json_dict["classes"],
                            json_dict["coords"],
                            json_dict["prices"],
                            json_dict["actions"],
                        )
                    ]
                )
                return redirect(
                    url_for("upload_damages", predictions_merged=f"model:{cdd_model_name}<br>" + predictions_merged)
                )

            else:
                return jsonify(json_dict)

    return "This API entrypoint needs a POST requests with a 'file' parameter"


# ##### PREDICT PLATE NUMBER #####

reader = None


def get_text(image, coords):
    """ Obtains the license plate number from the license plate """

    # Initialize easyocr reader if needed
    global reader
    if reader is None:
        reader = easyocr.Reader(["en"])

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


@app.route("/predict_plate/", methods=["GET", "POST"])
def predict_plate():

    if request.method == "POST":

        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            print("No file part")
            return redirect(request.url)
        file = request.files["file"]

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and (allowed_file(file.filename) or file.filename == "file"):
            print(os.getcwd())
            # filename = secure_filename(file.filename)

            # Open POST file with PIL
            # image_bytes = Image.open(io.BytesIO(file.read()))

            # Open POST file with CV2
            nparr = np.fromstring(file.read(), np.uint8)
            image_bytes = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Predict
            results = model_lpd.predict(image_bytes)  # obtain predictions

            predictions_coords = []
            predictions_texts = []

            for r in results:

                boxes = r.boxes
                for box in boxes:

                    coords = box.xyxy[
                        0
                    ]  # get box coordinates in (top, left, bottom, right) format
                    text = get_text(image_bytes, coords)

                    predictions_coords.append(coords.tolist())
                    predictions_texts.append(text)

            json_dict = {
                "model": lpd_model_name,
                "texts": predictions_texts,
                "coords": predictions_coords,
            }

            args = request.args
            if args.get("isfrontend"):
                predictions_merged = "<br>".join(
                    [str(x) for x in zip(json_dict["coords"], json_dict["texts"])]
                )
                return redirect(
                    url_for("upload_plate", predictions_merged=f"model:{lpd_model_name}<br>" + predictions_merged)
                )

            else:
                return jsonify(json_dict)

    return "This API entrypoint needs a POST requests with a 'file' parameter"


# ########## DEMO FRONTEND ##########
# This could be a different Flask script totally independant from the API!


def print_upload_form(API_URL, target, predictions_merged=None):
    """Define the HTML form used to send images / videos
    to the API 'predict' endpoint
    """

    if predictions_merged is not None:
        predictions_merged_display = (
            f"<h1>Predicted classes</h1><p>{predictions_merged}</p>"
        )
    else:
        predictions_merged_display = ""

    return f"""
    <!doctype html>
    <html>
        <head>
            <title>Upload new File</title>
        </head>
        <body>
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
def upload_damages():

    API_URL = request.url_root
    print("API_URL:", API_URL)

    args = request.args

    return print_upload_form(API_URL, "predict_damages", args.get("predictions_merged"))


@app.route("/upload_plate/")
def upload_plate():

    API_URL = request.url_root
    print("API_URL:", API_URL)

    args = request.args

    return print_upload_form(API_URL, "predict_plate", args.get("predictions_merged"))


# ########## START BOTH API & FRONTEND ##########

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT") or 5000)
    app.run(debug=True, host="0.0.0.0", port=current_port)
