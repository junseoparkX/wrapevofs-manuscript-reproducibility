"""Build submission-facing Nature reporting documents and cover letter."""

from __future__ import annotations

from pathlib import Path
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas as pdf_canvas


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = ROOT / "documentation" / "submission"
TMP = REPO / "tmp" / "nature_forms"
TITLE = "WrapEvoFS enables auditable feature compression with regret-constrained representative locking"
DATE = "19 August 2026"
PACKAGE_URL = "https://github.com/junseoparkX/wrapevofs-package"
REPRO_URL = "https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility"


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.2,
    leading=12.4,
    spaceAfter=5,
    textColor=colors.HexColor("#20272E"),
    alignment=TA_LEFT,
)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=8.1, leading=10.5)
TITLE_STYLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=21,
    textColor=colors.black,
    spaceAfter=8,
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=14,
    spaceBefore=8,
    spaceAfter=5,
)
LABEL = ParagraphStyle(
    "Label", parent=SMALL, fontName="Helvetica-Bold", textColor=colors.HexColor("#3D4B55")
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D3D8DC"))
    canvas.line(20 * mm, 14 * mm, 190 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#5E6972"))
    canvas.drawString(20 * mm, 9 * mm, "WrapEvoFS submission materials")
    canvas.drawRightString(190 * mm, 9 * mm, str(doc.page))
    canvas.restoreState()


def doc(path: Path, title: str):
    return SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Junseo Park and Huan Zhong",
    )


def header(story, title: str, subtitle: str):
    story.append(Paragraph(title, TITLE_STYLE))
    story.append(Paragraph(subtitle, BODY))
    story.append(Spacer(1, 4 * mm))


def response_table(rows, widths=(48 * mm, 122 * mm)):
    data = [[Paragraph(str(a), LABEL), Paragraph(str(b), SMALL)] for a, b in rows]
    table = Table(data, colWidths=list(widths), hAlign="LEFT", repeatRows=0)
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9DEE2")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F5F6")),
            ]
        )
    )
    return table


