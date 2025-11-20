from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import pandas as pd

def generate_pdf(data, filename="output.pdf"):
    """Generate PDF from table data"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('Header', parent=styles['Heading1'],
                                   fontSize=24, textColor=colors.HexColor('#1e293b'),
                                   spaceAfter=30, alignment=1, fontName='Helvetica-Bold')
    elements.append(Paragraph("💡 Tycoon Lights", header_style))
    
    # Subtitle
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=14, textColor=colors.HexColor('#475569'),
                                     spaceAfter=10, alignment=1)
    elements.append(Paragraph("Driver Calculation Report", subtitle_style))
    
    # Date
    date_style = ParagraphStyle('Date', parent=styles['Normal'],
                                 fontSize=10, textColor=colors.HexColor('#64748b'),
                                 spaceAfter=20, alignment=1, fontName='Helvetica-Oblique')
    date_text = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    elements.append(Paragraph(f"Generated on {date_text}", date_style))
    elements.append(Spacer(1, 20))
    
    # Table
    if data:
        df = pd.DataFrame(data)
        table_data = [df.columns.tolist()] + df.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total Items: {len(data)}", subtitle_style))
    else:
        empty_style = ParagraphStyle('Empty', parent=styles['Normal'],
                                      fontSize=12, textColor=colors.HexColor('#64748b'),
                                      alignment=1, fontName='Helvetica-Oblique')
        elements.append(Paragraph("No data available", empty_style))
    
    doc.build(elements)
    return filename

