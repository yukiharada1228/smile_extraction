import logging
from pathlib import Path

import cv2 as cv
from flask import redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import config

logger = logging.getLogger(__name__)


title = config.title
app = config.app
host = config.host
port = config.port
debug = config.debug
face_detect = config.face_detect
smile_recognition = config.smile_recognition
UPLOADS_FOLDER = config.UPLOADS_FOLDER

filename = None


@app.route("/", methods=["GET"])
def index():
    global filename
    if filename == None:
        return render_template("index.html", title=title)
    else:
        return render_template("index.html", title=title, filename=filename)


@app.route("/upload", methods=["POST"])
def upload_video():
    global filename
    video = request.files["video_file"]
    filename = secure_filename(video.filename)
    video.save(str(UPLOADS_FOLDER / filename))
    return redirect(url_for("index"))


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/execute", methods=["POST"])
def execute():
    global filename
    video_frame_count = 0
    capture = cv.VideoCapture("static/uploads/" + filename)
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
                cv.imwrite(f"static/outputs/{filename}.jpg", frame)
    (Path("static") / "uploads" / filename).unlink()
    return render_template(
        "result.html", title=title, filename=filename, smile_score=smile_score
    )


if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
