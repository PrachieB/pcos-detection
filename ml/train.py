"""Train, compare and export the Tier 1 and Tier 2 models.

Usage:
    python -m ml.train                 # uses data/PCOS_data_without_infertility.xlsx if present
    python -m ml.train --demo          # force synthetic demo data (NOT real results)
"""
import argparse, json, warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, RocCurveDisplay,
                             classification_report, confusion_matrix, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

from app.features import FEATURES, MODERATE_THRESHOLD
from ml.data import TARGET, load_real, make_demo

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "PCOS_data_without_infertility.xlsx"
MODELS = ROOT / "models"
REPORTS = MODELS / "reports"


def candidate_models(pos_weight: float) -> dict:
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                                 scale_pos_weight=pos_weight, eval_metric="logloss", random_state=42),
        "SVM (RBF)": SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=42),
    }


def pipeline(clf) -> Pipeline:
    return Pipeline([("imp", SimpleImputer(strategy="median")),
                     ("sc", StandardScaler()), ("clf", clf)])


def run_tier(df: pd.DataFrame, tier: int, source: str) -> dict:
    feats = FEATURES[tier]
    X, y = df[feats], df[TARGET].astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    pos_weight = float((ytr == 0).sum() / (ytr == 1).sum())
    cv = StratifiedKFold(5, shuffle=True, random_state=42)

    rows, fitted = [], {}
    for name, clf in candidate_models(pos_weight).items():
        pipe = pipeline(clf)
        cv_recall = cross_val_score(pipe, Xtr, ytr, cv=cv, scoring="recall").mean()
        pipe.fit(Xtr, ytr)
        proba = pipe.predict_proba(Xte)[:, 1]
        rep = classification_report(yte, (proba >= MODERATE_THRESHOLD).astype(int),
                                    output_dict=True, zero_division=0)
        rows.append({
            "model": name, "cv_recall": round(cv_recall, 3),
            "accuracy": round(rep["accuracy"], 3),
            "precision": round(rep["1"]["precision"], 3),
            "recall": round(rep["1"]["recall"], 3),
            "f1": round(rep["1"]["f1-score"], 3),
            "roc_auc": round(roc_auc_score(yte, proba), 3),
        })
        fitted[name] = pipe
    table = pd.DataFrame(rows)
    print(f"\n=== Tier {tier} ({len(df)} rows, source: {source}) ===")
    print(table.to_string(index=False))

    REPORTS.mkdir(parents=True, exist_ok=True)
    table.to_csv(REPORTS / f"tier{tier}_comparison.csv", index=False)

    fig, ax = plt.subplots(figsize=(6, 5))
    for name, pipe in fitted.items():
        RocCurveDisplay.from_estimator(pipe, Xte, yte, name=name, ax=ax)
    ax.set_title(f"ROC curves - Tier {tier}")
    fig.savefig(REPORTS / f"tier{tier}_roc.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # The API explains predictions with tree contributions, so XGBoost is always deployed.
    final = fitted["XGBoost"]
    proba = final.predict_proba(Xte)[:, 1]
    cm = confusion_matrix(yte, (proba >= MODERATE_THRESHOLD).astype(int))
    ConfusionMatrixDisplay(cm, display_labels=["No PCOS", "PCOS"]).plot(cmap="Purples")
    plt.title(f"Tier {tier} XGBoost (threshold {MODERATE_THRESHOLD})")
    plt.savefig(REPORTS / f"tier{tier}_confusion.png", dpi=200, bbox_inches="tight")
    plt.close()

    try:  # optional SHAP summary plot for the report
        import shap
        Xt = pd.DataFrame(final[:-1].transform(Xte), columns=feats)
        sv = shap.TreeExplainer(final.named_steps["clf"]).shap_values(Xt)
        shap.summary_plot(sv, Xt, show=False)
        plt.savefig(REPORTS / f"tier{tier}_shap.png", dpi=200, bbox_inches="tight")
        plt.close()
    except Exception as exc:  # shap not installed or version mismatch
        print(f"(SHAP plot skipped: {exc})")

    joblib.dump((final, feats), MODELS / f"tier{tier}.joblib")
    best = table[table.model == "XGBoost"].iloc[0].to_dict()
    return {"deployed": "XGBoost", "metrics": best, "comparison": rows,
            "n_train": int(len(Xtr)), "n_test": int(len(Xte))}


def main(demo: bool = False) -> None:
    if not demo and DATA_FILE.exists():
        df, source = load_real(DATA_FILE), "real"
    else:
        if not demo:
            print(f"\n!! {DATA_FILE.name} not found in data/. Falling back to SYNTHETIC demo data.")
            print("!! Results are NOT real. Download the Kaggle dataset for real results.\n")
        df, source = make_demo(), "demo"

    meta = {
        "data_source": source,
        "n_rows": int(len(df)),
        "positive_rate": round(float(df[TARGET].mean()), 3),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "threshold_moderate": MODERATE_THRESHOLD,
        "tiers": {str(t): run_tier(df, t, source) for t in (1, 2)},
    }
    (MODELS / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"\nSaved models and reports to {MODELS}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="force synthetic demo data")
    main(ap.parse_args().demo)
