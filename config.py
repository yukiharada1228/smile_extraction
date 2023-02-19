import logging
import secrets
import sys
from datetime import timedelta
from pathlib import Path

from flask import Flask

title = "笑顔きりとりくん"
debug = True
host = "0.0.0.0"
port = 5000
if debug:
    level = logging.DEBUG
else:
    level = logging.INFO
logging.basicConfig(level=level, stream=sys.stdout)
logger = logging.getLogger(__name__)

from models.smile_detection.face_detection.face_detection import \
    config as face_config
from models.smile_detection.smile_detection import config as smile_config

face_detect = face_config.face_detect
smile_recognition = smile_config.smile_recognition

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_FOLDER = PROJECT_ROOT / "static"
UPLOADS_FOLDER = STATIC_FOLDER / "uploads"
OUTPUTS_FOLDER = STATIC_FOLDER / "outputs"

folders = [UPLOADS_FOLDER, OUTPUTS_FOLDER]


def make_folders(folders):
    for folder in folders:
        try:
            folder.mkdir()
            logger.debug({"action": "make_folders", "folder": folder})
        except FileExistsError as ex:
            logger.warning({"action": "make_folders", "folder": folder, "ex": ex})


make_folders(folders=folders)

app = Flask(__name__)
app.secret_key = secrets.token_hex(8)
app.config["UPLOADS_FOLDER"] = UPLOADS_FOLDER
app.permanent_session_lifetime = timedelta(minutes=10)
