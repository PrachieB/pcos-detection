"""Builds the downloadable PDF screening report (in memory, nothing is stored)."""
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.features import LABELS

BAND_COLOR = {"low": "#2E7D6B", "moderate": "#C27A12", "high": "#B3304A"}
YESNO = {"cycle_irregular", "weight_gain", "hair_growth", "skin_darkening",
         "hair_loss", "pimples", "fast_food", "regular_exercise"}


def _fmt(key: str, value: float) -> str:
    if key in YESNO:
        return "Yes" if value else "No"
    return f"{value:g}"


def build_pdf(result: dict, inputs: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title="PCOS Risk Screening Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, alignment=0, textColor=colors.HexColor("#231F2E"))
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=colors.HexColor("#4B2E83"), spaceBefore=12)
    body = ParagraphStyle("body", parent=ss["BodyText"], leading=15)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, textColor=colors.HexColor("#6B6578"))
    band_col = BAND_COLOR[result["band"]]

    s = [Paragraph("PCOS Risk Screening Report", h1),
         Paragraph(datetime.now().strftime("Generated %d %B %Y, %H:%M"), small), Spacer(1, 8)]

    if result["demo_model"]:
        s += [Paragraph("<b>DEMO MODEL:</b> trained on synthetic data. This result is not meaningful.",
                        ParagraphStyle("warn", parent=body, textColor=colors.HexColor("#B3304A"))), Spacer(1, 6)]

    s += [Paragraph(f'<font size="26" color="{band_col}"><b>{result["risk_percent"]:.1f}%</b></font>', body),
          Paragraph(f'<font color="{band_col}"><b>{result["headline"]}</b></font> '
                    f'(Tier {result["tier"]} screening)', body),
          Paragraph("Suggested next steps", h2)]
    s += [Paragraph(f"&bull; {a}", body) for a in result["advice"]]

    s.append(Paragraph("What influenced this result", h2))
    rows = [["Factor", "Your value", "Effect"]] + [
        [f["label"], _fmt(f["feature"], f["value"]),
         "Raises risk" if f["direction"] == "raises" else "Lowers risk"] for f in result["factors"]]
    t = Table(rows, colWidths=[85 * mm, 35 * mm, 40 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B2E83")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDD8E6")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F4F9")]),
                           ("PADDING", (0, 0), (-1, -1), 6)]))
    s.append(t)

    s.append(Paragraph("Information you entered", h2))
    rows = [[LABELS[k], _fmt(k, v)] for k, v in inputs.items() if k in LABELS and v is not None]
    t2 = Table(rows, colWidths=[85 * mm, 75 * mm])
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDD8E6")),
                            ("PADDING", (0, 0), (-1, -1), 5)]))
    s += [t2, Spacer(1, 14), Paragraph(result["disclaimer"], small)]
    doc.build(s)
    return buf.getvalue()
