import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import sys

def create_project_report():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    pdf_path = docs_dir / "antarctica_project_report.pdf"
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        name='DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#2C3E50'),
        alignment=0,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        name='DocH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1A252F'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        name='DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#34495E'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        name='DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        name='DocCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#27AE60'),
        backColor=colors.HexColor('#F8F9F9'),
        borderPadding=6,
        spaceAfter=8
    )
    
    story = []
    
    # Title
    story.append(Paragraph("Antarctica Regional Weather Forecasting", title_style))
    story.append(Paragraph("<b>Model Configuration, Station Breakdowns, and Remote Execution Guide</b>", body_style))
    story.append(Spacer(1, 15))
    
    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    summary_text = (
        "This project implements a regionalized <b>FourCastNet (Adaptive Fourier Neural Operator - AFNO)</b> "
        "framework for high-accuracy weather forecasting at two Indian research stations in Antarctica: "
        "<b>Bharati</b> and <b>Maitri</b>. To prevent local hardware crashes and ensure absolute training "
        "stability, a single-threaded CPU execution pipeline with automated cooling intervals is utilized. "
        "Additionally, a machine learning post-processing layer (Ridge Regression Correctors) resolves localized "
        "systematic biases dynamically."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # Section 2: Model Architecture & Common Parameters
    story.append(Paragraph("2. Model Architecture & Common Parameters", h1_style))
    story.append(Paragraph("The regional FourCastNet neural network uses the following configuration parameters:", body_style))
    
    config_data = [
        ["Parameter Name", "Value", "Description"],
        ["Lookback Window (IN_STEPS)", "8 steps (48 hours)", "Historical duration fed into the model."],
        ["Prediction Window (OUT_STEPS)", "4 steps (24 hours)", "Direct forecasting horizon for the neural network."],
        ["Time Interval", "6 hours", "Temporal resolution of the ERA5 dataset."],
        ["Patch Size", "4 x 4 pixels", "Size of spatial patches mapped to the embedding space."],
        ["Embedding Dimension", "128", "Dimensionality of features in the transformer layers."],
        ["Number of Blocks", "6", "Number of sequential AFNO blocks in the model depth."],
        ["MLP Ratio", "4", "Expansion multiplier inside the block feedforward networks."],
        ["Learning Rate", "1e-4", "Initial learning rate utilizing Cosine Annealing scheduler."],
        ["Epochs", "30", "Maximum training epochs with 10-epoch early stopping patience."]
    ]
    
    t_config = Table(config_data, colWidths=[150, 120, 230])
    t_config.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_config)
    story.append(Spacer(1, 15))
    
    # Page Break for clean layout
    story.append(PageBreak())
    
    # Section 3: Station Specific Parameters
    story.append(Paragraph("3. Station Grid Specific Parameters", h1_style))
    story.append(Paragraph("The spatial datasets are customized for each station's respective geographical bounding boxes:", body_style))
    
    station_data = [
        ["Parameter", "Bharati Station", "Maitri Station"],
        ["Coordinates", "69.01° S, 76.19° E", "70.76° S, 11.73° E"],
        ["Bounding Box (Lat)", "-60.0° S to -89.75° S", "-68.0° S to -73.0° S"],
        ["Bounding Box (Lon)", "50.0° E to 99.75° E", "0.0° E to 20.0° E"],
        ["Grid Resolution", "120 x 200 points", "21 x 81 points"],
        ["Padded Resolution", "120 x 200 points", "24 x 84 points"],
        ["Station Index (Lat, Lon)", "Index (36, 105)", "Index (11, 47)"],
        ["Dataset File", "era5_processed.npy", "era5_maitri.npy"],
        ["Raw GRIB size", "10.42 GB", "362 MB"],
        ["Processed Dataset size", "5.61 GB (14,612 steps)", "495 MB (13,860 steps)"],
        ["Dataset Variables", "u10, v10, t2m, msl", "t2m, u10, v10, z"],
        ["Split logic", "Train: 2016-23 | BC: 2023 | Test: 2024-25", "Train: 2017-24 | BC: 2024 | Test: 2025-26"]
    ]
    
    t_station = Table(station_data, colWidths=[160, 170, 170])
    t_station.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A252F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_station)
    story.append(Spacer(1, 15))
    
    # Section 4: Validation Performance (R²)
    story.append(Paragraph("4. Historical Out-of-Sample Performance", h1_style))
    story.append(Paragraph(
        "Post-processing via non-linear Ridge regression correctors resolves systematic diurnal and "
        "seasonal errors, yielding significant R² gains:", body_style
    ))
    
    metrics_data = [
        ["Station", "Variable", "Raw Model R²", "Bias-Corrected R²", "Evaluation Period"],
        ["Bharati", "2m Temperature", "0.908", "0.923", "Years 2024 - 2025"],
        ["Bharati", "10m Wind Speed", "0.814", "0.835", "Years 2024 - 2025"],
        ["Maitri", "2m Temperature", "0.899", "0.911", "Years 2025 - 2026"],
        ["Maitri", "10m Wind Speed", "0.767", "0.795", "Years 2025 - 2026"]
    ]
    
    t_metrics = Table(metrics_data, colWidths=[70, 110, 95, 115, 110])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2C3E50')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 15))
    
    # Page Break
    story.append(PageBreak())
    
    # Section 5: Remote Execution Guide
    story.append(Paragraph("5. Step-by-Step Remote Execution Guide", h1_style))
    story.append(Paragraph(
        "To migrate and run the model training and evaluation pipeline on a remote CPU server "
        "(e.g., Linux-based server), follow this checklist:", body_style
    ))
    
    story.append(Paragraph("<b>Step 5.1: Package and Compress the Repository</b>", h2_style))
    story.append(Paragraph(
        "Compress only the source code and configuration files. Do NOT include raw datasets, checkpoints, "
        "or virtual environments to minimize transfer size. Run this in your local command prompt:", body_style
    ))
    story.append(Paragraph(
        "tar --exclude='.venv' --exclude='data/raw/*.grib' --exclude='*.npy' -czf antarctica_forecast.tar.gz .",
        code_style
    ))
    
    story.append(Paragraph("<b>Step 5.2: Transfer Package to Remote Server</b>", h2_style))
    story.append(Paragraph("Use Secure Copy Protocol (SCP) to upload the archive to your target server:", body_style))
    story.append(Paragraph(
        "scp antarctica_forecast.tar.gz username@remote_host:/path/to/destination",
        code_style
    ))
    
    story.append(Paragraph("<b>Step 5.3: Extract and Set Up Environment</b>", h2_style))
    story.append(Paragraph("Connect to the remote host, extract the files, and set up a python virtual environment:", body_style))
    story.append(Paragraph(
        "ssh username@remote_host<br/>"
        "cd /path/to/destination<br/>"
        "tar -xzf antarctica_forecast.tar.gz<br/>"
        "python3 -m venv .venv<br/>"
        "source .venv/bin/activate<br/>"
        "pip install -r requirements.txt",
        code_style
    ))
    
    story.append(Paragraph("<b>Step 5.4: Execute the Training Pipeline</b>", h2_style))
    story.append(Paragraph(
        "To run the training sequentially under safe single-core CPU parameters, "
        "execute the following scripts in order:", body_style
    ))
    story.append(Paragraph(
        "# Preprocess raw GRIB data into Numpy arrays<br/>"
        "python3 src/preprocess_maitri_safe.py<br/><br/>"
        "# Train the base neural network on CPU (saves best checkpoint)<br/>"
        "python3 src/train.py<br/><br/>"
        "# Train bias-correction estimators on dynamic splits<br/>"
        "python3 src/train_bias_correction.py<br/><br/>"
        "# Generate out-of-sample visual validation dashboards<br/>"
        "python3 src/generate_dashboards.py",
        code_style
    ))
    
    print("Building PDF...")
    doc.build(story)
    print(f"PDF successfully created at: {pdf_path}")

if __name__ == "__main__":
    create_project_report()
