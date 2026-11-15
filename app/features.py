"""Single source of truth for the features used by both training and the API."""

TIER1 = [
    "age", "bmi", "cycle_irregular", "weight_gain", "hair_growth",
    "skin_darkening", "hair_loss", "pimples", "fast_food", "regular_exercise",
]
TIER2_EXTRA = ["follicle_l", "follicle_r", "amh", "fsh_lh"]
TIER2 = TIER1 + TIER2_EXTRA
FEATURES = {1: TIER1, 2: TIER2}

LABELS = {
    "age": "Age",
    "bmi": "BMI",
    "cycle_irregular": "Irregular cycle",
    "weight_gain": "Recent weight gain",
    "hair_growth": "Excess facial/body hair",
    "skin_darkening": "Skin darkening",
    "hair_loss": "Hair loss",
    "pimples": "Acne / pimples",
    "fast_food": "Frequent fast food",
    "regular_exercise": "Regular exercise",
    "follicle_l": "Follicle count (left ovary)",
    "follicle_r": "Follicle count (right ovary)",
    "amh": "AMH level",
    "fsh_lh": "FSH/LH ratio",
}

# Decision thresholds on predicted probability (below 0.5 favours recall)
MODERATE_THRESHOLD = 0.40
HIGH_THRESHOLD = 0.70
