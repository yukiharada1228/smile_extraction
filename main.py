import logging
import os
import sys

import cv2 as cv
from flask import flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app import app

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
import models.smile_detection.face_detection.face_detection.config as face_detection
import models.smile_detection.smile_detection.config as smile_detection

filename = ""
face_detect = face_detection.face_detect
smile_recognition = smile_detection.smile_recognition


@app.route("/")
def upload_form():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_video():
    global filename
    if "file" not in request.files:
        flash("動画がありませんでした．")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("アップロードする動画が選択されていませんでした．")
        return redirect(request.url)
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        flash(f"{filename}がアップロードされました．")
        return render_template("upload.html", filename=filename)


@app.route("/execute", methods=["POST"])
def execute():
    global filename
    video_frame_count = 0
    capture = cv.VideoCapture("static/uploads/" + filename)
    probs_max = 0.0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        video_frame_count += 1
        faces = face_detect.detect(frame)
        probs = smile_recognition.recognize(frame, faces)
        if len(probs):
            if max(probs) > probs_max:
                probs_max = max(probs)
                logger.info({"action": "execute", "probs_max": probs_max})
                cv.imwrite("static/imgs/output.jpg", frame)
    return render_template("index.html", probs_max=probs_max)


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


if __name__ == "__main__":
    app.run()
