#! /usr/bin/env python3
# coding: utf-8

import os
import io
import pathlib

from flask import Flask, flash, request, redirect, jsonify, url_for

import numpy as np
from PIL import Image

from ultralytics import YOLO

# import tflite_runtime.interpreter as tflite

# import onnxruntime as rt
# print("ONX:", rt.get_device())


# ########## API ##########


# --- Load TF Model ---

base_W = 512
base_H = 256
base_resolution = f"{base_W}x{base_H}"

# print("Load Semantic-segmentation Model")
# model_name = "FPN-efficientnetb7_with_data_augmentation_2_diceLoss_512x256"

# -- with a keras model
# model = keras.models.load_model(
#     f"models/{model_name}.keras",
#     custom_objects={
#         "iou_score": sm.metrics.iou_score,
#         "f1-score": sm.metrics.f1_score,
#         "dice_loss": sm.losses.DiceLoss(),
#     },
# )

# -- with a TF-Lite model
# interpreter = tflite.Interpreter(model_path=f"models/{model_name}.tflite")
# interpreter.resize_tensor_input(0, [1, base_H, base_W, 3])
# interpreter.allocate_tensors()
# input_index = interpreter.get_input_details()[0]["index"]
# output_index = interpreter.get_output_details()[0]["index"]

# --- with a ONNX model

# providers = ['CPUExecutionProvider']
# providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
# m = rt.InferenceSession(str(pathlib.Path('models', f"{model_name}.onnx")), providers=providers)

model = YOLO("car_damage_detect.pt")  # load a pretrained model (recommended for training)

# --- API Flask app ---

app = Flask(__name__)
# app.secret_key = "super secret key"


UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocessing(im):
    try:
        # im = Image.open(infile)
        im = im.resize((base_W, base_H), resample=0) 
        im.save('test', "JPEG")
        return im
    except IOError:
        print(f"cannot preprocess")

@app.route("/")
def index():
    return "The 'MyCover Inference API' server is up."


@app.route("/predict/", methods=["GET", "POST"])
def upload_file():

    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
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

            image_bytes = preprocessing(image_bytes)

            # Preprocess image
            # img = preprocess_sample(image_bytes, preprocess_input)
            # /!\ Preprocessed layers are now included in the model
            img = np.array([np.array(image_bytes)], dtype=np.float32)

            if (img.shape[1] != base_H or img.shape[2] != base_W):
                print(img.shape[1], img.shape[2])
                raise Exception(f"Custom Error: wrong image size ({base_H}x{base_W}) ({img.shape[1]}, {img.shape[2]}) required!")

            # Apply model
            print("--- Predict")
            # pred = model.predict(img)  # keras model

            img = np.array(img, dtype=np.float32)
            print(img.shape)

            # -- Predict with TF-Lite
            # interpreter.set_tensor(input_index, img)
            # interpreter.invoke()
            # pred = interpreter.get_tensor(output_index)

            # -- Predict with ONNX
            #### pred = m.run(['model_6'], {'input': img})[0]

            # Convert to categories
            #### mask = np.argmax(pred, axis=3)[0]

            # Return the matrix
            #### return jsonify(mask.tolist())

            im = pathlib.Path('data', "val", 'emmanuel_letremble_1996_mercedes-benz_e_320_exterior_5211_postloss.jpg')
            img = Image.open(im)


            # results = model.predict(img)  # obtain predictions
            results = model(img)  # obtain predictions

            predictions = []
            for result in results:
                for i in result.boxes.cls:
                    predictions.append(
                        model.names[int(i)]
                    )  # append the detected classes to empty list

            print("PREDS:", predictions)

            # cv2.imshow("result", results[0].plot())

    return """
    <!doctype html>
    <html>
        <head>
            <title>Upload new File</title>
        </head>
        <body>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
                <input type=file name=file>
                <input type=submit value=Upload>
            </form>
        </body>
    </html>
    """


# ########## DEMO FRONTEND ##########
# This could be a different Flask script totally independant from the API!

def get_ids(path):
    ids = []
    for x in path.glob("*.jpg"):
        path = str(x)
        file = path[path.rfind('/')+1:]
        ids.append(file)
    return ids

@app.route("/list/")
def file_list():
    files_path = pathlib.Path('data', "val")
    ids = get_ids(files_path)

    API_URL = request.url_root
    print("API_URL:", API_URL)

    return f"""
    <!doctype html>
    <html>
        <head>
            <title>List of available ids</title>
        </head>
        <body>
            <h1>Upload new File</h1>
            <form action={API_URL}/predict/ method=post enctype=multipart/form-data>
                <input type=file name=file>
                <input type=submit value=Upload>
            </form>
        </body>
    </html>
    """

# ########## START BOTH API & FRONTEND ##########

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT") or 5000)
    app.run(debug=True, host="0.0.0.0", port=current_port)