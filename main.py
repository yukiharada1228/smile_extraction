import logging
from pathlib import Path

import cv2 as cv
from flask import redirect, render_template, request, session, url_for
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

count = 0


@app.route("/", methods=["GET"])
def index():
    global count
    if "id" not in session:
        session.permanent = True
        user = count
        session["id"] = user
        count += 1
    if "filename" in session:
        filename = session["filename"]
        return render_template("index.html", title=title, filename=filename)
    else:
        return render_template("index.html", title=title)


@app.route("/upload", methods=["POST"])
def upload_video():
    id = session["id"]
    video = request.files["video_file"]
    filename = str(id) + "." + secure_filename(video.filename).split(".")[-1]
    video.save(str(UPLOADS_FOLDER / filename))
    session["filename"] = filename
    return redirect(url_for("index"))


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/execute", methods=["POST"])
def execute():
    id = session["id"]
    filename = session["filename"]
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
                cv.imwrite(f"static/outputs/{id}.jpg", frame)
    (Path("static") / "uploads" / filename).unlink()
    del session["filename"]
    return render_template(
        "result.html", title=title, filename=filename, smile_score=smile_score
    )


if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
