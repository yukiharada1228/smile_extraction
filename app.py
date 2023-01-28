from pathlib import Path

from flask import Flask

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
