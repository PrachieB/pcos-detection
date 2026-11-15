"""Builds the final-year project report (.docx) from the real training outputs."""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from tools.summary import narrative, sample_predictions

PLUM = RGBColor(0x4B, 0x2E, 0x83)
RED = RGBColor(0xB3, 0x30, 0x4A)
TITLE = "Advancing Precision Women's Healthcare: A Data-Driven Approach to PCOS Risk Prediction"


def _field(run, code):
    for t, txt in (("begin", None), (None, code), ("end", None)):
        if t:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), t)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = txt
        run._r.append(el)


class Report:
    def __init__(self, demo: bool):
        self.d, self.demo, self.fig_n, self.tab_n, self.ch = Document(), demo, 0, 0, 0
        st = self.d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        st.paragraph_format.line_spacing = 1.5; st.paragraph_format.space_after = Pt(6)
        for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 12)):
            h = self.d.styles[name]; h.font.name = "Times New Roman"; h.font.size = Pt(size); h.font.bold = True
            h.font.color.rgb = PLUM if name != "Heading 3" else RGBColor(0x23, 0x1F, 0x2E)
            h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        s = self.d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(3), Cm(2.5), Cm(2.5), Cm(2.5)
        if demo:
            p = s.header.paragraphs[0]; r = p.add_run("DEMO DATA: results are from synthetic data. Re-run training on the Kaggle dataset and rebuild.")
            r.font.size = Pt(9); r.font.color.rgb = RED; r.bold = True; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER; _field(fp.add_run(), "PAGE")

    # --- primitives ---
    def p(self, text, bold=False, italic=False, align=None, size=None, color=None, after=None):
        para = self.d.add_paragraph(); r = para.add_run(text); r.bold, r.italic = bold, italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        if align == "c": para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == "j": para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if after is not None: para.paragraph_format.space_after = Pt(after)
        return para

    def body(self, text): return self.p(text, align="j")

    def bullets(self, items, style="List Bullet"):
        for i, it in enumerate(items, 1):
            if style == "List Number":
                para = self.d.add_paragraph()
                para.paragraph_format.left_indent = Cm(0.9); para.paragraph_format.first_line_indent = Cm(-0.9)
                para.add_run(f"{i}.\t")
                para.paragraph_format.tab_stops.add_tab_stop(Cm(0.9))
            else:
                para = self.d.add_paragraph(style=style)
            para.paragraph_format.line_spacing = 1.3
            if isinstance(it, tuple):
                para.add_run(it[0]).bold = True; para.add_run(it[1])
            else:
                para.add_run(it)

    def chapter(self, title):
        self.ch += 1; self.fig_n = 0; self.tab_n = 0
        self.d.add_page_break(); self.d.add_heading(f"{self.ch}. {title}", 1)

    def h2(self, t): self.d.add_heading(t, 2)

    def figure(self, path, caption, width=14.5):
        if not path or not Path(path).exists(): return
        self.fig_n += 1
        para = self.d.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.keep_with_next = True; para.add_run().add_picture(str(path), width=Cm(width))
        c = self.p(f"Figure {self.ch}.{self.fig_n}: {caption}", italic=True, align="c", size=11)

    def table(self, header, rows, caption, widths=None):
        self.tab_n += 1
        cap = self.p(f"Table {self.ch}.{self.tab_n}: {caption}", italic=True, align="c", size=11)
        cap.paragraph_format.keep_with_next = True
        t = self.d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(header):
            c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(255, 255, 255)
            sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "4B2E83"); c._tc.get_or_add_tcPr().append(sh)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(10.5)
        for row in t.rows:
            for c in row.cells:
                for pp in c.paragraphs: pp.paragraph_format.line_spacing = 1.1; pp.paragraph_format.space_after = Pt(2)
        t.autofit = False
        widths = widths or [16.0 / len(header)] * len(header)
        scale = 16.0 / sum(widths)
        for col, w in zip(t.columns, widths): col.width = Cm(w * scale)
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Cm(w * scale)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)

    def code(self, text):
        for line in text.strip("\n").split("\n"):
            para = self.d.add_paragraph(); para.paragraph_format.line_spacing = 1.0; para.paragraph_format.space_after = Pt(0)
            r = para.add_run(line or " "); r.font.name = "Courier New"; r.font.size = Pt(9)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")


