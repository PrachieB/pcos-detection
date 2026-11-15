"""Data loading: the real Kaggle dataset, or a clearly-labelled synthetic demo set."""
from pathlib import Path
import numpy as np
import pandas as pd

from app.features import TIER2

TARGET = "pcos"

# Kaggle column name -> clean internal name
KAGGLE_MAP = {
    "PCOS (Y/N)": TARGET,
    "Age (yrs)": "age",
    "BMI": "bmi",
    "Cycle(R/I)": "cycle_irregular",
    "Weight gain(Y/N)": "weight_gain",
    "hair growth(Y/N)": "hair_growth",
    "Skin darkening (Y/N)": "skin_darkening",
    "Hair loss(Y/N)": "hair_loss",
    "Pimples(Y/N)": "pimples",
    "Fast food (Y/N)": "fast_food",
    "Reg.Exercise(Y/N)": "regular_exercise",
    "Follicle No. (L)": "follicle_l",
    "Follicle No. (R)": "follicle_r",
    "AMH(ng/mL)": "amh",
    "FSH/LH": "fsh_lh",
}


def load_real(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Full_new")
    df.columns = df.columns.str.strip()
    missing = [c for c in KAGGLE_MAP if c not in df.columns]
    if missing:
        raise KeyError(
            f"Columns not found in dataset: {missing}\nAvailable: {df.columns.tolist()}\n"
            "Edit KAGGLE_MAP in ml/data.py to match."
        )
    df = df[list(KAGGLE_MAP)].rename(columns=KAGGLE_MAP)
    df = df.apply(pd.to_numeric, errors="coerce")
    # In the Kaggle file Cycle(R/I): 2 = regular, 4 (or 5) = irregular
    df["cycle_irregular"] = (df["cycle_irregular"] != 2).astype(int)
    return df.dropna(subset=[TARGET]).reset_index(drop=True)


def make_demo(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """SYNTHETIC data for running the pipeline end-to-end without the real dataset.

    Relationships are loosely inspired by clinical literature but are INVENTED.
    Models trained on this must never be presented as real results.
    """
    rng = np.random.default_rng(seed)
    y = rng.binomial(1, 0.30, n)
    p = lambda a, b: np.where(y == 1, b, a)  # noqa: E731
    flag = lambda a, b: rng.binomial(1, p(a, b))  # noqa: E731

    df = pd.DataFrame({
        "age": np.clip(rng.normal(28, 5, n), 16, 45).round().astype(int),
        "bmi": np.clip(rng.normal(22.5 + 3.5 * y, 3.5), 15, 42).round(1),
        "cycle_irregular": flag(0.12, 0.78),
        "weight_gain": flag(0.20, 0.60),
        "hair_growth": flag(0.07, 0.55),
        "skin_darkening": flag(0.10, 0.50),
        "hair_loss": flag(0.20, 0.50),
        "pimples": flag(0.25, 0.60),
        "fast_food": flag(0.35, 0.55),
        "regular_exercise": flag(0.40, 0.28),
        "follicle_l": rng.poisson(p(5, 11)),
        "follicle_r": rng.poisson(p(5, 11)),
        "amh": np.clip(rng.lognormal(np.log(p(3.0, 6.5)), 0.5), 0.1, 30).round(2),
        "fsh_lh": np.clip(rng.normal(p(2.0, 1.0), 0.6), 0.1, 20).round(2),
    })
    flip = rng.random(n) < 0.05  # label noise so results are not trivially perfect
    df[TARGET] = np.where(flip, 1 - y, y)
    return df[TIER2 + [TARGET]]
