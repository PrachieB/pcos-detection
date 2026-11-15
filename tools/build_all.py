"""Builds the final report (.docx), presentation (.pptx) and all figures from your training results.

Usage (after `python -m ml.train` on the real dataset):
    python -m tools.build_all
Outputs go to the deliverables/ folder.
"""
from pathlib import Path

from tools.build_ppt import build as build_ppt
from tools.build_report import build as build_report
from tools.figures import build_all as build_figures

OUT = Path(__file__).resolve().parent.parent / "deliverables"

if __name__ == "__main__":
    figs, meta, df, source, imp = build_figures(OUT / "figures")
    app_shot = OUT / "figures" / "fig_app.png"
    figs["app"] = app_shot if app_shot.exists() else None
    print("Data source:", source)
    print("Report:", build_report(figs, meta, source, imp, OUT / "PCOS_Project_Report.docx"))
    print("Slides:", build_ppt(figs, meta, source, imp, OUT / "PCOS_Presentation.pptx"))
    if source != "real":
        print("\nNOTE: built from synthetic demo data. Put the Kaggle file in data/, run `python -m ml.train`, then run this again.")
