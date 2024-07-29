from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
import os

class PdfGenerator:
    def __init__(self, destination: str, itinerary: dict,
                 budget_breakdown: list, travel_dates: str,
                 estimated_cost: str, city_of_residence: str, logo_path: str, regular_font: str, bold_font: str):
        self.destination = destination
        self.itinerary = itinerary
        self.budget_breakdown = budget_breakdown
        self.travel_dates = travel_dates
        self.estimated_cost = estimated_cost
        self.city_of_residence = city_of_residence
        self.logo_path = logo_path
        self.regular_font = regular_font
        self.bold_font = bold_font
    
    def generate_pdf(self):
        pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs")
        doc = SimpleDocTemplate(f"{pdf_path}/Travel_Itinerary_{self.destination}.pdf", pagesize=letter)
        elements = []

        # Register the Poppins font
        pdfmetrics.registerFont(TTFont('Poppins', self.regular_font))
        pdfmetrics.registerFont(TTFont('Poppins-Bold', self.bold_font))

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            fontName='Poppins-Bold',
            fontSize=24,
            textColor=colors.HexColor("#333333"),
            spaceAfter=14
        )
        subtitle_style = ParagraphStyle(
            'SubTitle',
            fontName='Poppins-Bold',
            fontSize=20,
            textColor=colors.HexColor("#666666"),
            spaceAfter=12
        )
        value_style = ParagraphStyle(
            'Value',
            fontName='Poppins',
            fontSize=12,
            textColor=colors.HexColor("#444444"),
            leading=15,
            leftIndent=20
        )
        normal_style = ParagraphStyle(
            'Normal',
            fontName='Poppins',
            fontSize=12,
            textColor=colors.HexColor("#444444"),
            leading=15
        )

        # Logo
        logo = Image(self.logo_path, width=1.5*inch, height=1.5*inch)
        elements.append(logo)
        elements.append(Spacer(1, 12))

        # Title
        elements.append(Paragraph(f"Travel Itinerary: {self.destination}", title_style))
        elements.append(Spacer(1, 12))

        # Travel Information
        elements.append(Paragraph("From:", subtitle_style))
        elements.append(Paragraph(f"{self.city_of_residence}", value_style))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("Travel Dates:", subtitle_style))
        elements.append(Paragraph(f"{self.travel_dates}", value_style))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("Estimated Cost:", subtitle_style))
        elements.append(Paragraph(f"{self.estimated_cost}", value_style))
        elements.append(Spacer(1, 12))

        # Itinerary Table
        elements.append(Paragraph("Itinerary", subtitle_style))
        elements.append(Spacer(1, 12))
        itinerary_data = [["Day", "Time of Day", "Activities"]]
        span_indices = []

        for i, (day, activities) in enumerate(self.itinerary.items()):
            row_index = len(itinerary_data)
            itinerary_data.extend([
                [day, "Morning", activities.get('Morning', [''])[0]],
                ['', "Afternoon", activities.get('Afternoon', [''])[0]],
                ['', "Evening", activities.get('Evening', [''])[0]]
            ])
            span_indices.append(row_index)  # Store the index for spanning the "Day" column

        itinerary_table = Table(itinerary_data, colWidths=[0.7*inch, 1.3*inch, 4*inch])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Poppins-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#333333")),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Poppins'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#4CAF50"))
        ])

        # Add SPAN for "Day" column dynamically
        for index in span_indices:
            table_style.add('SPAN', (0, index), (0, index+2))

        itinerary_table.setStyle(table_style)
        elements.append(itinerary_table)
        elements.append(Spacer(1, 12))


        # Budget Breakdown Table
        elements.append(Paragraph("Budget Breakdown", subtitle_style))
        elements.append(Spacer(1, 12))
        budget_data = [["Item", "Cost"]] + [i.split(": ") for i in self.budget_breakdown]
        budget_table = Table(budget_data, colWidths=[1.8*inch, 1.6*inch])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Poppins-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#333333")),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Poppins'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#4CAF50"))
        ]))
        elements.append(budget_table)

        # Build the PDF
        doc.build(elements)

        pdf_file_path = f"{pdf_path}/Travel_Itinerary_{self.destination}.pdf"
        return pdf_file_path
