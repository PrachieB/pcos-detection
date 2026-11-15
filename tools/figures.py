"""Generates every figure used by the report and the presentation from real project outputs."""
import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from matplotlib.patches import FancyBboxPatch

from app.features import FEATURES, LABELS, TIER2
from ml.data import TARGET, load_real, make_demo
from ml.train import DATA_FILE, MODELS

PLUM, TEAL, ROSE, AMBER, INK, MUTED, SOFT = "#4B2E83", "#2E7D6B", "#B3304A", "#C27A12", "#231F2E", "#6B6578", "#ECE6F6"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#BBB4C8", "axes.labelcolor": INK, "text.color": INK})


def load_dataset():
    if DATA_FILE.exists():
        return load_real(DATA_FILE), "real"
    return make_demo(), "demo"


def _box(ax, cx, cy, w, h, text, fc, tc="white", fs=11):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec="none"))
    ax.text(cx, cy, text, ha="center", va="center", color=tc, fontsize=fs, fontweight="bold", linespacing=1.25)


def _arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.8, shrinkA=0, shrinkB=0))


def architecture(out):
    fig, ax = plt.subplots(figsize=(13, 6.4)); ax.set_xlim(0, 13); ax.set_ylim(0, 6.4); ax.axis("off")
    ax.text(0.1, 6.05, "Online screening flow", fontsize=13, fontweight="bold", color=PLUM)
    row = 4.75
    xs = [1.3, 3.9, 6.5, 9.1, 11.7]
    labels = ["User\n(web browser)", "Frontend\nHTML, CSS, JS\nEnglish / Hindi", "FastAPI backend\nvalidation and\ntier routing",
              "Tier 1 or Tier 2\nXGBoost pipeline\nimpute, scale, predict", "Explainer\nfactor contributions\nrisk band and advice"]
    cols = [MUTED, PLUM, PLUM, TEAL, TEAL]
    for x, t, c in zip(xs, labels, cols):
        _box(ax, x, row, 2.2, 1.35, t, c, fs=10.5)
    for a, b in zip(xs, xs[1:]):
        _arrow(ax, a + 1.12, row, b - 1.12, row)
    _box(ax, 6.5, 2.95, 5.2, 0.95, "Response: risk %, band, top factors, advice, PDF report", SOFT, tc=PLUM, fs=11)
    ax.plot([11.7, 11.7], [row - 0.7, 2.95], color=MUTED, lw=1.8)
    ax.annotate("", xy=(9.1, 2.95), xytext=(11.7, 2.95), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.8))
    ax.text(0.1, 1.95, "Offline training flow", fontsize=13, fontweight="bold", color=PLUM)
    row2 = 0.85
    xs2 = [1.8, 5.0, 8.2, 11.4]
    labels2 = ["Kaggle PCOS dataset\n(541 patient records)", "ml/train.py\nclean, split, 5-fold CV\n4 models compared",
               "Evaluation\nrecall, F1, ROC-AUC\nconfusion, SHAP", "models/ folder\ntier1 and tier2\nsaved pipelines"]
    for x, t, c in zip(xs2, labels2, [MUTED, AMBER, AMBER, TEAL]):
        _box(ax, x, row2, 2.7, 1.25, t, c, fs=10.5)
    for a, b in zip(xs2, xs2[1:]):
        _arrow(ax, a + 1.38, row2, b - 1.38, row2)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


