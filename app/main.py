"""FastAPI backend. Serves the JSON API and the static frontend.

Run:  uvicorn app.main:app --reload
Docs: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.features import FEATURES, HIGH_THRESHOLD, MODERATE_THRESHOLD
from app.predictor import Predictor
from app.report import build_pdf
from app.schemas import PredictRequest, PredictResponse

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
state: dict = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["predictor"] = Predictor()
    yield


app = FastAPI(title="PCOS Risk Screening API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _run(req: PredictRequest) -> tuple[dict, dict]:
    values = req.model_dump()
    return state["predictor"].predict(req.tier, values), values


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    p: Predictor = state["predictor"]
    return {
        "demo_model": p.is_demo,
        "data_source": p.meta.get("data_source"),
        "n_rows": p.meta.get("n_rows"),
        "trained_at": p.meta.get("trained_at"),
        "features": {str(t): f for t, f in FEATURES.items()},
        "thresholds": {"moderate": MODERATE_THRESHOLD, "high": HIGH_THRESHOLD},
        "metrics": {t: v["metrics"] for t, v in p.meta.get("tiers", {}).items()},
    }


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    result, _ = _run(req)
    return result


@app.post("/api/report")
def report(req: PredictRequest):
    result, values = _run(req)
    pdf = build_pdf(result, values)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="pcos_screening_report.pdf"'})


# Static frontend last, so /api/* routes win.
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
