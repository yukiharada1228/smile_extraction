import logging
import os
import sys
from datetime import timedelta
from pathlib import Path

import cv2 as cv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
from models.smile_detection.face_detection.face_detection import \
    config as face_config
from models.smile_detection.smile_detection import config as smile_config

face_detect = face_config.face_detect
smile_recognition = smile_config.smile_recognition

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_FOLDER = PROJECT_ROOT / "static"
UPLOAD_FOLDER = STATIC_FOLDER / "uploads"
IMAGE_FOLDER = STATIC_FOLDER / "imgs"

if not STATIC_FOLDER.exists():
    for folder in [STATIC_FOLDER, UPLOAD_FOLDER, IMAGE_FOLDER]:
        folder.mkdir()

app = Flask(__name__)
app.secret_key = "secret key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.permanent_session_lifetime = timedelta(minutes=15)

count = 0


@app.route("/", methods=["GET"])
def login():
    if "filename" in session:
        return render_template(
            "upload.html", id=session["id"], filename=session["filename"]
        )
    elif "id" in session:
        return render_template("upload.html", id=session["id"])
    else:
        global count
        session.permanent = True
        user = count
        session["id"] = user
        count += 1
        return render_template("upload.html", id=session["id"])


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("id", None)
    session.clear()
    return redirect("/")


@app.route("/upload", methods=["POST"])
def upload_video():
    file = request.files["file"]
    session["filename"] = (
        str(session["id"]) + "." + secure_filename(file.filename).split(".")[-1]
    )
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], session["filename"]))
    return redirect("/")


@app.route("/execute", methods=["POST"])
def execute():
    video_frame_count = 0
    capture = cv.VideoCapture("static/uploads/" + session["filename"])
    smile_score = 0.0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        video_frame_count += 1
        faces = face_detect.detect(frame)
        probs = smile_recognition.recognize(frame, faces)
        if len(probs):
            if max(probs) > smile_score:
                smile_score = max(probs)
                logger.info({"action": "execute", "smile_score": smile_score})
                cv.imwrite(f"static/imgs/{session['id']}.jpg", frame)
    (Path("static") / "uploads" / session["filename"]).unlink()
    del session["filename"]
    return render_template("result.html", id=session["id"], smile_score=smile_score)


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
