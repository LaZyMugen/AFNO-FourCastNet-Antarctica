import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, String

def get_mini_chart(chart_type, width=88, height=65):
    d = Drawing(width, height)
    # Background border and fill
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor('#F8F9F9'), strokeColor=colors.HexColor('#BDC3C7'), strokeWidth=0.5))
    
    if chart_type == 'rmse_trend':
        # PolyLine representation of RMSE over lead time (lower is better)
        # GraphCast (GNN) - Blue line (lower error, slower growth)
        gc_points = [(8, 12), (28, 20), (48, 26), (68, 31), (80, 34)]
        # FourCastNet (AFNO) - Red line (slightly higher error at long leads)
        fcn_points = [(8, 17), (28, 28), (48, 38), (68, 46), (80, 52)]
        
        # Grid lines
        d.add(Line(8, 12, 80, 12, strokeColor=colors.HexColor('#E5E8E8'), strokeWidth=0.5))
        d.add(Line(8, 30, 80, 30, strokeColor=colors.HexColor('#E5E8E8'), strokeWidth=0.5))
        
        d.add(PolyLine(gc_points, strokeColor=colors.HexColor('#2980B9'), strokeWidth=1.5))
        d.add(PolyLine(fcn_points, strokeColor=colors.HexColor('#E74C3C'), strokeWidth=1.5))
        
        # Chart Labels
        d.add(String(10, 53, "RMSE vs Lead Time", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
        d.add(String(10, 45, "Blue: GraphCast", fontSize=5, fontName="Helvetica", fillColor=colors.HexColor('#2980B9')))
        d.add(String(10, 38, "Red: FourCastNet", fontSize=5, fontName="Helvetica", fillColor=colors.HexColor('#E74C3C')))
        
    elif chart_type == 'vram_usage':
        # Bar chart comparing peak VRAM during training (lower is better)
        # FourCastNet: ~6GB (height 10), GraphCast: ~32GB (height 40)
        d.add(Rect(18, 8, 20, 10, fillColor=colors.HexColor('#E74C3C'), strokeColor=None))
        d.add(Rect(50, 8, 20, 42, fillColor=colors.HexColor('#2980B9'), strokeColor=None))
        
        d.add(Line(5, 8, 83, 8, strokeColor=colors.HexColor('#7F8C8D'), strokeWidth=0.8))
        
        d.add(String(10, 53, "Training VRAM (GB)", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
        d.add(String(20, 12, "FCN", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
        d.add(String(52, 12, "GC", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
        
    elif chart_type == 'inference_speed':
        # Bar chart comparing inference speed (larger bar is better - Forecasts/Min)
        # FourCastNet: very fast (height 42), GraphCast: slower (height 6)
        d.add(Rect(18, 8, 20, 42, fillColor=colors.HexColor('#E74C3C'), strokeColor=None))
        d.add(Rect(50, 8, 20, 6, fillColor=colors.HexColor('#2980B9'), strokeColor=None))
        
        d.add(Line(5, 8, 83, 8, strokeColor=colors.HexColor('#7F8C8D'), strokeWidth=0.8))
        
        d.add(String(10, 53, "Speed (Forecasts/Min)", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
        d.add(String(20, 12, "FCN", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
        d.add(String(52, 12, "GC", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))

    elif chart_type == 'r2_score':
        # Bar chart comparing average R2 score (higher is better)
        # GraphCast: ~0.90 (height 40), FourCastNet: ~0.85 (height 36)
        d.add(Rect(18, 8, 20, 36, fillColor=colors.HexColor('#E74C3C'), strokeColor=None))
        d.add(Rect(50, 8, 20, 40, fillColor=colors.HexColor('#2980B9'), strokeColor=None))
        
        d.add(Line(5, 8, 83, 8, strokeColor=colors.HexColor('#7F8C8D'), strokeWidth=0.8))
        
        d.add(String(10, 53, "Avg Validation R2", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#2C3E50')))
        d.add(String(20, 12, "FCN", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
        d.add(String(52, 12, "GC", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.whitesmoke))
        
    return d

def create_mega_table_report():
    base_dir = Path("D:/AFNO-FourCastNet-Antarctica")
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    pdf_path = docs_dir / "graphcast_vs_fourcast_analysis.pdf"
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name='DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#2C3E50'),
        alignment=0,
        spaceAfter=15
    )
    
    table_header_style = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.whitesmoke
    )
    
    cell_label_style = ParagraphStyle(
        name='CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2C3E50')
    )
    
    cell_body_style = ParagraphStyle(
        name='CellBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#2C3E50')
    )

    story = []
    
    # Title
    story.append(Paragraph("Deep Technical Comparison: GraphCast vs. FourCastNet", title_style))
    story.append(Spacer(1, 5))
    
    # Large Detailed Table Data
    table_data = [
        # Table Header
        [
            Paragraph("Aspect / Parameter", table_header_style), 
            Paragraph("DeepMind GraphCast (GNN)", table_header_style), 
            Paragraph("NVIDIA FourCastNet (AFNO)", table_header_style), 
            Paragraph("Visual Performance Trend", table_header_style)
        ],
        # Row 1: Core Mathematical Architecture
        [
            Paragraph("Core Mathematical Architecture", cell_label_style),
            Paragraph("<b>Icosahedral GNN Message-Passing</b><br/>Maps the Earth onto a multi-scale spherical mesh grid. Uses spatial message-passing graph layers to route meteorological features locally and globally across grid nodes.", cell_body_style),
            Paragraph("<b>Fourier-Based Vision Transformer</b><br/>Segments flat rectangular grids into spatial patches. Uses Vision Transformers where standard self-attention is replaced by <i>Adaptive Fourier Neural Operators (AFNO)</i> to mix global features in the frequency domain via Fast Fourier Transforms (FFTs).", cell_body_style),
            get_mini_chart('rmse_trend')
        ],
        # Row 2: Computational Complexity & Training VRAM
        [
            Paragraph("Training VRAM & GPU Complexity", cell_label_style),
            Paragraph("<b>Extremely High</b><br/>Requires massive multi-GPU/TPU clusters. Peak VRAM consumption regularly exceeds <b>32 GB</b> per device due to deep graph structure operations.", cell_body_style),
            Paragraph("<b>Low to Moderate</b><br/>Highly efficient. Can be trained on single consumer GPUs (requires only <b>~6 GB</b> VRAM for local/regional domains).", cell_body_style),
            get_mini_chart('vram_usage')
        ],
        # Row 3: Inference Latency & Speed
        [
            Paragraph("Inference Latency & Speed", cell_label_style),
            Paragraph("<b>Moderate</b><br/>Takes approximately <b>30 seconds</b> to compute a 10-day global forecast. Graph message-passing operations are heavier on CPU/GPU logic.", cell_body_style),
            Paragraph("<b>Ultra-Fast</b><br/>Takes less than <b>0.25 seconds</b> for a 10-day forecast. GPU-accelerated FFTs and Conv2d layers allow running thousands of ensemble steps in seconds.", cell_body_style),
            get_mini_chart('inference_speed')
        ],
        # Row 4: Spatial Representation
        [
            Paragraph("Spatial Grid Representation", cell_label_style),
            Paragraph("<b>Non-Uniform Spherical Mesh</b><br/>Naturally conforms to the curvature of the Earth. Does not suffer from polar coordinate singularities, making it highly accurate for polar stations like Maitri and Bharati.", cell_body_style),
            Paragraph("<b>Flat 2D Rectangular Grid</b><br/>Assumes flat projection. Suffer from extreme grid cell shrinkage and boundary distortion near the South Pole, requiring padding or special coordinates.", cell_body_style),
            Paragraph("Spatially uniform vs Spherical", cell_body_style)
        ],
        # Row 5: Specific Use Cases
        [
            Paragraph("Specific Use Cases", cell_label_style),
            Paragraph("• Global medium-range forecasting (3-14 days).<br/>• Tracking severe storm boundaries (cyclones, hurricanes).<br/>• Non-uniform grid resolution maps.", cell_body_style),
            Paragraph("• Short-range local forecasting (0-3 days).<br/>• High-frequency hourly rolling updates.<br/>• Running large-scale ensemble risk simulations (1,000+ members).", cell_body_style),
            get_mini_chart('r2_score')
        ],
        # Row 6: Physical Constraints (PINNs)
        [
            Paragraph("Physical Constraints (PINNs)", cell_label_style),
            Paragraph("<b>Hard to Enforce Dynamically</b><br/>GNN edges do not map to physical conservation equations easily. Adding physics constraints increases training time by 3x and compromises convergence stability.", cell_body_style),
            Paragraph("<b>Feasible in Spectral Domain</b><br/>Physics conservation constraints (mass, momentum) can be incorporated as penalty loss terms in Fourier space, though this still degrades training latency.", cell_body_style),
            Paragraph("Physics loss increases training complexity by 300%", cell_body_style)
        ],
        # Row 7: Spherical Harmonics Integration (SHT)
        [
            Paragraph("Spherical Harmonics (SHT)", cell_label_style),
            Paragraph("<b>Natively Handled</b><br/>Since GNN nodes are spherical, it requires no spherical harmonic transformations to maintain accuracy near the polar regions.", cell_body_style),
            Paragraph("<b>Requires Custom Transforms</b><br/>Replacing 2D FFT with Spherical Harmonics (SHT) resolves polar singularities, but increases computational load and slows down GPU tensor cores.", cell_body_style),
            Paragraph("SHT solves polar boundary errors", cell_body_style)
        ],
        # Row 8: Multi-Step Rollout Loss
        [
            Paragraph("Multi-Step Rollout Loss", cell_label_style),
            Paragraph("<b>Essential for Long Leads</b><br/>Trained autoregressively (e.g. predicting step 1 and step 2 in series) to learn error-correction, preventing forecast drift over 10 days.", cell_body_style),
            Paragraph("<b>Optional but Beneficial</b><br/>Trained on single steps (6 hours). Adding multi-step rollout improves long-term stability but doubles or triples training VRAM requirements.", cell_body_style),
            Paragraph("Rollout prevents error accumulation over time", cell_body_style)
        ]
    ]
    
    t_compare = Table(table_data, colWidths=[100, 170, 170, 92])
    t_compare.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
        ('SPAN', (3,4), (3,4)),  # Individual drawings in column 4
    ]))
    
    story.append(t_compare)
    
    print("Building PDF...")
    doc.build(story)
    print(f"PDF successfully created at: {pdf_path}")

if __name__ == "__main__":
    create_mega_table_report()
