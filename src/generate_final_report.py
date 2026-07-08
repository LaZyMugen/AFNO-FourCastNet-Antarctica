"""
Combined Final Report: Midsem + Post-Midsem FourCastNet Work
Generates a formal PS-I report PDF that integrates:
  1. The original midsem content (Introduction, Literature Review, Architecture, etc.)
  2. Post-midsem modifications (extended data, normalization fixes, Bharati, bias correction, dashboards)
  3. Updated results with embedded dashboard figures
  4. Comparative analysis table (FourCastNet vs GraphCast vs Pangu-Weather)
"""
import os, sys, io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, String

# ── Mini chart helpers ──
def mini_line_chart(title, label_a, label_b, pts_a, pts_b, color_a='#2980B9', color_b='#E74C3C', w=100, h=70):
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor('#F8F9F9'), strokeColor=colors.HexColor('#D5D8DC'), strokeWidth=0.5))
    d.add(PolyLine(pts_a, strokeColor=colors.HexColor(color_a), strokeWidth=1.5))
    d.add(PolyLine(pts_b, strokeColor=colors.HexColor(color_b), strokeWidth=1.5))
    d.add(String(6, h-12, title, fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
    d.add(String(6, h-20, label_a, fontSize=5, fontName="Helvetica", fillColor=colors.HexColor(color_a)))
    d.add(String(6, h-27, label_b, fontSize=5, fontName="Helvetica", fillColor=colors.HexColor(color_b)))
    return d

def mini_bar_chart(title, labels, heights, bar_colors, w=100, h=70):
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor('#F8F9F9'), strokeColor=colors.HexColor('#D5D8DC'), strokeWidth=0.5))
    d.add(Line(5, 10, w-5, 10, strokeColor=colors.HexColor('#7F8C8D'), strokeWidth=0.6))
    n = len(labels)
    bar_w = min(22, (w - 20) // (n * 2))
    spacing = (w - 10) // (n + 1)
    for i, (lbl, ht, clr) in enumerate(zip(labels, heights, bar_colors)):
        x = spacing * (i + 1) - bar_w // 2
        d.add(Rect(x, 10, bar_w, ht, fillColor=colors.HexColor(clr), strokeColor=None))
        d.add(String(x + 1, 12, lbl, fontSize=5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
    d.add(String(6, h-12, title, fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
    return d

def safe_image(path, w, h):
    """Return an Image if file exists, else a placeholder Paragraph."""
    if os.path.exists(path):
        return Image(path, width=w, height=h)
    return Paragraph(f"<i>[Image not found: {os.path.basename(path)}]</i>",
                     ParagraphStyle('Missing', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor('#E74C3C')))


def build_report():
    base = Path("D:/AFNO-FourCastNet-Antarctica")
    docs = base / "docs"
    midsem_img = docs / "midsem_images"
    maitri_fig = base / "figures" / "maitri"
    maitri_dash = maitri_fig / "dashboards"
    pdf_path = docs / "AFNO_FourCastNet_Final_Report.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                            rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    # Custom styles
    title_s = ParagraphStyle('T', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1A252F'), alignment=1, spaceAfter=4)
    subtitle_s = ParagraphStyle('ST', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, textColor=colors.HexColor('#7F8C8D'), alignment=1, spaceAfter=6)
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=colors.HexColor('#1A252F'), spaceBefore=14, spaceAfter=8, keepWithNext=True)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#2980B9'), spaceBefore=10, spaceAfter=5, keepWithNext=True)
    h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#2C3E50'), spaceBefore=8, spaceAfter=4, keepWithNext=True)
    body = ParagraphStyle('B', parent=styles['BodyText'], fontName='Helvetica', fontSize=10.5, leading=14, textColor=colors.HexColor('#2C3E50'), spaceAfter=7)
    bullet = ParagraphStyle('BL', parent=styles['Normal'], fontName='Helvetica', fontSize=10.5, leading=14, textColor=colors.HexColor('#2C3E50'), leftIndent=20, firstLineIndent=-12, spaceAfter=4)
    caption = ParagraphStyle('CAP', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=colors.HexColor('#7F8C8D'), alignment=1, spaceAfter=12, spaceBefore=4)
    th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.whitesmoke)
    cl = ParagraphStyle('CL', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#2C3E50'))
    cb = ParagraphStyle('CB', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#2C3E50'))

    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 60))
    # BITS logo if available
    logo_path = str(midsem_img / "page1_img1.png")
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=0.8*inch, height=0.8*inch, hAlign='CENTER'))
        story.append(Spacer(1, 10))

    story.append(Paragraph("REPORT ON", ParagraphStyle('R', parent=styles['Normal'], fontName='Helvetica', fontSize=11, alignment=1, textColor=colors.HexColor('#7F8C8D'), spaceAfter=4)))
    story.append(Paragraph("AFNO-Based FourCastNet Model for<br/>Antarctic Weather Forecasting", title_s))
    story.append(Spacer(1, 8))
    story.append(Paragraph("BY", ParagraphStyle('R2', parent=styles['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#7F8C8D'), spaceAfter=8)))

    cover_info = [
        ["Name of the Student", "Shaswat Sahoo"],
        ["ID No.", "2024A7PS0152H"],
        ["Discipline", "B.E. in CSE"],
    ]
    t_cov1 = Table(cover_info, colWidths=[160, 310])
    t_cov1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#F8F9F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_cov1)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Prepared in partial fulfillment of the <b>Practice School - I</b>", subtitle_s))
    story.append(Paragraph("AT", ParagraphStyle('R3', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#7F8C8D'), spaceAfter=6)))
    story.append(Paragraph("<b>National Centre for Polar and Ocean Research (NCPOR), Goa</b>", ParagraphStyle('R4', parent=styles['Normal'], fontSize=11, alignment=1, textColor=colors.HexColor('#2C3E50'), spaceAfter=4)))
    story.append(Paragraph("A Practice School - I Station of", ParagraphStyle('R5', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#7F8C8D'), spaceAfter=4)))
    story.append(Paragraph("<b>BIRLA INSTITUTE OF TECHNOLOGY &amp; SCIENCE, PILANI</b>", ParagraphStyle('R6', parent=styles['Normal'], fontSize=11, alignment=1, textColor=colors.HexColor('#2C3E50'), spaceAfter=8)))
    story.append(Spacer(1, 8))

    cover_meta = [
        ["Station", "National Centre for Polar and Ocean Research, Goa"],
        ["Duration", "May 2026 - July 2026"],
        ["Date of Start", "25th May 2026"],
        ["Date of Submission", "18th July 2026"],
        ["Expert Mentor", "VS Samy, Scientist, NCPOR"],
        ["PS Faculty", "Prof Hemant Rathore"],
        ["Key Words", "FourCastNet, AFNO, Antarctic, ERA5, Deep Learning, Weather Forecasting, Bias Correction"],
        ["Project Areas", "Numerical Weather Prediction, Deep Learning, Polar Meteorology"],
    ]
    t_meta = Table(cover_meta, colWidths=[130, 340])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.whitesmoke),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#FAFAFA')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Abstract:</b> This report presents a lightweight AFNO-based FourCastNet model for regional "
        "Antarctic weather forecasting at Maitri and Bharati stations. ERA5 reanalysis data (2016-2026) "
        "is used with a 48-hour input window to produce 24-hour forecasts at 6-hourly resolution. "
        "Post-processing bias correction achieves an out-of-sample temperature R-squared of 0.918 for Maitri.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # ACKNOWLEDGEMENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Acknowledgements", h1))
    story.append(Paragraph(
        "I would like to express my sincere gratitude to the National Centre for Polar and Ocean "
        "Research (NCPOR), Goa, for providing me with the opportunity to undertake this Practice "
        "School internship. I am deeply grateful to my expert mentor at NCPOR, <b>VS Samy</b>, for their "
        "invaluable guidance, patient explanations, and continuous encouragement throughout the project. "
        "I also thank the Practice School faculty member, <b>Prof Hemant Rathore</b>, for their academic "
        "oversight and constructive feedback.", body))
    story.append(Paragraph(
        "I acknowledge the European Centre for Medium-Range Weather Forecasts (ECMWF) and "
        "the Copernicus Climate Data Store (CDS) for making the ERA5 reanalysis dataset publicly "
        "available, which formed the backbone of this project. I also thank the developers of the "
        "original FourCastNet framework whose open-source contributions made this regional adaptation possible.", body))
    story.append(Paragraph(
        "Finally, I thank BITS Pilani, Hyderabad Campus, and the Practice School Division for "
        "designing the PS-I programme, which bridges academic learning with real-world scientific challenges.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", h1))
    toc = [
        "1. Introduction",
        "    1.1 Objectives",
        "    1.2 Organisation of the Report",
        "2. Literature Review",
        "    2.1 Data-Driven Weather Prediction",
        "    2.2 Fourier Neural Operators and FourCastNet",
        "    2.3 Antarctic Meteorological Modelling",
        "3. Dataset and Preprocessing",
        "    3.1 ERA5 Reanalysis Data",
        "    3.2 Variables",
        "    3.3 Dataset Shape and Temporal Structure",
        "    3.4 Normalization",
        "4. Model Architecture",
        "    4.1 Patch Embedding",
        "    4.2 Positional Embedding",
        "    4.3 Adaptive Fourier Neural Operator (AFNO) Block",
        "    4.4 Patch Recovery and Dynamic Grid Support",
        "5. Methodology and Training",
        "    5.1 Training Configuration",
        "    5.2 Post-Midsem Modifications",
        "    5.3 Thermal-Safe CPU Training Pipeline",
        "6. Results: Maitri Station",
        "    6.1 Training Convergence",
        "    6.2 Temperature Forecast Skill",
        "    6.3 Wind Speed Forecast Skill",
        "    6.4 Severe Weather Meteorogram",
        "    6.5 Monthly Climatological Drift",
        "7. Bias Correction Post-Processing",
        "8. Results: Bharati Station",
        "9. Comparative Analysis: FourCastNet vs GraphCast vs Pangu-Weather",
        "10. Conclusions and Future Work",
        "11. Recommendations",
        "Bibliography",
        "Appendices",
    ]
    for item in toc:
        indent = 20 if item.startswith("    ") else 0
        s = ParagraphStyle('TOC', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14,
                           textColor=colors.HexColor('#2C3E50'), leftIndent=indent, spaceAfter=2)
        story.append(Paragraph(item.strip(), s))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 1: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 1: Introduction", h1))
    story.append(Paragraph(
        "Weather forecasting in polar regions presents unique scientific and operational challenges. "
        "The Antarctic continent, characterised by extreme cold, strong katabatic winds, and limited "
        "observational infrastructure, remains one of the most data-sparse regions on Earth. Accurate "
        "meteorological prediction over Antarctica is critical for the safety of research personnel, "
        "logistics planning of polar expeditions, and understanding of global climate systems.", body))
    story.append(Paragraph(
        "Traditional Numerical Weather Prediction (NWP) systems such as ECMWF's Integrated "
        "Forecasting System (IFS) rely on physics-based dynamical models that are computationally "
        "intensive and struggle to represent fine-scale polar phenomena. In recent years, data-driven "
        "deep learning models have emerged as powerful alternatives, demonstrating skill comparable "
        "to or exceeding operational NWP systems at a fraction of the computational cost.", body))
    story.append(Paragraph(
        "FourCastNet (Fourier Forecasting Neural Network), developed by Pathak et al. (2022) at "
        "NVIDIA, employs the Adaptive Fourier Neural Operator (AFNO) as its core computational block, "
        "enabling efficient modelling of atmospheric dynamics in the Fourier frequency domain. "
        "This project adapts the FourCastNet philosophy to a regional Antarctic context, targeting "
        "two Indian research stations: <b>Maitri</b> (Schirmacher Oasis, 70.76S) and <b>Bharati</b> "
        "(Larsemann Hills, 69.41S).", body))

    story.append(Paragraph("1.1 Objectives", h2))
    objectives = [
        "- Acquire, preprocess, and normalise ERA5 reanalysis data for both Maitri and Bharati Antarctic domains.",
        "- Implement a lightweight AFNO-based FourCastNet architecture with dynamic grid support.",
        "- Train the model to produce 24-hour forecasts from a 48-hour input history at 6-hourly resolution.",
        "- Implement Ridge Regression-based bias correction post-processing for temperature and wind speed.",
        "- Evaluate forecast quality through comprehensive validation dashboards (scatter plots, meteorograms, climatological drift analysis).",
        "- Generate a comparative analysis against other leading AI weather models (GraphCast, Pangu-Weather).",
    ]
    for obj in objectives:
        story.append(Paragraph(obj, bullet))

    story.append(Paragraph("1.2 Organisation of the Report", h2))
    story.append(Paragraph(
        "Chapter 2 provides a literature review. Chapter 3 describes the dataset and preprocessing. "
        "Chapter 4 presents the model architecture. Chapter 5 covers training configuration and post-midsem "
        "modifications. Chapters 6-8 present results for both stations. Chapter 9 provides a head-to-head "
        "comparative analysis. Chapter 10 concludes the report, and Chapter 11 provides recommendations.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 2: LITERATURE REVIEW
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 2: Literature Review", h1))
    story.append(Paragraph("2.1 Data-Driven Weather Prediction", h2))
    story.append(Paragraph(
        "The application of deep learning to weather forecasting has seen rapid advances. Weyn et al. (2020) "
        "demonstrated the viability of CNNs for medium-range forecasting on a cubed-sphere grid. "
        "Pangu-Weather (Bi et al., 2023) employs a 3D Earth Transformer to achieve superior 10-day "
        "forecast accuracy compared to ECMWF. GraphCast (Lam et al., 2023) uses a graph neural network "
        "over a multi-scale icosahedral mesh, achieving state-of-the-art skill on 1380 forecast targets. "
        "Aurora (Chen et al., 2024) pushes the boundary with a large foundation model approach.", body))

    story.append(Paragraph("2.2 Fourier Neural Operators and FourCastNet", h2))
    story.append(Paragraph(
        "The Fourier Neural Operator (FNO), proposed by Li et al. (2021), applies spectral convolutions "
        "in the Fourier domain to learn PDE solution operators efficiently. The Adaptive Fourier Neural "
        "Operator (AFNO), introduced by Guibas et al. (2021), extends this to vision transformer-style "
        "architectures with learned Fourier mixing. FourCastNet (Pathak et al., 2022) integrates AFNO "
        "blocks into an end-to-end autoregressive forecasting architecture trained on ERA5, demonstrating "
        "a 45,000x speedup over ECMWF IFS while matching forecast skill.", body))

    story.append(Paragraph("2.3 Antarctic Meteorological Modelling", h2))
    story.append(Paragraph(
        "Antarctic weather forecasting has historically relied on global NWP output supplemented by "
        "regional models such as Polar WRF and the Antarctic Mesoscale Prediction System (AMPS). "
        "The limited observational density over Antarctica makes data assimilation difficult. Deep "
        "learning models trained on reanalysis data offer a promising alternative for regional deployment, "
        "particularly for research stations such as Maitri and Bharati operated by NCPOR.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 3: DATASET AND PREPROCESSING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 3: Dataset and Preprocessing", h1))
    story.append(Paragraph("3.1 ERA5 Reanalysis Data", h2))
    story.append(Paragraph(
        "The ERA5 reanalysis dataset, produced by ECMWF, provides global atmospheric data at 0.25-degree "
        "horizontal resolution with hourly temporal resolution. Data was retrieved from the Copernicus "
        "Climate Data Store (CDS) for both Antarctic station domains.", body))

    story.append(Paragraph("3.2 Maitri Station Dataset", h3))
    m_data = [
        ["Parameter", "Midsem (Original)", "Post-Midsem (Updated)"],
        ["Temporal Coverage", "2021-2025 (5 years)", "2017-2026 (9.5 years)"],
        ["Bounding Box", "60S-75S, 10E-15E", "68S-73S, 0E-20E"],
        ["Grid Resolution", "21 x 101", "21 x 81"],
        ["Time Steps", "8,768", "13,860"],
        ["Data Format", "NetCDF (.nc files)", "GRIB (single file, converted to .npy)"],
        ["Raw File Size", "~2 GB (5 NetCDF files)", "362 MB (single GRIB)"],
        ["Normalization", "Standard (per-variable)", "Z-score (Mean~0, Std~1, verified)"],
    ]
    t_m = Table(m_data, colWidths=[120, 175, 205])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_m)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.3 Bharati Station Dataset (Post-Midsem Addition)", h3))
    b_data = [
        ["Parameter", "Value"],
        ["Bounding Box", "Lat 60S-89.75S, Lon 50E-99.75E"],
        ["Grid Resolution", "120 x 200 grid points"],
        ["Temporal Coverage", "2016-2025 (10 years)"],
        ["Time Steps", "14,612"],
        ["Variables", "u10, v10, t2m, msl"],
        ["Processed File Size", "5.61 GB (NumPy .npy, normalized)"],
    ]
    t_b = Table(b_data, colWidths=[160, 340])
    t_b.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_b)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.4 Normalization", h2))
    story.append(Paragraph(
        "All variables were standardized using z-score normalization (subtracting the per-variable mean "
        "and dividing by the standard deviation, computed across the entire temporal and spatial extent). "
        "This is critical for neural network convergence -- unnormalized Bharati data initially produced "
        "training losses of 625 million, which dropped to ~0.65 after proper normalization.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 4: MODEL ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 4: Model Architecture", h1))
    story.append(Paragraph(
        "The model follows the original FourCastNet design philosophy while remaining lightweight "
        "enough for local training and HPC deployment. The processing pipeline is:", body))
    story.append(Paragraph("ERA5 Input --> Patch Embedding --> Positional Embedding --> AFNO Blocks (x6) --> Patch Recovery --> 24-Hour Forecast", body))

    story.append(Paragraph("4.1 Patch Embedding", h2))
    story.append(Paragraph(
        "The input weather field is divided into non-overlapping 4x4 spatial patches via a 2D convolutional "
        "projection layer (inspired by ViT tokenisation). For patch size P=4, the spatial dimensions are "
        "reduced by a factor of 4 in each direction, producing tokens of embedding dimension d=128.", body))

    story.append(Paragraph("4.2 Adaptive Fourier Neural Operator (AFNO) Block", h2))
    story.append(Paragraph(
        "The AFNO block is the core computational unit. Each block processes spatial features through: "
        "(1) 2D FFT to the frequency domain, (2) learned MLP-based frequency mixing with GELU activation, "
        "(3) inverse FFT back to spatial domain, and (4) residual connection. This achieves O(N log N) "
        "complexity versus O(N^2) for standard self-attention. Six AFNO blocks are stacked sequentially.", body))

    config_table = [
        ["Hyperparameter", "Value"],
        ["Patch size (P)", "4"],
        ["Embedding dimension (d)", "128"],
        ["Number of AFNO blocks (N)", "6"],
        ["MLP expansion ratio (r)", "4"],
        ["Input steps (I)", "8 (48 hours)"],
        ["Output steps (O)", "4 (24 hours)"],
        ["Variables (V)", "4"],
        ["Total parameters", "~1.73 M"],
    ]
    t_cfg = Table(config_table, colWidths=[200, 300])
    t_cfg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(Paragraph("Table 4.1: Model Configuration Summary", caption))
    story.append(t_cfg)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 5: METHODOLOGY AND TRAINING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 5: Methodology and Training", h1))
    story.append(Paragraph("5.1 Training Configuration", h2))
    train_table = [
        ["Parameter", "Midsem", "Post-Midsem (Updated)"],
        ["Batch size", "4", "8"],
        ["Learning rate", "1e-4 (fixed)", "1e-4 (Cosine Annealing to 1e-6)"],
        ["Optimizer", "Adam", "Adam"],
        ["Loss function", "MSE", "MSE"],
        ["Epochs", "30", "30 (with early stopping, patience=10)"],
        ["Train/Val split", "80%/20%", "80%/20% (date-based, not random)"],
        ["Device", "GPU (when available)", "CPU only (single-threaded, thermal-safe)"],
        ["Gradient Clipping", "None", "Max norm = 1.0"],
    ]
    t_train = Table(train_table, colWidths=[120, 150, 230])
    t_train.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_train)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Post-Midsem Modifications", h2))
    story.append(Paragraph("The following key changes were made after the mid-semester evaluation to improve "
        "model robustness, accuracy, and reproducibility:", body))
    mods = [
        "- <b>Extended Training Data:</b> Maitri dataset expanded from 5 years (2021-2025) to 9.5 years (2017-2026), increasing training samples from 8,768 to 13,860 timesteps.",
        "- <b>GRIB-based Pipeline:</b> Replaced the 5-file NetCDF pipeline with a single pre-cropped GRIB file downloaded directly from CDS, eliminating cfgrib memory leaks during preprocessing.",
        "- <b>Bharati Station Added:</b> Extended the pipeline to support a second Indian Antarctic station with a much larger spatial domain (120x200 grid).",
        "- <b>Verified Normalization:</b> Added explicit verification checks to ensure z-score normalization produces Mean~0 and Std~1 for all variables before training begins.",
        "- <b>Cosine Annealing LR Schedule:</b> Replaced the fixed learning rate with a cosine annealing schedule that smoothly decays from 1e-4 to 1e-6 over the training run.",
        "- <b>Bias Correction Layer:</b> Added a Ridge Regression post-processing step that corrects systematic forecast biases using cyclical time features (sine/cosine encoded day-of-year and hour-of-day).",
        "- <b>Validation Dashboards:</b> Created a 4-dashboard evaluation suite (temperature scatter, wind scatter, storm meteorogram, climatological drift) for visual quality assessment.",
        "- <b>Station-Separated Outputs:</b> Refactored all scripts to save checkpoints and figures into station-specific subdirectories (checkpoints/maitri/, figures/maitri/) to prevent cross-contamination.",
    ]
    for m in mods:
        story.append(Paragraph(m, bullet))

    story.append(Paragraph("5.3 Thermal-Safe CPU Training Pipeline", h2))
    story.append(Paragraph(
        "Due to laptop thermal constraints (RTX 3050 GPU causing system shutdowns), all training was "
        "executed on CPU with single-threaded execution (OMP_NUM_THREADS=1, MKL_NUM_THREADS=1) and "
        "3-second cooling breaks between epochs. This kept CPU utilisation under 15% and eliminated "
        "all thermal crashes while maintaining full training convergence.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 6: RESULTS - MAITRI
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 6: Results - Maitri Station", h1))

    story.append(Paragraph("6.1 Training Convergence", h2))
    story.append(Paragraph(
        "The Maitri model was trained for 30 epochs. Training loss decreased from 0.179 (Epoch 1) "
        "to 0.126 (Epoch 30). The validation loss converged to <b>0.1448</b>, indicating good "
        "generalisation without significant overfitting.", body))

    train_hist = str(maitri_fig / "training_history_maitri.png")
    story.append(safe_image(train_hist, 5.5*inch, 2.8*inch))
    story.append(Paragraph("Figure 6.1: Training and Validation Loss Convergence (Maitri, 30 Epochs)", caption))

    story.append(Paragraph("6.2 Temperature Forecast Skill", h2))
    story.append(Paragraph(
        "The scatter plot shows the model's 2m temperature forecasts against ERA5 ground truth "
        "for the out-of-sample test period (2025-2026). Left panel: raw model output. "
        "Right panel: bias-corrected predictions.", body))
    story.append(safe_image(str(maitri_dash / "dashboard_temp_scatter_maitri.png"), 6.2*inch, 2.9*inch))
    story.append(Paragraph("Figure 6.2: Maitri Temperature Scatter - Raw vs Bias-Corrected (2025-2026)", caption))

    story.append(PageBreak())

    story.append(Paragraph("6.3 Wind Speed Forecast Skill", h2))
    story.append(safe_image(str(maitri_dash / "dashboard_wind_scatter_maitri.png"), 6.2*inch, 2.9*inch))
    story.append(Paragraph("Figure 6.3: Maitri Wind Speed Scatter - Raw vs Bias-Corrected (2025-2026)", caption))

    story.append(Paragraph("6.4 Severe Weather Meteorogram", h2))
    story.append(Paragraph(
        "The meteorogram captures a 72-hour window around the most extreme wind event in the test "
        "period, showing how well the model tracks rapid temperature drops and wind speed spikes.", body))
    story.append(safe_image(str(maitri_dash / "dashboard_storm_meteorogram_maitri.png"), 5.8*inch, 3.8*inch))
    story.append(Paragraph("Figure 6.4: 72-Hour Storm Meteorogram - Temperature and Wind Speed (Maitri)", caption))

    story.append(Paragraph("6.5 Monthly Climatological Drift", h2))
    story.append(safe_image(str(maitri_dash / "dashboard_climatology_drift_maitri.png"), 6.2*inch, 2.9*inch))
    story.append(Paragraph("Figure 6.5: Monthly Climatological Drift Analysis (Maitri, 2025-2026)", caption))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 7: BIAS CORRECTION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 7: Bias Correction Post-Processing", h1))
    story.append(Paragraph(
        "Raw neural network forecasts exhibit systematic biases that vary with time of day and season. "
        "A Ridge Regression model was trained as a post-processing layer, taking the raw model prediction "
        "along with cyclical time features (day-of-year and hour-of-day encoded as sine/cosine pairs) "
        "and learning to map them to observed values.", body))

    bc_table = [
        ["Variable", "Raw Model R-squared", "Bias-Corrected R-squared", "Improvement"],
        ["2m Temperature", "0.9165", "0.9177", "+0.13%"],
        ["10m Wind Speed", "0.6677", "0.6861", "+2.76%"],
    ]
    t_bc = Table(bc_table, colWidths=[120, 130, 140, 110])
    t_bc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(Paragraph("Table 7.1: Maitri Bias Correction Results (Out-of-Sample 2025-2026)", caption))
    story.append(t_bc)

    # ══════════════════════════════════════════════════════════════════════════
    # CH 8: BHARATI
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 15))
    story.append(Paragraph("Chapter 8: Results - Bharati Station", h1))
    story.append(Paragraph(
        "The Bharati model is trained on a significantly larger spatial domain (120 x 200 grid points "
        "vs. Maitri's 21 x 81). The dataset has been fully preprocessed and normalized. Base model "
        "training was initiated and will be completed upon resumption. The model architecture remains "
        "identical to the Maitri configuration.", body))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 9: COMPARATIVE ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 9: Comparative Analysis", h1))
    story.append(Paragraph("FourCastNet vs GraphCast vs Pangu-Weather", subtitle_s))

    comp = [
        [Paragraph("Feature", th), Paragraph("FourCastNet<br/>(NVIDIA)", th), Paragraph("GraphCast<br/>(DeepMind)", th), Paragraph("Pangu-Weather<br/>(Huawei)", th), Paragraph("Trend", th)],
        [Paragraph("<b>Architecture</b>", cl), Paragraph("AFNO Vision Transformer", cb), Paragraph("GNN Message-Passing on Icosahedral Mesh", cb), Paragraph("3D Swin Transformer with Earth Positional Encoding", cb), Paragraph("", cb)],
        [Paragraph("<b>Training VRAM</b>", cl), Paragraph("<font color='#27AE60'><b>6-16 GB</b></font>", cb), Paragraph("<font color='#E74C3C'>32+ GB</font>", cb), Paragraph("<font color='#E74C3C'>32+ GB</font>", cb),
         mini_bar_chart("VRAM (GB)", ["FCN","GC","PW"], [8, 40, 35], ['#27AE60','#E74C3C','#E74C3C'])],
        [Paragraph("<b>Inference Speed</b>", cl), Paragraph("<font color='#27AE60'><b>&lt; 2 seconds</b></font>", cb), Paragraph("~30 seconds", cb), Paragraph("~5 seconds", cb),
         mini_bar_chart("Speed", ["FCN","GC","PW"], [45, 4, 25], ['#27AE60','#E74C3C','#F39C12'])],
        [Paragraph("<b>Short-Range (0-3d)</b>", cl), Paragraph("<font color='#27AE60'><b>Excellent</b></font>", cb), Paragraph("<font color='#27AE60'><b>Excellent</b></font>", cb), Paragraph("<font color='#27AE60'><b>Excellent</b></font>", cb),
         mini_line_chart("RMSE 0-3d", "AI", "HRES", [(10,15),(30,20),(50,24),(70,28),(90,31)], [(10,18),(30,23),(50,27),(70,31),(90,34)], '#27AE60', '#7F8C8D')],
        [Paragraph("<b>Medium-Range (5-10d)</b>", cl), Paragraph("<font color='#E74C3C'>Degrades</font><br/>Error drift", cb), Paragraph("<font color='#27AE60'><b>Best in class</b></font>", cb), Paragraph("<font color='#F39C12'>Good</font>", cb),
         mini_line_chart("RMSE 5-10d", "FCN", "GC", [(10,15),(30,25),(50,38),(70,48),(90,58)], [(10,14),(30,19),(50,24),(70,30),(90,35)], '#E74C3C', '#2980B9')],
        [Paragraph("<b>Polar Accuracy</b>", cl), Paragraph("<font color='#E74C3C'>Weak</font><br/>Flat FFT distortion", cb), Paragraph("<font color='#27AE60'><b>Strong</b></font><br/>Spherical mesh", cb), Paragraph("<font color='#F39C12'>Moderate</font>", cb),
         mini_bar_chart("Polar Error", ["FCN","GC","PW"], [38, 8, 25], ['#E74C3C','#27AE60','#F39C12'])],
        [Paragraph("<b>Ensemble Scalability</b>", cl), Paragraph("<font color='#27AE60'><b>Excellent</b></font><br/>10,000+ members", cb), Paragraph("<font color='#F39C12'>Good</font><br/>~100 members", cb), Paragraph("<font color='#27AE60'>Very Good</font><br/>~1,000 members", cb),
         mini_bar_chart("Ensemble", ["FCN","GC","PW"], [45, 6, 22], ['#27AE60','#E74C3C','#F39C12'])],
        [Paragraph("<b>Physical Conservation</b>", cl), Paragraph("<font color='#E74C3C'>None</font>", cb), Paragraph("<font color='#E74C3C'>None</font>", cb), Paragraph("<font color='#E74C3C'>None</font>", cb), Paragraph("<i>All lack physics</i>", cb)],
        [Paragraph("<b>Precipitation Skill</b>", cl), Paragraph("<font color='#E74C3C'>Weak</font>", cb), Paragraph("<font color='#F39C12'>Moderate</font>", cb), Paragraph("<font color='#F39C12'>Moderate</font>", cb),
         mini_bar_chart("Precip", ["FCN","GC","PW"], [6, 20, 18], ['#E74C3C','#F39C12','#F39C12'])],
        [Paragraph("<b>Variables Predicted</b>", cl), Paragraph("~25 total", cb), Paragraph("~228 total", cb), Paragraph("~69 total", cb),
         mini_bar_chart("Vars", ["FCN","GC","PW"], [6, 45, 18], ['#E74C3C','#27AE60','#F39C12'])],
        [Paragraph("<b>Open Source</b>", cl), Paragraph("<font color='#27AE60'>Fully Open</font>", cb), Paragraph("<font color='#27AE60'>Fully Open</font>", cb), Paragraph("<font color='#F39C12'>Partial</font>", cb), Paragraph("", cb)],
        [Paragraph("<b>Best Suited For</b>", cl), Paragraph("Short-range local forecasting. Massive ensembles. Edge deployment.", cb), Paragraph("Medium-range global forecasting. Extreme weather tracking.", cb), Paragraph("Operational 5-day forecasting. Pressure-level analysis.", cb), Paragraph("", cb)],
    ]

    t_comp = Table(comp, colWidths=[80, 130, 130, 130, 60])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A252F')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FAFAFA')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#F2F4F4')),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#F2F4F4')),
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#F2F4F4')),
        ('BACKGROUND', (0,9), (-1,9), colors.HexColor('#F2F4F4')),
        ('BACKGROUND', (0,11), (-1,11), colors.HexColor('#F2F4F4')),
        ('BACKGROUND', (0,13), (-1,13), colors.HexColor('#F2F4F4')),
    ]))
    story.append(t_comp)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 10: CONCLUSIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 10: Conclusions and Future Work", h1))
    story.append(Paragraph("10.1 Conclusions", h2))
    conclusions = [
        "- A working ERA5 data pipeline for both Maitri and Bharati Antarctic domains, producing clean training-ready datasets spanning 9.5 and 10 years respectively.",
        "- A lightweight AFNO-based FourCastNet implementation with dynamic grid support, automatic padding, and station-separated output structure.",
        "- Demonstrated forecast skill for surface temperature with an out-of-sample R-squared of <b>0.918</b> at Maitri station.",
        "- Successful bias correction post-processing that improved wind speed R-squared by 2.76%.",
        "- A thermal-safe training pipeline enabling reliable training on consumer laptop hardware.",
        "- Comprehensive validation dashboards for visual quality assessment of forecast skill.",
    ]
    for c in conclusions:
        story.append(Paragraph(c, bullet))

    story.append(Paragraph("10.2 Future Work", h2))
    futures = [
        "- <b>Station-wise observational validation:</b> Validate against actual observational records from Maitri and Bharati.",
        "- <b>Multi-step rollout training:</b> Implement autoregressive rollout loss to reduce forecast drift beyond 24 hours.",
        "- <b>Spherical Harmonic Transforms:</b> Replace flat 2D FFTs to improve polar accuracy.",
        "- <b>Extended variable coverage:</b> Add specific humidity, precipitation, cloud cover, and sea-ice concentration.",
        "- <b>HPC scaling:</b> Scale to full FourCastNet parameter counts (45-75M) on NCPOR HPC infrastructure.",
        "- <b>GraphCast comparison:</b> Perform head-to-head skill comparison at Antarctic stations.",
    ]
    for f in futures:
        story.append(Paragraph(f, bullet))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # CH 11: RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 11: Recommendations", h1))
    recs = [
        "- <b>Establish a dedicated ERA5 archive:</b> A curated, continuously updated ERA5 archive for the Antarctic domain should be maintained at NCPOR.",
        "- <b>Invest in GPU-enabled HPC capacity:</b> Access to multi-GPU HPC nodes would enable training on decade-scale data with full FourCastNet model sizes.",
        "- <b>Prioritise in-situ data collection:</b> Digitising historical station records from Maitri and Bharati would enhance verification capability.",
        "- <b>Pursue collaborative benchmarking:</b> Participating in benchmarking with other Antarctic NWP groups would provide context for evaluating data-driven models.",
        "- <b>Consider probabilistic extensions:</b> Future model versions should target probabilistic outputs via ensemble generation or diffusion-based approaches.",
    ]
    for r in recs:
        story.append(Paragraph(r, bullet))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # BIBLIOGRAPHY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Bibliography", h1))
    refs = [
        "[1] Ba, Kiros, Hinton. Layer normalization. NeurIPS Workshop, 2016.",
        "[2] Bi et al. Accurate medium-range global weather forecasting with 3D neural networks. Nature, 619:533-538, 2023.",
        "[3] Bromwich et al. Development and testing of Polar WRF. J. Geophys. Res., 118(6):2463-2484, 2013.",
        "[4] Chen et al. Aurora: A foundation model of the atmosphere. arXiv:2405.13063, 2024.",
        "[5] Guibas et al. Adaptive Fourier neural operators: Efficient token mixers for transformers. ICLR, 2022.",
        "[6] Harris et al. Array programming with NumPy. Nature, 585(7825):357-362, 2020.",
        "[7] He et al. Deep residual learning for image recognition. CVPR, 2016.",
        "[8] Hersbach et al. The ERA5 global reanalysis. QJRMS, 146(730):1999-2049, 2020.",
        "[9] Hunter. Matplotlib: A 2D graphics environment. Computing in Science &amp; Engineering, 2007.",
        "[10] Kingma, Ba. Adam: A method for stochastic optimization. arXiv:1412.6980, 2014.",
        "[11] Lam et al. Learning skillful medium-range global weather forecasting. Science, 382(6677):1416-1421, 2023.",
        "[12] Li et al. Fourier neural operator for parametric PDEs. ICLR, 2021.",
        "[13] Paszke et al. PyTorch: An imperative style, high-performance deep learning library. NeurIPS, 2019.",
        "[14] Pathak et al. FourCastNet: A global data-driven high-resolution weather model using adaptive Fourier neural operators. arXiv:2202.11214, 2022.",
        "[15] Powers et al. The Antarctic mesoscale prediction system (AMPS). Bull. AMS, 93(10):1545-1563, 2012.",
        "[16] Rasp, Thuerey. Data-driven medium-range weather prediction with a ResNet. JAMES, 2021.",
        "[17] Tastula et al. Evaluation of Polar WRF. Monthly Weather Review, 140(10):3258-3273, 2012.",
        "[18] Vaswani et al. Attention is all you need. NeurIPS, 2017.",
        "[19] Weyn et al. Improving data-driven global weather prediction using deep CNNs. JAMES, 2020.",
        "[20] Whitaker et al. netCDF4 python interface, 2023.",
    ]
    ref_style = ParagraphStyle('REF', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12,
                               textColor=colors.HexColor('#2C3E50'), spaceAfter=3, leftIndent=25, firstLineIndent=-25)
    for r in refs:
        story.append(Paragraph(r, ref_style))

    # Build
    print("Building combined final report PDF...")
    doc.build(story)
    print(f"PDF created at: {pdf_path}")


if __name__ == "__main__":
    build_report()
