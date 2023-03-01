#! /usr/bin/env python3
# coding: utf-8

import os
import io
import pathlib

from flask import Flask, flash, request, redirect, jsonify # , url_for
from PIL import Image
from ultralytics import YOLO
# import cv2

# ########## API ##########

# --- Load Model ---

model = YOLO("car_damage_detect.pt")

# --- API Flask app ---

app = Flask(__name__)
app.secret_key = "super secret key"


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ########## API ENTRY POINTS (BACKEND) ##########

@app.route("/")
def index():
    return "The 'MyCover Inference API' server is up."


@app.route("/predict/", methods=["GET", "POST"])
def upload_file():

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

        if file and (allowed_file(file.filename) or file.filename == 'file'):
            print(os.getcwd())
            # filename = secure_filename(file.filename)
            image_bytes = Image.open(io.BytesIO(file.read()))

            results = model.predict(image_bytes)  # obtain predictions

            predictions_classes = []
            predictions_coords = []

            for r in results:
        
                # annotator = Annotator(frame)
        
                boxes = r.boxes
                for box in boxes:
            
                    coords = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
                    classindex = box.cls

                    predictions_classes.append(
                        model.names[int(classindex)]
                    )
                    predictions_coords.append(
                        coords.tolist()
                    )

            print("PREDS:", predictions_classes)
            print("COORDS:", predictions_coords)
            json_dict = {
                'classes':predictions_classes,
                'coords':predictions_coords,
                'prices':['PRICE-TODO']*len(predictions_classes),
                'actions': ['REPAIR-REPLACE-TODO']*len(predictions_classes)
            }

            args = request.args
            if args.get('isfrontend'):
    
                API_URL = request.url_root
                predictions_merged = '<br>'.join([str(x) for x in zip(json_dict['classes'], json_dict['coords'], json_dict["prices"], json_dict["actions"])])
                # predictions_merged = '<br>'.join([f" {key} : {value}" for key, value in json_dict.items()])
                return print_upload_form(API_URL, predictions_merged)

            else:
                return jsonify(json_dict)

    return f"This API entrypoint needs a POST requests with a 'file' parameter"



# ########## DEMO FRONTEND ##########
# This could be a different Flask script totally independant from the API!

def print_upload_form(API_URL, predictions_merged=None):
    """ Define the HTML form used to send images / videos 
        to the API 'predict' endpoint
    """

    if predictions_merged is not None:
        predictions_merged_display = f"<h1>Predicted classes</h1><p>{predictions_merged}</p>"
    else:
        predictions_merged_display = ''

    return f"""
    <!doctype html>
    <html>
        <head>
            <title>Upload new File</title>
        </head>
        <body>
            {predictions_merged_display}
            <h1>Upload new File</h1>
            <form action={API_URL}predict/?isfrontend=True method=post enctype=multipart/form-data>
                <input type=file name=file>
                <input type=submit value=Predict>
            </form>
        </body>
    </html>
    """

@app.route("/upload/")
def upload():

    API_URL = request.url_root
    print("API_URL:", API_URL)

    return print_upload_form(API_URL)

# ########## START BOTH API & FRONTEND ##########

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT") or 5000)
    app.run(debug=True, host="0.0.0.0", port=current_port)