def build_bio_summary():
    path = OUT / "Bio_and_Life_Sciences_Reporting_Summary.pdf"
    story = []
    header(
        story,
        "Bio and Life Sciences Reporting Summary",
        f"Corresponding author: Huan Zhong &nbsp;&nbsp;|&nbsp;&nbsp; Last updated: {DATE}<br/>{TITLE}",
    )
    story.append(Paragraph("Statistics", SUBTITLE))
    story.append(
        response_table(
            [
                ("Sample sizes", "Confirmed. Exact cohort, partition, branch, and condition sizes are reported in Table 1, Methods, figure legends, and Supplementary Tables."),
                ("Distinct or repeated measurements", "Confirmed. Repeated outer-CV predictions, common bootstrap resamples, paired feature-space analyses, and five-seed candidate banks are identified explicitly."),
                ("Statistical procedures", "Confirmed. Metrics, resampling units, bootstrap stratification, seeds, confidence intervals, and descriptive dependent-fold summaries are specified in Methods and legends."),
                ("Covariates", "Confirmed. No clinical covariates were added to the predictive feature matrices. Cohort composition and omitted scanner/site covariates are reported where relevant."),
                ("Assumptions and multiplicity", "Confirmed. The manuscript distinguishes descriptive comparisons, unadjusted exploratory analyses, and tests for which equivalence or non-inferiority was not assessed."),
                ("Summary and uncertainty", "Confirmed. Means, medians, ranges, standard deviations, confidence intervals, and credible intervals are identified with their resampling or posterior basis."),
                ("Null-hypothesis testing", "The primary empirical analyses emphasize estimates and confidence intervals; no primary claim depends on a null-hypothesis P value."),
                ("Bayesian analysis", "Priors, sampling settings, chain diagnostics, credible intervals, R-hat, and effective sample sizes are reported for the secondary Bayesian analyses."),
                ("Hierarchical or complex designs", "Participant-clustered resampling retains repeat-specific predictions, leave-one-center-out analyses preserve centers, and overlapping outer folds are summarized descriptively."),
                ("Effect estimates", "Paired AUROC differences, empirical regret, feature counts, compression, and Jaccard agreement are reported with definitions and uncertainty where applicable."),
            ]
        )
    )
    story.append(Paragraph("Software, code, and data", SUBTITLE))
    story.append(
        response_table(
            [
                ("Data collection", "Secondary analyses used provider-supplied ADNI, AMP-AD, CGGA, and TCGA matrices. The VGH cohort used de-identified clinical DICOM data processed with dcm2niix, RaidionicsRADS, RaidionicsSeg, and PyRadiomics; versions and settings are reported."),
                ("Data analysis", f"WrapEvoFS v0.2.0, Python 3.10–3.12, scikit-learn, XGBoost, BorutaPy, and documented cohort-specific dependencies were used. Package: {PACKAGE_URL}. Reproducibility materials: {REPRO_URL}."),
                ("Data availability", "Participant-level data are not redistributed. ADNI, AMP-AD, CGGA, and TCGA access routes and identifiers are given in the Data availability statement. The provider-organized TCGA workbook is not redistributed. VGH participant-level data remain restricted; non-identifying aggregate and audit materials are public."),
            ]
        )
    )
    story.append(Paragraph("Research involving human participants or human data", SUBTITLE))
    story.append(
        response_table(
            [
                ("Sex and gender", "The study did not test sex- or gender-specific effects and makes no sex- or gender-specific inference. Available cohort composition is reported in source publications and cohort tables."),
                ("Race and ethnicity", "The AMP-AD source was designed as a diverse-cohort resource, but race and ethnicity were not used as predictive labels or proxies in this methodological study. Center-specific heterogeneity is reported without attributing it to race or ethnicity."),
                ("Population characteristics", "The five analyses cover ADNI-derived diagnostic classes, AMP-AD post-mortem multi-omics cohorts, CGGA MGMT methylation, TCGA histological classes, and a VGH MGMT radiomics cohort. Exact counts and outcome compositions are reported in Table 1."),
                ("Recruitment", "No participants were newly recruited. Recruitment, consent, and source-study inclusion followed the originating cohort protocols; the present work is a secondary methodological analysis."),
                ("Ethics oversight", "ADNI used participating-site IRB/REB approval and written consent. CGGA reports Beijing Tiantan Hospital approval KY2013-017-01 and written consent. AMP-AD source institutions reported IRB approval and participant or next-of-kin consent. TCGA followed NCI/NHGRI human-subject protection and informed-consent policies. VGH data were analyzed under UBC REB H20-02354; consent was waived for the retrospective study and secondary analysis was permitted."),
            ]
        )
    )
    story.append(Paragraph("Life sciences study design", SUBTITLE))
    story.append(
        response_table(
            [
                ("Sample-size determination", "No prospective power calculation was used. Sample sizes were fixed by available eligible participants, validated source linkage, and prespecified cohort boundaries. The primary TCGA analysis used all 491 supplied eligible participants in repeated outer CV."),
                ("Data exclusions", "Exclusions were prespecified and based on source availability, participant matching, finite-value or geometry checks, and validated outcome linkage. VGH flow and all exclusions are reported in Methods and Supplementary Table S28."),
                ("Replication", "Algorithmic replication used five GA seeds, repeated outer CV, development-only audits, one-time post-freeze center evaluation, and synthetic candidate-bank simulation. These are not presented as independent biological replication."),
                ("Randomization", "No intervention allocation occurred. Stratified splits, CV folds, bootstrap resamples, genetic operators, and model seeds were prespecified and recorded."),
                ("Blinding", "Held-out outcomes were blocked from Direct selection, RFECV, GA, rescoring, and locking. Feature masks, parameters, and protocol hashes were frozen before the one-time post-freeze evaluations."),
            ]
        )
    )
    doc(path, "Bio and Life Sciences Reporting Summary").build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def build_code_checklist():
    path = OUT / "Code_and_Software_Submission_Checklist.pdf"
    story = []
    header(
        story,
        "Code and Software Submission Checklist",
        f"Corresponding author: Huan Zhong<br/>{TITLE}",
    )
    story.append(Paragraph("Required content", SUBTITLE))
    story.append(
        response_table(
            [
                ("Source code", f"Provided. The installable package and versioned release are public at {PACKAGE_URL}; manuscript analysis code and aggregate source data are public at {REPRO_URL}."),
                ("Demonstration data", "Provided. The package includes synthetic, nonbiomedical examples and a toy regret-locking workflow that require no restricted data."),
                ("System requirements", "Provided in README and pyproject metadata, including Python 3.10–3.12, dependencies, optional selector extras, and CPU execution."),
                ("Tested versions", "Provided. Continuous integration tests Python 3.10, 3.11, and 3.12; the release includes build and clean-install validation."),
                ("Non-standard hardware", "Not required for installation, API/CLI use, property tests, or reviewer examples. Archived GPU analyses are identified separately in the computational audit."),
                ("Installation guide", "Provided. PyPI installation: pip install wrapevofs==0.2.0. Source and development installation are documented in the package README."),
                ("Demo instructions, outputs, and runtime", "Provided in the package examples and README. Expected audit artifacts and schema validation are documented."),
                ("Instructions for use", "Provided for the Python API, command-line interface, configuration files, checkpoint/resume, deterministic locking, and artifact validation."),
                ("Reproduction instructions", "Provided in REPRODUCIBILITY.md, the manuscript source README, figure-source manifest, source-data workbook, and analysis-specific provenance records."),
            ]
        )
    )
    story.append(Paragraph("Additional information", SUBTITLE))
    story.append(
        response_table(
            [
                ("License", "WrapEvoFS v0.2.0 is distributed under the OSI-approved BSD 3-Clause License."),
                ("Open repository", PACKAGE_URL),
                ("Immutable version", "GitHub release and tag v0.2.0; the same version is available from PyPI."),
                ("Functionality description", "The main Methods define the objective, candidate rescoring, regret-constrained eligible pool, Jaccard medoid, deterministic tie-breaking, and evaluation boundaries. Supplementary Algorithm 1, formal propositions, complexity analysis, and implementation correspondence provide executable detail."),
                ("Restricted data boundary", "No participant-level ADNI, AMP-AD, CGGA, TCGA provider workbook, or VGH DICOM-derived records are included in the software repository. Reviewer examples are synthetic."),
            ]
        )
    )
    doc(path, "Code and Software Submission Checklist").build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def radio_value(fields, name: str, choice: str) -> str:
    field = fields[name]
    suffix = f"_{choice}_On"
    for kid in field.get("/Kids", []):
        for key in kid.get_object()["/AP"]["/N"].keys():
            value = str(key)
            if value.endswith(suffix):
                return value[1:]
    raise KeyError((name, choice))


