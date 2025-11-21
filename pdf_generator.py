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
    elements.append(Paragraph("Tycoon Lights", header_style))
    
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
        
        # Calculate total price
        total_price = 0
        price_col_idx = None
        
        # Find Price column index
        if 'Price' in df.columns:
            price_col_idx = df.columns.get_loc('Price')
            for row in data:
                price_value = row.get('Price', 0)
                if isinstance(price_value, (int, float)):
                    total_price += price_value
                elif price_value and price_value != '-':
                    try:
                        price_str = str(price_value).replace('₹', '').replace(',', '').strip()
                        total_price += float(price_str)
                    except (ValueError, AttributeError):
                        pass
        
        # Build table data with total row
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Add total row
        total_row = [''] * len(df.columns)
        total_row[0] = 'Total'
        if price_col_idx is not None:
            total_display = f"{total_price:,.2f}".rstrip('0').rstrip('.')
            total_row[price_col_idx] = total_display
        
        table_data.append(total_row)
        
        table = Table(table_data)
        total_row_idx = len(table_data) - 1
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, total_row_idx - 1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, total_row_idx - 1), colors.HexColor('#1e293b')),
            ('FONTSIZE', (0, 1), (-1, total_row_idx - 1), 9),
            # Total row styling
            ('BACKGROUND', (0, total_row_idx), (-1, total_row_idx), colors.HexColor('#fbbf24')),
            ('TEXTCOLOR', (0, total_row_idx), (-1, total_row_idx), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, total_row_idx), (-1, total_row_idx), 'Helvetica-Bold'),
            ('FONTSIZE', (0, total_row_idx), (-1, total_row_idx), 10),
            ('BOTTOMPADDING', (0, total_row_idx), (-1, total_row_idx), 12),
            ('TOPPADDING', (0, total_row_idx), (-1, total_row_idx), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, total_row_idx - 1), [colors.white, colors.HexColor('#f1f5f9')]),
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

