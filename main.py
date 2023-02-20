import hashlib
import json
import logging
import threading
from pathlib import Path
from queue import Queue

import cv2 as cv
from flask import (Response, jsonify, redirect, render_template, request,
                   send_file, session, url_for)
from werkzeug.utils import secure_filename

import config

logger = logging.getLogger(__name__)


title = config.title
app = config.app
key = app.secret_key
host = config.host
port = config.port
debug = config.debug
face_detect = config.face_detect
smile_recognition = config.smile_recognition
UPLOADS_FOLDER = config.UPLOADS_FOLDER

count = 0
LOCK = threading.Lock()
queue_dict = dict()


@app.route("/", methods=["GET"])
def index():
    global count, queue_dict
    if "id" not in session:
        session.permanent = True
        with LOCK:
            user = str(count)
            session["id"] = hashlib.sha256((key + user).encode('utf-8')).hexdigest()
            queue_dict[str(session["id"])] = Queue()
            count += 1
    if "filename" in session:
        filename = session["filename"]
        return render_template("index.html", title=title, filename=filename)
    else:
        return render_template("index.html", title=title)


@app.route("/stream")
def stream():
    global queue_dict
    queue = queue_dict[str(session["id"])]
    return Response(event_stream(queue), mimetype="text/event-stream")


def event_stream(queue):
    while True:
        persent = queue.get(True)
        print("progress:{}%".format(persent))
        sse_event = "progress-item"
        if persent == 100:
            sse_event = "last-item"
        yield "event:{event}\ndata:{data}\n\n".format(event=sse_event, data=persent)


@app.route("/ajax", methods=["POST"])
def ajax():
    global queue_dict
    queue = queue_dict[str(session["id"])]
    if request.method == "POST":
        id = session["id"]
        filename = session["filename"]
        video_frame_count = 0
        capture = cv.VideoCapture("static/uploads/" + filename)
        totalframecount = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
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
            queue.put(100 * video_frame_count // totalframecount)
        result = {"id": id, "smileScore": str(smile_score)}
        return jsonify(json.dumps(result))


@app.route("/upload", methods=["POST"])
def upload_video():
    id = session["id"]
    video = request.files["video_file"]
    filename = str(id) + "." + secure_filename(video.filename).split(".")[-1]
    video.save(str(UPLOADS_FOLDER / filename))
    session["filename"] = filename
    return redirect(url_for("index"))


@app.route("/download", methods=["POST"])
def download():
    id = session["id"]
    downloadFileName = "smile.jpg"
    downloadFile = "static/outputs/" + id + ".jpg"
    return send_file(
        downloadFile,
        as_attachment=True,
        download_name=downloadFileName,
        mimetype="image/jpeg",
    )


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/reset", methods=["GET"])
def reset():
    try:
        del session["filename"]
    except KeyError as ex:
        logger.warning({"action": "reset", "ex": ex})
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
