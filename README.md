# PCOS Risk Screening: Two-Tier Explainable ML System

Full-stack final-year project: **FastAPI backend + vanilla JS frontend + ML training pipeline**.

- **Tier 1** predicts risk from easy inputs only (age, BMI, cycle, symptoms, lifestyle). No lab test needed.
- **Tier 2** adds ultrasound and hormone values (follicle counts, AMH, FSH/LH) for higher accuracy.
- Every prediction comes with the factors that raised or lowered the risk, advice for the next step, and a downloadable PDF report.
- English and Hindi interface. Nothing the user enters is stored.

> **Important:** this zip ships with a **demo model trained on synthetic data** so it runs immediately.
> The red banner in the app says so. For your real project and report, download the Kaggle dataset
> and retrain (Step 2). Never submit demo numbers as your results.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Always retrain first on your own PC** (the saved model must match your installed libraries):
`python -m ml.train --demo` (or `python -m ml.train` once the Kaggle file is in `data/`).

Open http://localhost:8000 (app) and http://localhost:8000/docs (interactive API docs).

## Step 2: train on the real dataset

1. Download **"Polycystic Ovary Syndrome (PCOS)" by Prasoon Kottarathil** from Kaggle.
2. Put `PCOS_data_without_infertility.xlsx` inside the `data/` folder.
3. Run `python -m ml.train`

This compares Logistic Regression, Random Forest, XGBoost and SVM with 5-fold stratified CV, then saves:

| Output (in `models/`) | Use in your report |
|---|---|
| `reports/tier1_comparison.csv`, `tier2_comparison.csv` | Model comparison tables (Chapter 8) |
| `reports/tier*_roc.png` | ROC curves |
| `reports/tier*_confusion.png` | Confusion matrices |
| `reports/tier*_shap.png` | SHAP summary plots |
| `metadata.json` | Data source, row count, metrics |

If a column name differs in your copy of the file, edit `KAGGLE_MAP` in `ml/data.py`.
Restart the server after retraining. The demo banner disappears automatically.


## Step 3: build the final report and presentation

After training on the real dataset, run:

```bash
python -m tools.build_all
```

This writes to `deliverables/`: `PCOS_Project_Report.docx` (about 27 pages, with architecture and pipeline diagrams,
EDA plots, model comparison tables and graphs, ROC curves, confusion matrices, SHAP and feature importance),
`PCOS_Presentation.pptx` (18 slides with editable charts and speaker notes) and all figures as PNG files.
All numbers and graphs come from your own training run. The copies shipped in this zip use synthetic demo data
and carry a red "DEMO DATA" marker, which disappears once you rebuild from real data.
Before submitting, fill in the [bracketed] names, the literature review papers and the survey table.

## Project structure

```
app/
  main.py        FastAPI app: /api/predict, /api/report, /api/meta, /api/health, serves frontend
  schemas.py     Request/response validation (pydantic)
  features.py    Feature lists, labels, risk thresholds (shared by training and API)
  predictor.py   Loads models, predicts, explains, picks risk band and advice
  report.py      PDF report generator (reportlab)
ml/
  data.py        Kaggle loader and synthetic demo generator
  train.py       Model comparison, evaluation plots, export
frontend/        index.html, styles.css, app.js (no build step)
models/          Trained models, metadata, report figures
tests/           pytest API tests
data/            Put the Kaggle .xlsx here
Dockerfile
```

## API

`POST /api/predict`

```json
{"tier": 1, "age": 24, "bmi": 29, "cycle_irregular": 1, "weight_gain": 1,
 "hair_growth": 1, "skin_darkening": 1, "hair_loss": 1, "pimples": 1,
 "fast_food": 1, "regular_exercise": 0}
```

Tier 2 also needs `follicle_l`, `follicle_r`, `amh`, `fsh_lh`. The response contains `risk_percent`, `band`
(low / moderate / high), `advice`, `factors` (top contributions) and a disclaimer. `POST /api/report`
takes the same body and returns a PDF.

## How the pieces map to your report

- **Explainability:** the API uses XGBoost's built-in SHAP-style contributions for each patient. `train.py` produces the global SHAP plot.
- **Why XGBoost is deployed:** it gives fast, exact per-patient contributions. The other models are compared in the report.
- **Recall focus:** risk bands use a 0.40 threshold (moderate) and 0.70 (high) to favour catching true cases. Change them in `app/features.py`.
- **Imbalance:** handled with class weights inside the training split, so no test-set leakage.

## Tests and Docker

```bash
python -m pytest -q
docker build -t pcos-app . && docker run -p 8000:8000 pcos-app
```

## Limitations to state in your viva

Small, single-region dataset; self-reported symptoms in Tier 1; no clinical validation; this is a screening aid and
not a diagnosis.