def pipeline(out):
    fig, ax = plt.subplots(figsize=(13, 5.2)); ax.set_xlim(0, 13); ax.set_ylim(0, 5.2); ax.axis("off")
    top = ["Load data\nand rename\ncolumns", "Clean and\nmedian-impute\nmissing values", "Explore\n(EDA plots)",
           "Stratified\n80/20 split", "Scale\nfeatures"]
    bot = ["Train 4 models\n5-fold CV", "Evaluate\nrecall, F1, AUC", "Select and\ndeploy XGBoost", "Explain\nwith SHAP", "Web app\nand PDF report"]
    xs = [1.3, 3.9, 6.5, 9.1, 11.7]
    for i, (x, t) in enumerate(zip(xs, top)):
        _box(ax, x, 4.1, 2.1, 1.25, t, PLUM if i < 4 else TEAL, fs=10.5)
    for a, b in zip(xs, xs[1:]):
        _arrow(ax, a + 1.07, 4.1, b - 1.07, 4.1)
    ax.plot([11.7, 11.7], [3.45, 2.95], color=MUTED, lw=1.8)
    ax.plot([11.7, 1.3], [2.95, 2.95], color=MUTED, lw=1.8)
    _arrow(ax, 1.3, 2.95, 1.3, 2.4)
    for i, (x, t) in enumerate(zip(xs, bot)):
        _box(ax, x, 1.75, 2.1, 1.25, t, AMBER if i < 2 else TEAL, fs=10.5)
    for a, b in zip(xs, xs[1:]):
        _arrow(ax, a + 1.07, 1.75, b - 1.07, 1.75)
    ax.text(6.5, 0.45, "Preprocessing is fitted on training folds only, so no test data leaks into training.",
            ha="center", color=MUTED, fontsize=11)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


def eda(df, out_dir):
    paths = {}
    fig, ax = plt.subplots(figsize=(4.8, 4))
    counts = df[TARGET].value_counts().sort_index()
    bars = ax.bar(["No PCOS", "PCOS"], counts.values, color=[TEAL, ROSE], width=0.55)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v}\n({v / counts.sum() * 100:.0f}%)", ha="center", va="bottom")
    ax.set_ylabel("Patients"); ax.set_ylim(0, counts.max() * 1.22); ax.set_title("Class distribution", loc="left", fontweight="bold")
    paths["class"] = out_dir / "fig_class_distribution.png"; fig.savefig(paths["class"], dpi=200, bbox_inches="tight"); plt.close(fig)

    d = df.copy(); d["follicles_total"] = d["follicle_l"] + d["follicle_r"]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4))
    for ax, col, title in zip(axes, ["bmi", "amh", "follicles_total"], ["BMI", "AMH (ng/mL)", "Total follicle count"]):
        groups = [d.loc[d[TARGET] == k, col].dropna() for k in (0, 1)]
        bp = ax.boxplot(groups, tick_labels=["No PCOS", "PCOS"], patch_artist=True, widths=0.55, showfliers=False)
        for patch, c in zip(bp["boxes"], [TEAL, ROSE]):
            patch.set_facecolor(c); patch.set_alpha(0.75)
        for m in bp["medians"]: m.set_color(INK)
        ax.set_title(title, loc="left", fontweight="bold")
    paths["box"] = out_dir / "fig_boxplots.png"; fig.tight_layout(); fig.savefig(paths["box"], dpi=200, bbox_inches="tight"); plt.close(fig)

    corr = df[TIER2 + [TARGET]].corr()
    names = [LABELS.get(c, "PCOS (target)") for c in corr.columns]
    fig, ax = plt.subplots(figsize=(8.4, 7))
    im = ax.imshow(corr.values, cmap="PuOr_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)), names, rotation=60, ha="right", fontsize=8.5); ax.set_yticks(range(len(names)), names, fontsize=8.5)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f"{corr.values[i, j]:.1f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(corr.values[i, j]) > 0.55 else INK)
    fig.colorbar(im, ax=ax, shrink=0.75); ax.set_title("Correlation between features", loc="left", fontweight="bold")
    for s in ax.spines.values(): s.set_visible(False)
    paths["corr"] = out_dir / "fig_correlation.png"; fig.savefig(paths["corr"], dpi=200, bbox_inches="tight"); plt.close(fig)
    return paths


def comparison_charts(meta, out_dir):
    paths = {}
    for tier in (1, 2):
        comp = pd.DataFrame(meta["tiers"][str(tier)]["comparison"])
        metrics = [("precision", PLUM), ("recall", ROSE), ("f1", AMBER), ("roc_auc", TEAL)]
        x = np.arange(len(comp)); w = 0.2
        fig, ax = plt.subplots(figsize=(9, 4.4))
        for i, (m, c) in enumerate(metrics):
            ax.bar(x + (i - 1.5) * w, comp[m], w, label=m.replace("roc_auc", "ROC-AUC").replace("f1", "F1").title()
                   if m != "roc_auc" else "ROC-AUC", color=c)
        ax.set_xticks(x, comp["model"]); ax.set_ylim(0, 1.08); ax.set_ylabel("Score")
        ax.set_title(f"Tier {tier}: model comparison on the held-out test set", loc="left", fontweight="bold")
        ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1))
        paths[f"cmp{tier}"] = out_dir / f"fig_comparison_tier{tier}.png"
        fig.savefig(paths[f"cmp{tier}"], dpi=200, bbox_inches="tight"); plt.close(fig)

    names = ["precision", "recall", "f1", "roc_auc"]; pretty = ["Precision", "Recall", "F1", "ROC-AUC"]
    t1 = [meta["tiers"]["1"]["metrics"][n] for n in names]; t2 = [meta["tiers"]["2"]["metrics"][n] for n in names]
    x = np.arange(4); fig, ax = plt.subplots(figsize=(7.5, 4.2))
    b1 = ax.bar(x - 0.19, t1, 0.38, label="Tier 1 (no lab tests)", color=PLUM)
    b2 = ax.bar(x + 0.19, t2, 0.38, label="Tier 2 (with ultrasound + hormones)", color=TEAL)
    for bars in (b1, b2):
        for b in bars: ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01, f"{b.get_height():.2f}", ha="center", fontsize=9)
    ax.set_xticks(x, pretty); ax.set_ylim(0, 1.15); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    ax.set_title("Deployed XGBoost: Tier 1 vs Tier 2", loc="left", fontweight="bold")
    paths["tiers"] = out_dir / "fig_tier_comparison.png"; fig.savefig(paths["tiers"], dpi=200, bbox_inches="tight"); plt.close(fig)
    return paths