def build_ml_checklist():
    source = TMP / "machine-learning-checklist.pdf"
    path = OUT / "Machine_Learning_Checklist.pdf"
    intermediate = OUT / ".Machine_Learning_Checklist_fields.pdf"
    reader = PdfReader(str(source))
    fields = reader.get_fields()
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    values = {
        "Corresponding authors": "Huan Zhong",
        "The source code is included in the submission or a": "/On",
        "Textfield": PACKAGE_URL,
        "A test dataset and instructionsscripts for replica": "/On",
        "Textfield-1": PACKAGE_URL + "/tree/main/examples",
        "A Readme file with instructions for installing and": "/On",
        "Textfield-2": PACKAGE_URL,
        "The code is made available to reviewers during rev": "/On",
        "Pretrained models are used in the study and access": "/On",
        "Textfield-3": "Raidionics software/models; supervised classifiers were fitted within study folds",
        "The paper contains information on how to obtain co": "/On",
        "A What model architecture is the current model bas": "Staged feature selection (SVM-L1, XGBoost, or Boruta-RF), RFECV, five genetic searches, regret-constrained medoid locking, and a fixed random-forest evaluator.",
        "Yes": "Discussion and Methods: empirical datasets and analysis boundary",
        "Yes-0": "Methods; Supplementary Methods; Supplementary Tables S26-S28",
        "Yes-1": "Methods: empirical datasets and analysis boundary",
        "Yes-2": "Methods: fully nested TCGA and cohort-specific designs",
        "No-3": "Internal and center-shift evaluations are not claimed to reproduce clinical deployment.",
        "Yes-4": "Methods and Figure 1 leakage boundary",
        "No-5": "Feature identities are descriptive and are not validated as biological biomarkers.",
        "Yes-6": "Methods: metrics and resampling; figure and table legends",
        "Yes-7": "TCGA, ADNI, AMP-AD, and CGGA source cohorts",
        "Yes-8": "RFECV-only, highest-score, medoid, Elastic Net, stability, and random-bank controls",
        "Yes-9": "Elastic Net, stability selection, RFECV, and random-bank comparisons",
        "Yes-10": "Objective, locking-rule, tolerance, and candidate-bank analyses",
        "DD-MM-YYYY": "19-08-2026",
    }
    yes = [
        "A All data sources are listed in the paper",
        "C We have reported and discussed potential dataset",
        "D The data cleaning and preprocessing steps are cl",
        "E Instances of combining data from multiple source",
        "C The model clearly splits data into different set",
        "D The method of data splitting eg random cluster o",
        "F The data splitting procedure has been chosen to",
        "A The performance metrics used are described and j",
        "B Crossvalidation of the results is included",
        "C Communityaccepted benchmark datasetstasks are us",
        "D Baseline comparisons to simpletrivial models for",
        "E Benchmarks with current stateoftheart are provid",
        "F Ablation experiments are included",
        "A The paper contains information on hardwarecomput",
        "B The paper includes information on the computatio",
    ]
    no = [
        "B The train test and validation datasets are publi",
        "B A Model Card is provided1",
        "E The data splitting mimics anticipated realworld",
        "G The interpretability of the model has been studi",
        "G The model has been tested on a fully independent",
    ]
    for name in yes:
        values[name] = "/" + radio_value(fields, name, "Yes")
    for name in no:
        values[name] = "/" + radio_value(fields, name, "No")
    writer.set_need_appearances_writer(True)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    with intermediate.open("wb") as handle:
        writer.write(handle)
    # Some PDF renderers do not regenerate checkbox appearance streams for the
    # official AcroForm. Add a visible vector X over every selected button while
    # retaining the completed form fields.
    completed = PdfReader(str(intermediate))
    visible = PdfWriter()
    visible.clone_document_from_reader(completed)
    for page in visible.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        buffer = BytesIO()
        overlay_canvas = pdf_canvas.Canvas(buffer, pagesize=(width, height))
        overlay_canvas.setStrokeColor(colors.black)
        overlay_canvas.setLineWidth(1.0)
        selected = 0
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            parent = annotation.get("/Parent")
            parent_obj = parent.get_object() if parent else None
            field_type = annotation.get("/FT") or (parent_obj.get("/FT") if parent_obj else None)
            state = str(annotation.get("/AS", "/Off"))
            if field_type != "/Btn" or state == "/Off":
                continue
            x0, y0, x1, y1 = [float(value) for value in annotation["/Rect"]]
            pad = 1.2
            overlay_canvas.line(x0 + pad, y0 + pad, x1 - pad, y1 - pad)
            overlay_canvas.line(x0 + pad, y1 - pad, x1 - pad, y0 + pad)
            selected += 1
        overlay_canvas.save()
        if selected:
            buffer.seek(0)
            page.merge_page(PdfReader(buffer).pages[0])
    with path.open("wb") as handle:
        visible.write(handle)
    intermediate.unlink()
    return path


