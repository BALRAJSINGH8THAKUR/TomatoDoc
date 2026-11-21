# TomatoDoc – Tomato Leaf Disease Detector

MobileNetV2 model (128×128, 10 classes) + Flask backend + responsive frontend.

## Run locally
```
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt                       # Python 3.10–3.12
python app.py                                         # http://127.0.0.1:5000
```

## Deploy (Render / Railway / any Procfile host)
- Build: `pip install -r requirements.txt` · Start: `gunicorn app:app --workers 1 --threads 2 --timeout 180`
- Use **1 worker** (TensorFlow is memory-heavy; ~1 GB RAM recommended, free 512 MB tiers may fail).
- Health check path: `/health`

## "Not a tomato leaf" rejection (3 layers)
1. **Colour gate** – rejects photos with almost no plant-coloured pixels (faces, objects, screenshots).
2. **Confidence gate** – rejects when the top softmax score < 70 % (`MIN_CONFIDENCE`).
3. **Feature-distance gate** (strongest) – run once on your machine with your training data:
   `python build_ood_stats.py path/to/PlantVillage_tomato_folders --negatives path/to/apple_potato_leaves`
   This writes `ood_stats.npz`; the app uses it automatically.

A classifier trained only on tomato classes cannot truly recognise "other", so for rock-solid rejection of
look-alike leaves, retrain with an 11th class `not_tomato` (e.g. apple/potato/grape leaves from PlantVillage),
then add it to `knowledge.py` / `class_names.json`.

## Things to verify
- Class order in `knowledge.py` must match training (alphabetical folders). Override with `class_names.json`.
- Preprocessing is `/255`. If you trained with `mobilenet_v2.preprocess_input`, set env `RESCALE=mobilenet`.
