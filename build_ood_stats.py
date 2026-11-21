"""Create ood_stats.npz so the app can reject non-tomato leaves (apple, potato, ...).

Usage:
  python build_ood_stats.py PATH/TO/TRAIN_DATASET [--negatives PATH/TO/NON_TOMATO_LEAVES] [--per-class 200]

PATH/TO/TRAIN_DATASET has one sub-folder per class (the same data you trained on).
--negatives (optional but recommended): a folder of non-tomato leaf photos; the threshold is then
placed between tomato and non-tomato similarity scores instead of using a percentile only.
"""
import argparse, os, random
import numpy as np
from PIL import Image
from predictor import Predictor, STATS_PATH

ap = argparse.ArgumentParser()
ap.add_argument("dataset"); ap.add_argument("--negatives"); ap.add_argument("--per-class", type=int, default=200)
a = ap.parse_args()
EXT = (".jpg", ".jpeg", ".png", ".webp")
p = Predictor()

def feats_of(paths):
    out = []
    for q in paths:
        f, _ = p.embed(Image.open(q).convert("RGB"))
        out.append(f / (np.linalg.norm(f) + 1e-9))
    return np.array(out)

classes = sorted(d for d in os.listdir(a.dataset) if os.path.isdir(os.path.join(a.dataset, d)))
cents, own = [], []
for c in classes:
    d = os.path.join(a.dataset, c)
    files = [os.path.join(d, x) for x in os.listdir(d) if x.lower().endswith(EXT)]
    random.shuffle(files); F = feats_of(files[:a.per_class])
    m = F.mean(0); m /= np.linalg.norm(m); cents.append(m); own.extend(F @ m)
    print(f"{c}: {len(F)} images")
cents = np.array(cents); own = np.array(own)
thr = float(np.percentile(own, 1))  # keep 99% of real tomato leaves
print(f"tomato similarity: min={own.min():.3f} 1st-pct={thr:.3f} median={np.median(own):.3f}")

if a.negatives:
    neg = [os.path.join(a.negatives, x) for x in os.listdir(a.negatives) if x.lower().endswith(EXT)]
    sims = (feats_of(neg) @ cents.T).max(1)
    print(f"non-tomato similarity: max={sims.max():.3f} median={np.median(sims):.3f}")
    if sims.max() < thr:
        thr = float((sims.max() + thr) / 2); print("clean separation -> threshold set between the two groups")
    else:
        print(f"WARNING: {(sims >= thr).mean()*100:.0f}% of non-tomato images would still pass. "
              "Train with an extra 'not_tomato' class for reliable rejection (see README).")
np.savez(STATS_PATH, centroids=cents, threshold=thr)
print("saved", STATS_PATH, "threshold =", round(thr, 3))
