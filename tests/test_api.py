import subprocess, sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent

if not (ROOT / "models" / "tier1.joblib").exists():
    subprocess.run([sys.executable, "-m", "ml.train", "--demo"], cwd=ROOT, check=True)

from app.main import app  # noqa: E402

LOW = dict(tier=1, age=24, bmi=20.5, cycle_irregular=0, weight_gain=0, hair_growth=0,
           skin_darkening=0, hair_loss=0, pimples=0, fast_food=0, regular_exercise=1)
HIGH = dict(tier=1, age=24, bmi=29, cycle_irregular=1, weight_gain=1, hair_growth=1,
            skin_darkening=1, hair_loss=1, pimples=1, fast_food=1, regular_exercise=0)
LABS = dict(follicle_l=14, follicle_r=13, amh=8.0, fsh_lh=0.8)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_meta(client):
    m = client.get("/api/meta").json()
    assert "1" in m["features"] and "2" in m["features"]


def test_high_profile_scores_above_low_profile(client):
    lo = client.post("/api/predict", json=LOW).json()
    hi = client.post("/api/predict", json=HIGH).json()
    assert hi["risk"] > lo["risk"]
    assert lo["band"] == "low"
    assert hi["band"] in ("moderate", "high")
    assert hi["factors"] and hi["disclaimer"]


def test_tier2(client):
    r = client.post("/api/predict", json={**HIGH, "tier": 2, **LABS})
    assert r.status_code == 200 and r.json()["tier"] == 2


def test_tier2_requires_labs(client):
    assert client.post("/api/predict", json={**HIGH, "tier": 2}).status_code == 422


def test_validation_rejects_bad_values(client):
    assert client.post("/api/predict", json={**LOW, "bmi": 200}).status_code == 422
    assert client.post("/api/predict", json={**LOW, "pimples": 5}).status_code == 422


def test_report_is_pdf(client):
    r = client.post("/api/report", json=HIGH)
    assert r.status_code == 200 and r.content[:4] == b"%PDF"


def test_frontend_served(client):
    assert "PCOS" in client.get("/").text
