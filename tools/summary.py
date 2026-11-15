"""Turns training outputs into numbers and sentences shared by the report and the slides."""
import pandas as pd

from app.features import LABELS
from app.predictor import Predictor

PROFILES = {
    "Profile A: no symptoms, regular periods": dict(tier=1, age=22, bmi=20.5, cycle_irregular=0, weight_gain=0, hair_growth=0,
        skin_darkening=0, hair_loss=0, pimples=0, fast_food=0, regular_exercise=1),
    "Profile B: irregular periods, acne, extra hair": dict(tier=1, age=25, bmi=27.5, cycle_irregular=1, weight_gain=0, hair_growth=1,
        skin_darkening=0, hair_loss=0, pimples=1, fast_food=1, regular_exercise=0),
    "Profile C: many symptoms, high BMI": dict(tier=1, age=24, bmi=29.5, cycle_irregular=1, weight_gain=1, hair_growth=1,
        skin_darkening=1, hair_loss=1, pimples=1, fast_food=1, regular_exercise=0),
}


def sample_predictions():
    pred = Predictor()
    rows = []
    for name, v in PROFILES.items():
        r = pred.predict(v["tier"], v)
        rows.append((name, f"{r['risk_percent']:.1f}%", r["band"].capitalize(), LABELS.get(r["factors"][0]["feature"], "")))
    return rows


def best_model(comp: list[dict]) -> dict:
    return sorted(comp, key=lambda d: (d["recall"], d["roc_auc"]), reverse=True)[0]


def narrative(meta: dict, imp: dict) -> dict:
    t1, t2 = meta["tiers"]["1"], meta["tiers"]["2"]
    m1, m2 = t1["metrics"], t2["metrics"]
    b1, b2 = best_model(t1["comparison"]), best_model(t2["comparison"])
    top1 = [LABELS[f] for f in imp[1].index[:3]]
    top2 = [LABELS[f] for f in imp[2].index[:3]]
    d_rec = (m2["recall"] - m1["recall"]) * 100
    d_auc = m2["roc_auc"] - m1["roc_auc"]
    return {
        "n_rows": meta["n_rows"], "pos_rate": meta["positive_rate"] * 100,
        "n_train": t1["n_train"], "n_test": t1["n_test"],
        "m1": m1, "m2": m2, "b1": b1, "b2": b2, "top1": top1, "top2": top2,
        "tier_sentence": (f"Tier 2 recall was {m2['recall']:.2f} against {m1['recall']:.2f} for Tier 1 "
                          f"({d_rec:+.1f} percentage points), and ROC-AUC was {m2['roc_auc']:.2f} against "
                          f"{m1['roc_auc']:.2f} ({d_auc:+.3f})."),
        "best1_sentence": f"On Tier 1, {b1['model']} had the highest recall ({b1['recall']:.2f}) on the test set.",
        "best2_sentence": f"On Tier 2, {b2['model']} had the highest recall ({b2['recall']:.2f}) on the test set.",
        "deploy_sentence": (f"XGBoost was deployed for both tiers because it gives fast, exact per-patient factor "
                            f"contributions. Its test recall was {m1['recall']:.2f} (Tier 1) and {m2['recall']:.2f} (Tier 2)."),
        "top1_sentence": "The strongest Tier 1 factors were " + ", ".join(top1) + ".",
        "top2_sentence": "The strongest Tier 2 factors were " + ", ".join(top2) + ".",
    }