def importance(df, out_dir):
    """Mean absolute contribution per feature on the full dataset (XGBoost pred_contribs)."""
    result, fig = {}, plt.figure(figsize=(11, 4.8))
    for k, tier in enumerate((1, 2), start=1):
        pipe, feats = joblib.load(MODELS / f"tier{tier}.joblib")
        Xt = np.asarray(pipe[:-1].transform(df[feats]), dtype=np.float32)
        contrib = pipe.named_steps["clf"].get_booster().predict(xgb.DMatrix(Xt), pred_contribs=True)[:, :-1]
        imp = pd.Series(np.abs(contrib).mean(axis=0), index=feats).sort_values()
        result[tier] = imp.sort_values(ascending=False)
        ax = fig.add_subplot(1, 2, k)
        ax.barh([LABELS[f] for f in imp.index], imp.values, color=PLUM if tier == 1 else TEAL)
        ax.set_title(f"Tier {tier}: feature importance", loc="left", fontweight="bold")
        ax.set_xlabel("Mean absolute contribution (log-odds)")
    fig.tight_layout(); path = out_dir / "fig_importance.png"; fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)
    return path, result


def build_all(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = json.loads((MODELS / "metadata.json").read_text())
    df, source = load_dataset()
    figs = {"architecture": out_dir / "fig_architecture.png", "pipeline": out_dir / "fig_pipeline.png"}
    architecture(figs["architecture"]); pipeline(figs["pipeline"])
    figs.update(eda(df, out_dir)); figs.update(comparison_charts(meta, out_dir))
    figs["importance"], imp = importance(df, out_dir)
    rep = MODELS / "reports"
    for tier in (1, 2):
        for kind in ("roc", "confusion", "shap"):
            src = rep / f"tier{tier}_{kind}.png"
            figs[f"{kind}{tier}"] = src if src.exists() else None
    return figs, meta, df, source, imp
