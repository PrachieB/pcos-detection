"""Builds the final presentation (.pptx) from the real training outputs."""
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt, Emu
from PIL import Image

from tools.summary import narrative, sample_predictions

PLUM, DEEP, TEAL, ROSE, AMBER = "4B2E83", "2D1B52", "2E7D6B", "B3304A", "C27A12"
INK, MUTED, SOFT, WHITE = "231F2E", "6B6578", "ECE6F6", "FFFFFF"
HEAD, BODY = "Cambria", "Calibri"
W, H = 13.333, 7.5
rgb = lambda h: RGBColor.from_string(h)  # noqa: E731


class Deck:
    def __init__(self, demo):
        self.p = Presentation(); self.p.slide_width, self.p.slide_height = Inches(W), Inches(H)
        self.demo = demo
        self.p.core_properties.title = "PCOS Risk Prediction: Final Year Project"

    def slide(self, bg=WHITE, notes=""):
        s = self.p.slides.add_slide(self.p.slide_layouts[6])
        s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(bg)
        if notes: s.notes_slide.notes_text_frame.text = notes
        if self.demo:
            self.text(s, "DEMO DATA: rebuild after training on the Kaggle dataset", 8.3, 7.08, 4.7, 0.3, 11, ROSE if bg == WHITE else "F4B6C2", bold=True, align="r")
        return s

    def text(self, s, txt, x, y, w, h, size=16, color=INK, bold=False, font=BODY, align="l", anchor="t", italic=False):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
        lines = txt if isinstance(txt, list) else [txt]
        for i, ln in enumerate(lines):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            r = para.add_run(); r.text = ln; f = r.font
            f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, font; f.color.rgb = rgb(color)
            if i: para.space_before = Pt(6)
        return tb

    def title(self, s, t, color=INK):
        self.text(s, t, 0.6, 0.45, 12.1, 0.9, 36, color, True, HEAD, anchor="m")

    def shape(self, s, kind, x, y, w, h, fill, line=None):
        sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        if line: sh.line.color.rgb = rgb(line); sh.line.width = Pt(1)
        else: sh.line.fill.background()
        sh.shadow.inherit = False
        return sh

    def card(self, s, x, y, w, h, head, body, fill=SOFT, hc=PLUM, bsize=15):
        self.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill).adjustments[0] = 0.06
        self.text(s, head, x + 0.3, y + 0.25, w - 0.6, 0.5, 19, hc, True, HEAD)
        self.text(s, body, x + 0.3, y + 0.85, w - 0.6, h - 1.0, bsize, INK)

    def image(self, s, path, x, y, w=None, h=None):
        """Place an image inside the box (x, y, w, h), keeping its aspect ratio, centred."""
        if not path or not Path(path).exists(): return
        iw, ih = Image.open(path).size; ar = iw / ih
        bw, bh = w or W, h or H
        if bw / bh > ar: ph, pw = bh, bh * ar
        else: pw, ph = bw, bw / ar
        s.shapes.add_picture(str(path), Inches(x + (bw - pw) / 2), Inches(y + (bh - ph) / 2), Inches(pw), Inches(ph))

    def stat(self, s, x, y, w, big, small, color=PLUM):
        self.text(s, big, x, y, w, 0.9, 48, color, True, HEAD)
        self.text(s, small, x, y + 0.95, w, 0.6, 14, MUTED)

    def bar_chart(self, s, comp, x, y, w, h):
        cd = CategoryChartData(); cd.categories = [c["model"] for c in comp]
        for key, name in (("precision", "Precision"), ("recall", "Recall"), ("f1", "F1"), ("roc_auc", "ROC-AUC")):
            cd.add_series(name, [c[key] for c in comp])
        gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
        self.style_chart(gf.chart, [PLUM, ROSE, AMBER, TEAL])

    def style_chart(self, ch, colors):
        ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(14); ch.legend.font.color.rgb = rgb(INK); ch.legend.font.name = BODY
        for ser, c in zip(ch.plots[0].series, colors):
            ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(c)
        pl = ch.plots[0]; pl.gap_width = 60; pl.has_data_labels = True
        dl = pl.data_labels; dl.number_format = "0.00"; dl.number_format_is_linked = False
        dl.font.size = Pt(11); dl.font.color.rgb = rgb(INK); dl.font.name = BODY; dl.position = XL_LABEL_POSITION.OUTSIDE_END
        va, ca = ch.value_axis, ch.category_axis
        va.maximum_scale, va.minimum_scale = 1.0, 0.0; va.major_unit = 0.2
        va.tick_labels.font.size = Pt(12); ca.tick_labels.font.size = Pt(13)
        va.tick_labels.font.color.rgb = rgb(MUTED); ca.tick_labels.font.color.rgb = rgb(INK)
        va.major_gridlines.format.line.color.rgb = rgb("DDD8E6"); va.format.line.fill.background()