def build_cover_letter():
    path = OUT / "Cover_Letter_Nature_Communications.pdf"
    story = []
    story.append(Paragraph(DATE, BODY))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Editors<br/>Nature Communications", BODY))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(f"Re: <b>{TITLE}</b>", BODY))
    story.append(Spacer(1, 4 * mm))
    paragraphs = [
        "Dear Editors,",
        "We submit the Article entitled “WrapEvoFS enables auditable feature compression with regret-constrained representative locking” for consideration in Nature Communications.",
        "Stochastic feature-selection searches can return several near-scoring signatures, yet the final retained run is often chosen by rank or by an undocumented tie rule. WrapEvoFS separates candidate generation from this final decision. It restricts selection to candidates within a prespecified empirical development-score gap, chooses the Jaccard medoid of that eligible pool, and records a deterministic audit trail. The finite-bank guarantee is exact: every selected candidate satisfies the configured empirical score-gap constraint.",
        "The study combines a corrected untruncated genetic objective with three complementary evaluations. A development-only multicentre analysis verifies objective behavior and strict locking feasibility; a four-class TCGA analysis evaluates all study-fitted steps from the supplied matrix under repeated fully nested resampling and matched selector controls; and a one-time post-freeze AMP-AD analysis tests frozen signatures across held-out centers without reselection or retuning. Additional ADNI, CGGA, VGH radiomics, and synthetic candidate-bank analyses characterize scope, reproducibility, and participant-partition sensitivity.",
        "The work should interest the journal’s broad readership because it addresses a general decision problem shared by high-dimensional genomics, proteomics, metabolomics, radiomics, and other stochastic model-selection workflows. The contribution is not a dataset-specific biomarker claim; it is an auditable method for retaining one representative result while preserving an explicit empirical score tolerance.",
        f"WrapEvoFS v0.2.0 is publicly available under the BSD 3-Clause License at {PACKAGE_URL}, with an immutable tagged release and PyPI distribution. Manuscript source, analysis code, aggregate figure source data, checksums, and provenance records are publicly available at {REPRO_URL}. Controlled participant-level data are not redistributed, and all source-access routes and restrictions are stated in the manuscript.",
        "The manuscript is original, is not under consideration elsewhere, and has not been discussed previously with a Nature Communications editor. Authorship, contributions, funding, and competing-interest declarations are provided in the manuscript. Reviewer suggestions and any exclusions will be entered in the submission system.",
        "Thank you for considering our work.",
        "Sincerely,<br/><br/><b>Huan Zhong</b><br/>Michael Smith Laboratories<br/>Department of Biochemistry and Molecular Biology<br/>University of British Columbia<br/>Vancouver, BC, Canada<br/>huan.zhong@ubc.ca",
    ]
    for p in paragraphs:
        story.append(Paragraph(p, BODY))
        story.append(Spacer(1, 2.2 * mm))
    doc(path, "Cover Letter to Nature Communications").build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = [build_bio_summary(), build_ml_checklist(), build_code_checklist(), build_cover_letter()]
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