def comp_rows(comp):
    return [[c["model"], f"{c['cv_recall']:.3f}", f"{c['accuracy']:.3f}", f"{c['precision']:.3f}",
             f"{c['recall']:.3f}", f"{c['f1']:.3f}", f"{c['roc_auc']:.3f}"] for c in comp]


def build(figs, meta, source, imp, out: Path):
    n = narrative(meta, imp); demo = source != "real"
    R = Report(demo); d = R.d
    COMP_H = ["Model", "CV recall", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]

    # ---- Title page ----
    for _ in range(3): R.p("")
    R.p(TITLE, bold=True, align="c", size=20, color=PLUM)
    R.p("A Two-Tier Explainable Machine Learning Screening System", align="c", size=14, italic=True)
    R.p("")
    R.p("A Project Report submitted in partial fulfilment of the requirements for the degree of", align="c")
    R.p("Bachelor of Technology / Bachelor of Engineering", bold=True, align="c", after=18)
    R.p("Submitted by", align="c"); R.p("[Student Name]   [Roll No.]", bold=True, align="c", after=14)
    R.p("Under the guidance of", align="c"); R.p("[Guide Name], [Designation]", bold=True, align="c", after=14)
    R.p("Department of [Department Name]", bold=True, align="c"); R.p("[College Name], [University]", align="c")
    R.p("Academic Year 2026-27", align="c")
    if demo:
        R.p("")
        R.p("This copy was generated from SYNTHETIC DEMO data. Retrain on the Kaggle dataset and rebuild before submission.",
            bold=True, align="c", size=10.5, color=RED)

    # ---- Front matter ----
    d.add_page_break(); d.add_heading("Certificate", 1)
    R.body(f"This is to certify that the project report titled \"{TITLE}\" is a bonafide record of work carried out by "
           "[Student Name], Roll No. [Roll No.], under my supervision, in partial fulfilment of the requirements for the award "
           "of the degree of [Degree] at [College Name].")
    R.p(""); R.p("Project Guide: ____________________          Head of Department: ____________________")
    R.p("Date: ____________          External Examiner: ____________________")
    d.add_heading("Declaration", 1)
    R.body("I declare that this report is my own work, that all sources used are acknowledged, and that it has not been submitted "
           "elsewhere for any degree or diploma.")
    R.p("[Student Name]                                  Date: ____________")
    d.add_heading("Acknowledgement", 1)
    R.body("I thank my guide [Guide Name] for guidance throughout this project, the department for the facilities provided, and the "
           "students who volunteered in the usability survey. I am grateful to my family and friends for their support.")

    d.add_page_break(); d.add_heading("Abstract", 1)
    R.body("Polycystic Ovary Syndrome (PCOS) is a common endocrine disorder in women of reproductive age. It is often diagnosed late "
           "because confirmation needs ultrasound and hormone tests that many women cannot easily access. This project builds a "
           "two-tier machine learning screening system. Tier 1 estimates PCOS risk from easily collected information only (age, BMI, "
           "cycle regularity, common symptoms and lifestyle) and needs no laboratory test. Tier 2 adds follicle counts, AMH and the "
           "FSH/LH ratio for clinic settings.")
    R.body(f"Four classifiers (Logistic Regression, Random Forest, XGBoost and SVM) were compared using stratified 5-fold cross-validation "
           f"on {n['n_rows']} records, with recall as the primary metric because a missed case costs more than a false alarm in screening. "
           f"{n['tier_sentence']} Each prediction is explained with per-patient factor contributions. The system is deployed as a "
           "FastAPI web application with an English and Hindi interface and a downloadable PDF report. It is a screening aid, not a diagnostic device.")
    R.p("Keywords: PCOS, machine learning, XGBoost, explainable AI, SHAP, screening, women's health", italic=True)

    d.add_page_break(); d.add_heading("Table of Contents", 1)
    para = d.add_paragraph(); _field(para.add_run(), 'TOC \\o "1-2" \\h \\z \\u')
    R.p("(In Word: right-click this area and choose Update Field, then Update entire table.)", italic=True, size=10)

    # ---- 1 Introduction ----
    R.chapter("Introduction")
    R.h2("1.1 Background")
    R.body("PCOS is a hormonal condition marked by irregular or absent ovulation, excess androgen (causing acne, unwanted hair growth "
           "and hair loss) and often polycystic-appearing ovaries. It is strongly linked to insulin resistance and weight gain, and over "
           "time raises the risk of infertility, type 2 diabetes, heart disease and mental health problems. Reported prevalence is about "
           "1 in 10 women worldwide, and Indian studies report higher and widely varying figures depending on the population and criteria used.")
    R.h2("1.2 Motivation")
    R.body("Diagnosis follows the Rotterdam criteria, which need two of three features: oligo or anovulation, clinical or biochemical "
           "hyperandrogenism, and polycystic ovaries on ultrasound. Many women, especially outside cities, cannot easily reach a gynaecologist, "
           "an ultrasound or a hormone assay, so diagnosis is delayed. A low-cost first-level screening tool can help decide who should be "
           "sent for confirmatory tests.")
    R.h2("1.3 Scope")
    R.body("The system estimates risk and suggests a next step. It does not diagnose PCOS and does not replace a doctor.")
    R.h2("1.4 Report organisation")
    R.body("Chapter 2 reviews related work. Chapter 3 states the problem and objectives. Chapters 4 to 6 describe the data, method and system design. "
           "Chapter 7 covers implementation, Chapter 8 the results, Chapter 9 the usability survey, and Chapters 10 to 12 ethics, limitations and conclusion.")

    # ---- 2 Literature ----
    R.chapter("Literature Review")
    R.body("Add 6 to 8 recent papers here after searching Google Scholar and IEEE Xplore (search: \"PCOS prediction machine learning\", "
           "\"PCOS ultrasound deep learning\", \"explainable AI PCOS\"). The themes below structure the review.")
    R.table(["Theme", "What prior work does", "Gap this project addresses"], [
        ["Clinical-feature ML models", "Train classifiers on hospital clinical and hormonal data", "Most need lab data, limiting use in low-resource settings"],
        ["Image-based detection", "CNNs on ultrasound images to detect polycystic ovaries", "Needs imaging equipment and expert-labelled images"],
        ["Feature selection studies", "Identify cycle regularity, follicle count, AMH and BMI as strong predictors", "Often stop at accuracy and do not become a usable tool"],
        ["Explainability", "Some work uses SHAP or LIME", "Rarely turned into patient-facing output"]],
        "Themes in the PCOS machine learning literature", widths=[3.6, 6, 6])
    R.body("Reference points used in this work are the Rotterdam consensus criteria (2003), the international evidence-based PCOS guideline "
           "(Teede et al., 2018), SMOTE (Chawla et al., 2002), XGBoost (Chen and Guestrin, 2016) and SHAP (Lundberg and Lee, 2017). "
           "The research gap is that few studies offer a tier that works without laboratory tests, per-patient explanations and a deployed tool together.")

    # ---- 3 Problem ----
    R.chapter("Problem Statement and Objectives")
    R.body("Confirming PCOS needs tests that many women cannot readily access, which delays diagnosis. There is a need for an accessible, "
           "explainable risk-screening tool that works with or without laboratory data.")
    R.bullets(["Build and compare machine learning models for PCOS risk prediction.",
               "Build a Tier 1 model using only non-invasive, easily available inputs.",
               "Build a Tier 2 model using ultrasound and hormone data for higher accuracy.",
               "Explain each prediction by showing the factors that raised or lowered the risk.",
               "Deploy a web application that gives risk, reasons and next-step advice.",
               "Check usability and risk distribution with a small student survey."], "List Number")

    # ---- 4 Dataset ----
    R.chapter("Dataset Description")
    src = ("Polycystic Ovary Syndrome (PCOS) dataset by Prasoon Kottarathil on Kaggle, collected from 10 hospitals in Kerala, India."
           if not demo else "SYNTHETIC demo data generated by ml/data.py. Replace with the Kaggle dataset by Prasoon Kottarathil (541 records, 10 hospitals in Kerala) before submission.")
    R.body(f"Source: {src} The data used for this report has {n['n_rows']} records, of which {n['pos_rate']:.0f}% are PCOS-positive. "
           f"{n['n_train']} records were used for training and {n['n_test']} for testing (stratified 80/20 split).")
    R.table(["Tier", "Features", "Needs lab test?"], [
        ["Tier 1", "Age, BMI, cycle regularity, weight gain, hair growth, skin darkening, hair loss, pimples, fast food, regular exercise", "No"],
        ["Tier 2", "All Tier 1 features plus follicle count (left and right), AMH, FSH/LH ratio", "Yes"]],
        "Feature sets used by the two tiers", widths=[2.2, 11, 3])
    R.figure(figs["class"], "Class distribution of the dataset", 9)
    R.figure(figs["box"], "BMI, AMH and total follicle count by PCOS status", 15)
    R.figure(figs["corr"], "Correlation matrix of the features and the target", 12.5)
    R.body("Data-quality notes: the dataset is small, comes from one region and is moderately imbalanced. These limit how far results generalise.")

    # ---- 5 Methodology ----
    R.chapter("Methodology")
    R.figure(figs["pipeline"], "Methodology pipeline", 15.5)
    R.h2("5.1 Preprocessing")
    R.bullets(["Column names are cleaned and renamed; all values are converted to numbers.",
               "Missing values are filled with the median inside the pipeline, fitted on training data only.",
               "Features are standardised with StandardScaler.",
               "Class imbalance is handled with class weights (scale_pos_weight for XGBoost), not by modifying the test set."])
    R.h2("5.2 Models compared")
    R.table(["Model", "Reason for inclusion"], [
        ["Logistic Regression", "Interpretable baseline"], ["Random Forest", "Robust, handles non-linearity"],
        ["XGBoost", "Strong on small tabular data, supports exact per-patient contributions"], ["SVM (RBF)", "Strong margin-based classifier"]],
        "Candidate models", widths=[4, 12])
    R.h2("5.3 Evaluation protocol")
    R.body("An 80/20 stratified hold-out split is used, with stratified 5-fold cross-validation on the training portion. Metrics are accuracy, "
           "precision, recall, F1, ROC-AUC and the confusion matrix. Recall is the primary metric because in screening a missed case is worse "
           "than an unnecessary follow-up. A probability threshold of 0.40 is used for the positive class to favour recall.")
    R.h2("5.4 Explainability")
    R.body("For each prediction the XGBoost model returns the contribution of every feature in log-odds (SHAP-style values). The top factors "
           "are shown to the user as factors that raise or lower the risk. A global SHAP summary plot is produced during training.")

    # ---- 6 System design ----
    R.chapter("System Design and Architecture")
    R.figure(figs["architecture"], "System architecture: online screening flow and offline training flow", 15.5)
    R.body("Risk bands: below 40% is low, 40 to 70% is moderate (suggest ultrasound and hormone tests) and above 70% is high (suggest consulting a gynaecologist). "
           "Thresholds are set in app/features.py.")
    R.table(["Requirement", "Description"], [
        ["Functional", "Accept inputs, validate ranges, choose tier, show risk, factors and advice, produce PDF report, English and Hindi interface"],
        ["Non-functional", "Responds in well under two seconds, runs on a basic laptop, stores no personal data, no login needed"],
        ["Technology", "Python, pandas, scikit-learn, XGBoost, SHAP, FastAPI, pydantic, ReportLab, HTML/CSS/JavaScript"]],
        "System requirements and technology", widths=[3.5, 12.5])
    R.table(["Endpoint", "Purpose"], [
        ["POST /api/predict", "Returns risk, band, top factors and advice for a tier 1 or tier 2 input"],
        ["POST /api/report", "Returns the same result as a PDF report"],
        ["GET /api/meta", "Returns model information and metrics"], ["GET /api/health", "Health check"]],
        "REST API endpoints", widths=[4.5, 11.5])

    # ---- 7 Implementation ----
    R.chapter("Implementation")
    R.body("The project has three parts: the ML pipeline (ml/), the FastAPI backend (app/) and the browser frontend (frontend/). "
           "Training is run with python -m ml.train, and the application with python -m uvicorn app.main:app.")
    R.table(["Folder or file", "Role"], [
        ["ml/data.py", "Loads the Kaggle dataset and maps columns to clean names"],
        ["ml/train.py", "Compares models, evaluates, saves plots and the deployed pipelines"],
        ["app/main.py", "FastAPI application and static file serving"],
        ["app/predictor.py", "Loads models, predicts, computes factor contributions, chooses band and advice"],
        ["app/report.py", "Builds the PDF report"],
        ["frontend/", "Single-page interface with live risk dial, factor bars and language switch"]],
        "Project structure", widths=[4.5, 11.5])
    R.p("Core of the training routine (ml/train.py):", bold=True)
    R.code('''pipe = Pipeline([("imp", SimpleImputer(strategy="median")),
                 ("sc", StandardScaler()), ("clf", XGBClassifier(...))])
cv_recall = cross_val_score(pipe, Xtr, ytr, cv=StratifiedKFold(5), scoring="recall").mean()
pipe.fit(Xtr, ytr)
proba = pipe.predict_proba(Xte)[:, 1]
pred = (proba >= 0.40).astype(int)      # threshold chosen to favour recall''')
    R.figure(figs.get("app"), "Screening interface showing the risk dial, advice and contributing factors", 14)

    # ---- 8 Results ----
    R.chapter("Results and Discussion")
    if demo:
        R.p("Note: these numbers come from synthetic demo data and only show the layout. They are replaced automatically when the report is rebuilt after training on the real dataset.",
            bold=True, color=RED, size=11)
    R.h2("8.1 Tier 1 results (no laboratory tests)")
    R.table(COMP_H, comp_rows(meta["tiers"]["1"]["comparison"]), "Tier 1 model comparison on the held-out test set", widths=[4, 2, 2, 2, 2, 1.6, 2])
    R.figure(figs["cmp1"], "Tier 1 metrics for all four models", 14)
    R.body(n["best1_sentence"])
    R.figure(figs["roc1"], "Tier 1 ROC curves", 10.5)
    R.figure(figs["confusion1"], "Tier 1 confusion matrix of the deployed XGBoost model", 8.5)
    R.h2("8.2 Tier 2 results (with ultrasound and hormone values)")
    R.table(COMP_H, comp_rows(meta["tiers"]["2"]["comparison"]), "Tier 2 model comparison on the held-out test set", widths=[4, 2, 2, 2, 2, 1.6, 2])
    R.figure(figs["cmp2"], "Tier 2 metrics for all four models", 14)
    R.body(n["best2_sentence"])
    R.figure(figs["roc2"], "Tier 2 ROC curves", 10.5)
    R.figure(figs["confusion2"], "Tier 2 confusion matrix of the deployed XGBoost model", 8.5)
    R.h2("8.3 Tier 1 compared with Tier 2")
    R.figure(figs["tiers"], "Deployed XGBoost metrics for the two tiers", 12)
    R.body(n["tier_sentence"] + " " + n["deploy_sentence"])
    R.h2("8.4 Explainability")
    R.figure(figs["importance"], "Mean absolute factor contribution for each tier", 15)
    R.body(n["top1_sentence"] + " " + n["top2_sentence"] + " Compare these with clinical knowledge in your viva: irregular cycles, "
           "raised follicle count and AMH, excess hair growth and weight are widely reported as associated with PCOS.")
    R.figure(figs["shap1"], "SHAP summary plot, Tier 1", 12)
    R.figure(figs["shap2"], "SHAP summary plot, Tier 2", 12)
    R.h2("8.5 Example predictions from the deployed system")
    R.table(["Example input", "Risk", "Band", "Strongest factor"], [list(r) for r in sample_predictions()],
            "Tier 1 predictions for three example profiles", widths=[7.2, 2, 2.3, 4.5])
    R.h2("8.6 Discussion")
    R.bullets(["Recall is the headline metric: a screening tool should miss as few true cases as possible.",
               "Tier 2 is expected to do better than Tier 1 because follicle count and AMH measure the condition more directly.",
               "Tier 1 still gives a useful first-level signal from symptoms alone, which suits settings with no lab access.",
               "False negatives deserve attention: advice for low-risk results still tells users with irregular periods to see a doctor."])

    # ---- 9 Survey ----
    R.chapter("Real-World Usability Survey")
    R.body("A short anonymous form was designed for 50 to 100 consenting adult students. It collects only the Tier 1 inputs plus two feedback "
           "questions: ease of use (1 to 5) and whether the user would consult a doctor based on the advice.")
    R.table(["Item", "Result"], [["Participants", "[fill in]"], ["Low / moderate / high risk band", "[fill in]"],
                                 ["Average ease-of-use score (1 to 5)", "[fill in]"], ["Would consult a doctor if advised", "[fill in]%"]],
            "Survey summary (complete after collecting responses)", widths=[9, 6])
    R.body("Survey respondents have no confirmed diagnosis, so this is a usability and distribution check, not accuracy validation. Consent was "
           "obtained and no names or contact details were collected.")

    # ---- 10-12 ----
    R.chapter("Ethical Considerations")
    R.bullets([("Not a diagnostic device. ", "A disclaimer appears on every result and in the PDF."),
               ("Privacy. ", "Inputs are processed in memory and not stored; the survey is anonymous."),
               ("Bias. ", "Training data comes from one region and from patients already visiting hospitals, so results may not generalise."),
               ("Harm from errors. ", "A false negative can reassure wrongly; a false positive can cause anxiety. Advice wording encourages a doctor visit in both cases."),
               ("Transparency. ", "Factor contributions show why a result was produced.")])
    R.chapter("Limitations")
    R.bullets(["Small dataset from a single region.", "Labels depend on the hospitals' diagnoses and may be inconsistent.",
               "Tier 1 relies on self-reported symptoms, which can be inaccurate.", "The survey group has no ground-truth diagnosis.",
               "No prospective clinical trial or regulatory approval."], "List Number")
    R.chapter("Conclusion and Future Scope")
    R.body("This project built a two-tier, explainable PCOS risk-screening system that works with or without laboratory data and is deployed as a "
           "web application. By pairing predictions with factor explanations and clear next-step advice, it moves beyond a model-on-a-dataset "
           "exercise toward a usable screening aid.")
    R.p("Future scope:", bold=True)
    R.bullets(["Train on larger multi-centre and multi-region datasets and validate externally with clinicians.",
               "Add ultrasound image analysis with CNNs.", "Build a mobile app with more regional languages.",
               "Link with wearables for cycle and sleep tracking.", "Run a clinical pilot with a gynaecologist."])

    # ---- References ----
    d.add_page_break(); d.add_heading("References", 1)
    refs = ["Kottarathil, P. Polycystic Ovary Syndrome (PCOS) dataset. Kaggle.",
            "Rotterdam ESHRE/ASRM-Sponsored PCOS Consensus Workshop Group (2004). Revised 2003 consensus on diagnostic criteria and long-term health risks related to PCOS. Fertility and Sterility.",
            "Teede, H. J., et al. (2018). Recommendations from the international evidence-based guideline for the assessment and management of PCOS.",
            "Chawla, N. V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. Journal of Artificial Intelligence Research.",
            "Chen, T., and Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD.",
            "Lundberg, S. M., and Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS.",
            "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR.",
            "[Add 6 to 8 recent PCOS and machine learning papers from your literature search.]"]
    R.bullets(refs, "List Number")

    out.parent.mkdir(parents=True, exist_ok=True); d.save(out)
    return out
