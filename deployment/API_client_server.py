#! /usr/bin/env python3
# coding: utf-8

import os
from flask import Flask, request, redirect, jsonify, url_for, session, abort
from flask_cors import CORS
from apiflask import APIFlask

# from PIL import Image
import cv2
import numpy as np
from json2html import json2html

from api_internals.config_postgres import init_db, demo_queries
from api_internals.config_apiflask import Image, DamagesFullOut, PlatesFullOut
from api_internals.predict_damages import predict_damages, cdd_model_name
from api_internals.predict_plates import predict_plates, lpd_model_name


# --- API Flask app ---
# app = Flask(__name__)
app = APIFlask(__name__)
app.secret_key = "super secret key"
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 20

CORS(app)
init_db(app)
demo_queries()

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

# --- DEFINE FUNCTIONS


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def filter_images(f):
    # filename = secure_filename(file.filename)
    return allowed_file(f.filename)


def prepare_images(filtered_files):
    preprocessed_data = [preprocess_image(x) for x in filtered_files]
    preprocessed_data = list(map(list, zip(*preprocessed_data)))

    preprocessed_files, original_ratios = preprocessed_data[0], preprocessed_data[1]
    return preprocessed_files, original_ratios


def preprocess_image(f):

    # Open POST file with PIL
    # image_bytes = Image.open(io.BytesIO(file.read()))

    # Open POST file with CV2

    nparr = np.fromstring(f.read(), np.uint8)
    image_bytes = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    newSize = 640
    resized = cv2.resize(
        image_bytes, (newSize, newSize), interpolation=cv2.INTER_LINEAR
    )

    ratioW = image_bytes.shape[0] / newSize
    ratioH = image_bytes.shape[1] / newSize

    return resized, (ratioW, ratioH)


def check_uploaded_files(request: request) -> list:

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

    return filtered_files


# ########## API ENTRY POINTS (BACKEND) ##########


# ----- PREDICT DAMAGES -----


@app.route("/predict_damages", methods=["POST"])
@app.input(Image, location="files")
@app.output(DamagesFullOut)
def route_predict_damages(data):
    """
    Define the API endpoint to get damages predictions from one or more images.
    This entrypoint awaits a POST request along with a 'file' parameter containing image(s).
    """

    # --- CHECK FILES
    filtered_files = check_uploaded_files(request)

    # --- PREPARE FILES
    preprocessed_files, original_ratios = prepare_images(filtered_files)

    # --- PREDICT
    json_damages = predict_damages(filtered_files, preprocessed_files, original_ratios)
    json_dict = {"damage_model": cdd_model_name, "damages": json_damages}

    # --- RETURN ANSWER
    args = request.args
    if args.get("isfrontend") is None:
        print(jsonify(json_dict))
        return jsonify(json_dict)

    else:
        session["json2html"] = json2html.convert(json_dict)
        return redirect(url_for("upload_damages"))


# ----- PREDICT PLATES -----


@app.route("/predict_plates", methods=["POST"])
@app.input(Image, location="files")
@app.output(PlatesFullOut)
def route_predict_plates(data):
    """
    Define the API endpoint to get plate text (if any) from an image.
    This entrypoint awaits a POST request along with a 'file' parameter containing an image.
    """

    # --- CHECK FILES
    filtered_files = check_uploaded_files(request)

    # --- PREPARE FILES
    preprocessed_files, original_ratios = prepare_images(filtered_files)

    # --- PREDICT
    json_plates = predict_plates(filtered_files, preprocessed_files, original_ratios)
    json_dict = {"plate_model": lpd_model_name, "plates": json_plates}

    # --- RETURN ANSWER
    args = request.args
    if args.get("isfrontend") is None:
        return jsonify(json_dict)

    else:
        session["json2html"] = json2html.convert(json_dict)
        return redirect(url_for("upload_plate"))


# ########## DEMO FRONTEND ##########
# This could be a different Flask script totally independant from the API!


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
            <title>Upload new files</title>
        </head>
        <body>
            <a href='{API_URL}' target='_self'><< back</a><br>
            {predictions_merged_display}
            <h1>Upload new File</h1>
            <form action={API_URL}{target}?isfrontend=True method=post enctype=multipart/form-data>
                <input type=file name=file multiple>
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

    return print_upload_form(API_URL, "predict_plates", predictions_merged)


# ########## START BOTH API & FRONTEND ##########

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT") or 5000)
    app.run(debug=True, host="0.0.0.0", port=current_port, threaded=True)
