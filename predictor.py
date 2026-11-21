"""Model loading, preprocessing and 'is this really a tomato leaf?' checks."""
import json
import os
import threading

import numpy as np
from PIL import Image

from knowledge import CLASS_NAMES

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE, "tomato_disease_model.h5"))
STATS_PATH = os.path.join(BASE, "ood_stats.npz")
NAMES_PATH = os.path.join(BASE, "class_names.json")
IMG_SIZE = 128
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.70"))   # softmax gate
MIN_LEAF_RATIO = float(os.getenv("MIN_LEAF_RATIO", "0.20"))   # plant-colour gate
RESCALE = os.getenv("RESCALE", "unit")  # "unit" -> /255 ; "mobilenet" -> [-1, 1]


def load_class_names():
    if os.path.exists(NAMES_PATH):
        with open(NAMES_PATH) as f:
            return json.load(f)
    return CLASS_NAMES


def leaf_ratio(img):
    """Fraction of pixels with a leaf-like colour (green/yellow/brown-green hues)."""
    hsv = np.asarray(img.resize((128, 128)).convert("HSV"))
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return float(((h >= 14) & (h <= 120) & (s >= 40) & (v >= 40)).mean())


def preprocess(img):
    x = np.asarray(img.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR), dtype="float32")
    x = x / 127.5 - 1.0 if RESCALE == "mobilenet" else x / 255.0
    return x[None]


class Predictor:
    def __init__(self):
        from tensorflow import keras  # imported here so tooling can import this module without TF
        self.names = load_class_names()
        model = keras.models.load_model(MODEL_PATH, compile=False)
        if model.output_shape[-1] != len(self.names):
            raise RuntimeError(
                f"Model has {model.output_shape[-1]} outputs but {len(self.names)} class names are configured."
            )
        gap = model.get_layer("global_average_pooling2d").output
        self.fm = keras.Model(model.input, [gap, model.output])  # one pass -> embedding + probabilities
        self.stats = None
        if os.path.exists(STATS_PATH):
            d = np.load(STATS_PATH)
            self.stats = (d["centroids"], float(d["threshold"]))
        self._lock = threading.Lock()
        self.fm(np.zeros((1, IMG_SIZE, IMG_SIZE, 3), "float32"), training=False)  # warm-up

    def embed(self, img):
        with self._lock:
            feats, probs = self.fm(preprocess(img), training=False)
        return feats.numpy()[0], probs.numpy()[0]

    def predict(self, img):
        ratio = leaf_ratio(img)
        if ratio < MIN_LEAF_RATIO:
            return {"status": "rejected", "reason": "not_a_leaf"}
        feats, probs = self.embed(img)
        if self.stats is not None:
            centroids, threshold = self.stats
            sim = float((centroids @ (feats / (np.linalg.norm(feats) + 1e-9))).max())
            if sim < threshold:
                return {"status": "rejected", "reason": "not_tomato"}
        order = np.argsort(probs)[::-1]
        top = int(order[0])
        if probs[top] < MIN_CONFIDENCE:
            return {"status": "rejected", "reason": "low_confidence",
                    "confidence": round(float(probs[top]) * 100, 1)}
        return {
            "status": "ok",
            "label": self.names[top],
            "confidence": round(float(probs[top]) * 100, 1),
            "top3": [{"label": self.names[int(i)], "confidence": round(float(probs[i]) * 100, 1)}
                     for i in order[:3]],
        }
