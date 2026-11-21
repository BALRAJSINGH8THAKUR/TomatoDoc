import threading

from flask import Flask, jsonify, render_template, request
from PIL import Image, ImageOps, UnidentifiedImageError

from knowledge import DISEASES

Image.MAX_IMAGE_PIXELS = 40_000_000
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB
app.predictor = None
_lock = threading.Lock()

MESSAGES = {
    "not_a_leaf": "This doesn't look like a leaf. Please upload a close-up photo of a tomato leaf.",
    "not_tomato": "This doesn't look like a tomato leaf. This tool only works on tomato plants, so other plants "
                  "(apple, potato, pepper, etc.) can't be diagnosed.",
    "low_confidence": "I'm not confident this is a tomato leaf I can diagnose. Try a sharper, well-lit, "
                      "close-up photo of a single leaf against a plain background.",
}


def get_predictor():
    with _lock:
        if app.predictor is None:
            from predictor import Predictor
            app.predictor = Predictor()
    return app.predictor


def open_image(stream):
    img = Image.open(stream)
    img.load()
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict():
    f = request.files.get("image")
    if not f or not f.filename:
        return jsonify(status="error", message="No image was uploaded."), 400
    try:
        img = open_image(f.stream)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return jsonify(status="error", message="That file isn't a valid image (try JPG or PNG)."), 400
    if min(img.size) < 64:
        return jsonify(status="error", message="The image is too small. Please upload a larger photo."), 400

    try:
        result = get_predictor().predict(img)
    except Exception:  # model missing / TF failure
        app.logger.exception("Prediction failed")
        return jsonify(status="error", message="The server couldn't run the model. Please try again later."), 500

    if result["status"] == "rejected":
        result["message"] = MESSAGES[result["reason"]]
        return jsonify(result)

    info = DISEASES[result["label"]]
    result["name"] = info["name"]
    result["healthy"] = info["healthy"]
    result["info"] = {k: info[k] for k in ("summary", "organic", "chemical", "prevention")}
    for t in result["top3"]:
        t["name"] = DISEASES[t["label"]]["name"]
    return jsonify(result)


@app.errorhandler(413)
def too_large(_):
    return jsonify(status="error", message="Image is too large (max 8 MB)."), 413


if __name__ == "__main__":
    app.run(debug=False, port=5000)