def table(deck, s, header, rows, x, y, w, colw, size=14, rowh=0.5):
    t = s.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(rowh * (len(rows) + 1))).table
    tot = sum(colw)
    for i, cw in enumerate(colw): t.columns[i].width = Inches(w * cw / tot)
    for r in range(len(rows) + 1):
        t.rows[r].height = Inches(rowh)
        for c in range(len(header)):
            cell = t.cell(r, c); cell.margin_left = cell.margin_right = Inches(0.12)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            txt = header[c] if r == 0 else rows[r - 1][c]
            tf = cell.text_frame; tf.text = ""; run = tf.paragraphs[0].add_run(); run.text = str(txt)
            run.font.size = Pt(size); run.font.name = BODY; run.font.bold = (r == 0)
            run.font.color.rgb = rgb(WHITE if r == 0 else INK)
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(PLUM if r == 0 else (SOFT if r % 2 == 0 else WHITE))


def build(figs, meta, source, imp, out: Path):
    n = narrative(meta, imp); demo = source != "real"; D = Deck(demo)
    m1, m2 = n["m1"], n["m2"]

    # 1 Title
    s = D.slide(DEEP, "Introduce yourself and the project: a screening tool that works with or without lab tests.")
    D.text(s, "Advancing Precision Women's Healthcare", 0.8, 1.7, 11.7, 1.0, 44, WHITE, True, HEAD)
    D.text(s, "A data-driven approach to PCOS risk prediction", 0.8, 2.75, 11.7, 0.7, 28, "D9CCF0", False, HEAD)
    D.text(s, "Two-tier explainable machine learning screening system", 0.8, 3.65, 11.7, 0.5, 18, "D9CCF0", italic=True)
    D.text(s, ["[Student Name]   [Roll No.]", "Guide: [Guide Name]   |   [Department], [College Name]", "Final Year Project 2026-27"], 0.8, 5.0, 8, 1.4, 16, WHITE)
    for i, c in enumerate([ROSE, AMBER, TEAL]):
        D.shape(s, MSO_SHAPE.OVAL, 10.2 + i * 0.85, 4.6, 1.5, 1.5, c).fill.fore_color.rgb = rgb(c)
    D.text(s, "PCOS", 10.2, 5.1, 3.3, 0.5, 20, WHITE, True, HEAD, "c")

    # 2 Problem
    s = D.slide(notes="Explain why this matters: late diagnosis, limited access, serious long-term risks.")
    D.title(s, "PCOS is common, and often found late")
    D.card(s, 0.6, 1.8, 3.9, 3.4, "Late diagnosis", "Many women wait years for a diagnosis because symptoms like irregular periods or acne are easy to dismiss.", bsize=18)
    D.card(s, 4.72, 1.8, 3.9, 3.4, "Limited access", "Confirming PCOS needs ultrasound and hormone tests. These are hard to reach outside big cities.", bsize=18)
    D.card(s, 8.84, 1.8, 3.9, 3.4, "Long-term risk", "Untreated PCOS raises the risk of infertility, type 2 diabetes, heart disease and mental health problems.", bsize=18)
    D.text(s, "Need: a simple, explainable first-level screen that tells a woman whether to see a doctor.", 0.6, 5.7, 12, 0.6, 18, PLUM, True)

    # 3 Objectives
    s = D.slide(notes="Read the six objectives briefly; each one maps to a chapter and a result later.")
    D.title(s, "What this project sets out to do")
    objs = [("Compare models", "Logistic Regression, Random Forest, XGBoost and SVM."), ("Tier 1 model", "Risk from easy inputs, no lab test."),
            ("Tier 2 model", "Adds ultrasound and hormone values."), ("Explain results", "Show what raised or lowered the risk."),
            ("Deploy a web app", "Risk, reasons, advice and a PDF report."), ("Check usability", "Short survey with college students.")]
    for i, (h, b) in enumerate(objs):
        D.card(s, 0.6 + (i % 3) * 4.12, 1.75 + (i // 3) * 2.6, 3.9, 2.3, h, b, bsize=17)

    # 4 Dataset + tiers
    s = D.slide(notes="Two tiers is the key idea: Tier 1 for accessibility, Tier 2 for accuracy in clinics.")
    D.title(s, "One dataset, two screening tiers")
    D.stat(s, 0.6, 1.7, 2.8, f"{n['n_rows']}", "patient records")
    D.stat(s, 3.6, 1.7, 2.8, f"{n['pos_rate']:.0f}%", "PCOS positive", ROSE)
    D.stat(s, 6.6, 1.7, 2.8, "14", "features across both tiers", TEAL)
    D.card(s, 0.6, 3.6, 5.9, 3.0, "Tier 1: no lab tests", "Age, BMI, cycle regularity, weight gain, hair growth, skin darkening, hair loss, acne, fast food, exercise.", bsize=15)
    D.card(s, 6.8, 3.6, 5.9, 3.0, "Tier 2: with reports", "Everything in Tier 1, plus follicle count (left and right), AMH and the FSH/LH ratio.", fill="DDEFEA", hc=TEAL, bsize=15)
    D.text(s, "Source: Kaggle PCOS dataset (Kerala hospitals)" if not demo else "Source: synthetic demo data", 9.6, 1.95, 3.2, 0.9, 14, MUTED)

    # 5 Architecture
    s = D.slide(notes="Walk left to right along the top row, then the training flow at the bottom.")
    D.title(s, "System architecture"); D.image(s, figs["architecture"], 0.6, 1.5, 12.1, 5.2)
    # 6 Pipeline
    s = D.slide(notes="Stress that preprocessing is fitted on training data only, so there is no leakage.")
    D.title(s, "Methodology pipeline"); D.image(s, figs["pipeline"], 0.6, 1.5, 12.1, 5.2)

    # 7 EDA
    s = D.slide(notes="Point out how BMI, AMH and follicle count differ between the two groups.")
    D.title(s, "What the data looks like")
    D.image(s, figs["class"], 0.6, 1.6, 3.9, 4.9); D.image(s, figs["box"], 4.7, 1.9, 8.1, 4.3)

    # 8 Models & metrics
    s = D.slide(notes="Explain why recall is the main metric for a screening tool.")
    D.title(s, "Four models, judged mainly on recall")
    table(D, s, ["Model", "Why it was included"], [["Logistic Regression", "Interpretable baseline"], ["Random Forest", "Robust, non-linear"],
          ["XGBoost", "Strong on small tabular data, exact factor contributions"], ["SVM (RBF)", "Strong margin-based classifier"]],
          0.6, 1.8, 7.3, [2.6, 4.7], size=15, rowh=0.62)
    D.card(s, 8.3, 1.8, 4.4, 3.1, "Why recall?", "In screening, missing a real case is worse than a false alarm. We use stratified 5-fold CV and a 0.40 threshold to favour recall.", bsize=15)
    D.text(s, "Also reported: precision, F1, ROC-AUC and confusion matrix.", 0.6, 5.2, 7.3, 0.6, 16, MUTED)

    # 9-10 Results per tier
    for tier, key, color in ((1, "b1", PLUM), (2, "b2", TEAL)):
        mm = n[f"m{tier}"]; comp = meta["tiers"][str(tier)]["comparison"]
        s = D.slide(notes=f"Tier {tier} results. {n['best%d_sentence' % tier]}")
        D.title(s, f"Tier {tier} results: " + ("no lab tests" if tier == 1 else "with ultrasound and hormones"))
        D.bar_chart(s, comp, 0.6, 1.5, 8.6, 5.3)
        D.stat(s, 9.7, 1.7, 3.2, f"{mm['recall']:.2f}", "recall, deployed XGBoost", color)
        D.stat(s, 9.7, 3.6, 3.2, f"{mm['roc_auc']:.2f}", "ROC-AUC", color)
        D.text(s, n[f"best{tier}_sentence"], 9.7, 5.5, 3.2, 1.3, 14, MUTED)

    # 11 Tier comparison
    s = D.slide(notes="Compare accuracy gain from adding lab data against the convenience of Tier 1.")
    D.title(s, "What lab data adds")
    D.image(s, figs["tiers"], 0.6, 1.5, 7.6, 5.2)
    D.card(s, 8.6, 1.7, 4.1, 4.4, "Reading the chart", n["tier_sentence"] + " Tier 1 still gives a useful first signal when no reports are available.", bsize=15)

    # 12-13 ROC, confusion
    s = D.slide(notes="ROC curves show the trade-off between catching cases and false alarms.")
    D.title(s, "ROC curves"); D.image(s, figs["roc1"], 0.6, 1.5, 6.0, 5.3); D.image(s, figs["roc2"], 6.8, 1.5, 6.0, 5.3)
    s = D.slide(notes="Read the false negatives first: those are the missed cases.")
    D.title(s, "Confusion matrices (deployed XGBoost)")
    D.image(s, figs["confusion1"], 0.6, 1.5, 6.0, 5.2); D.image(s, figs["confusion2"], 6.8, 1.5, 6.0, 5.2)

    # 14 Explainability
    s = D.slide(notes="Compare top factors with clinical knowledge: irregular cycle, follicles, AMH, hair growth, BMI.")
    D.title(s, "Why the model says what it says")
    D.image(s, figs["importance"], 0.6, 1.5, 8.3, 4.6)
    D.card(s, 9.2, 1.7, 3.5, 4.4, "Top factors", f"Tier 1: {', '.join(n['top1'])}.  Tier 2: {', '.join(n['top2'])}.", bsize=15)

    # 15 Demo
    s = D.slide(notes="Switch to the live app here. Show a low and a high profile, then download the PDF.")
    D.title(s, "The working application")
    D.image(s, figs.get("app"), 0.6, 1.4, 5.6, 5.6)
    table(D, s, ["Example input", "Risk", "Band"], [[r[0].split(": ")[1], r[1], r[2]] for r in sample_predictions()],
          6.6, 1.9, 6.1, [3.6, 1.1, 1.4], size=14, rowh=0.62)
    D.text(s, "Live risk dial, factor bars, English and Hindi, PDF report. Nothing the user types is stored.", 6.6, 4.5, 6.1, 1.2, 16, MUTED)

    # 16 Ethics & limits
    s = D.slide(notes="Be upfront: it is a screening aid, not a diagnosis. Mention the dataset limits.")
    D.title(s, "Ethics and limitations")
    D.card(s, 0.6, 1.9, 5.9, 3.3, "Ethics", ["Screening aid, never a diagnosis.", "No personal data stored.", "Advice tells users with irregular periods to see a doctor even at low risk."][0] + " No personal data is stored. Advice tells users with irregular periods to see a doctor even when the score is low.", bsize=20)
    D.card(s, 6.8, 1.9, 5.9, 3.3, "Limitations", "Small single-region dataset. Self-reported symptoms in Tier 1. No clinical trial. Survey group has no confirmed diagnosis.", fill="FBE6EA", hc=ROSE, bsize=20)

    # 17 Conclusion
    s = D.slide(notes="Close with what was built and where it can go next.")
    D.title(s, "Conclusion and future scope")
    D.card(s, 0.6, 1.9, 5.9, 3.3, "What we built", "A two-tier, explainable PCOS screening system with a web interface, risk bands, factor explanations and a PDF report.", fill="DDEFEA", hc=TEAL, bsize=20)
    D.card(s, 6.8, 1.9, 5.9, 3.3, "Next steps", "Multi-centre data and clinician validation. Ultrasound image analysis. Mobile app with more languages. Wearable cycle tracking.", bsize=20)

    # 18 Thanks
    s = D.slide(DEEP, "Invite questions. Keep the app open for a live demo.")
    D.text(s, "Thank you", 0.8, 2.6, 11.7, 1.2, 60, WHITE, True, HEAD)
    D.text(s, "Questions?", 0.8, 3.95, 11.7, 0.8, 28, "D9CCF0", False, HEAD)

    out.parent.mkdir(parents=True, exist_ok=True); D.p.save(out); return out
