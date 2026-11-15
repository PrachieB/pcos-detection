import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from app.features import HIGH_THRESHOLD, LABELS, MODERATE_THRESHOLD

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

DISCLAIMER = ("This is a screening aid, not a medical diagnosis. "
              "PCOS can only be confirmed by a doctor using clinical, hormonal and ultrasound assessment.")

HEADLINES = {
    "low": "Lower likelihood of PCOS",
    "moderate": "Moderate likelihood of PCOS",
    "high": "Higher likelihood of PCOS",
}

ADVICE = {
    "low": [
        "Your answers point to a lower likelihood. Keep up regular exercise and a balanced diet.",
        "If your periods are irregular or symptoms persist, see a doctor anyway. A screening score does not rule PCOS out.",
    ],
    "moderate": [
        "Consider booking a visit with a gynaecologist or physician to discuss your symptoms.",
        "Tests that help confirm or rule out PCOS include a pelvic ultrasound and hormone blood tests.",
        "Track your cycle dates for a few months and bring the record to your appointment.",
    ],
    "high": [
        "Please consult a gynaecologist soon. Your answers match the pattern seen in many women with PCOS.",
        "Ask about a pelvic ultrasound and hormone tests to confirm. Early diagnosis helps prevent complications.",
        "Healthy eating, regular activity and good sleep help manage PCOS symptoms, and a doctor can guide you further.",
    ],
}


def band_for(p: float) -> str:
    if p >= HIGH_THRESHOLD:
        return "high"
    if p >= MODERATE_THRESHOLD:
        return "moderate"
    return "low"


class Predictor:
    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models = {}
        for tier in (1, 2):
            path = models_dir / f"tier{tier}.joblib"
            if not path.exists():
                raise FileNotFoundError(
                    f"{path} missing. Run `python -m ml.train` (or `python -m ml.train --demo`) first.")
            self.models[tier] = joblib.load(path)
        meta_path = models_dir / "metadata.json"
        self.meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    @property
    def is_demo(self) -> bool:
        return self.meta.get("data_source") != "real"

    def predict(self, tier: int, values: dict) -> dict:
        pipe, feats = self.models[tier]
        X = pd.DataFrame([[values[f] for f in feats]], columns=feats)
        risk = float(pipe.predict_proba(X)[0, 1])

        # Per-patient explanation: XGBoost's built-in SHAP-style contributions (log-odds)
        Xt = pipe[:-1].transform(X)
        booster = pipe.named_steps["clf"].get_booster()
        contrib = booster.predict(xgb.DMatrix(np.asarray(Xt, dtype=np.float32)), pred_contribs=True)[0][:-1]
        factors = [
            {"feature": f, "label": LABELS[f], "value": float(values[f]),
             "contribution": round(float(c), 3),
             "direction": "raises" if c > 0 else "lowers"}
            for f, c in zip(feats, contrib) if abs(c) >= 0.02
        ]
        factors.sort(key=lambda d: abs(d["contribution"]), reverse=True)

        band = band_for(risk)
        return {
            "tier": tier,
            "risk": round(risk, 4),
            "risk_percent": round(risk * 100, 1),
            "band": band,
            "headline": HEADLINES[band],
            "advice": ADVICE[band],
            "factors": factors[:6],
            "demo_model": self.is_demo,
            "disclaimer": DISCLAIMER,
        }
