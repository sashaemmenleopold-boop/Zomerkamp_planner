import io
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(dag_naam: str, berekende_blokken: List[Dict[str, Any]], notulen: Dict[str, str]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    # Titel
    elements.append(Paragraph(f"<b>Kamp Planning: {dag_naam}</b>", styles['Title']))
    elements.append(Spacer(1, 20))

    # Tabel Data opbouwen
    table_data = [["Tijd", "Wat & Details", "Wie"]]
    
    for blok in berekende_blokken:
        tijd_str = f"{blok['start']} - {blok['eind']}"
        wat_str = f"<b>{blok['activiteit']}</b><br/><i>{blok['details']}</i>"
        wie_str = ", ".join(blok['leiding'])
        
        table_data.append([
            Paragraph(tijd_str, styles['Normal']),
            Paragraph(wat_str, styles['Normal']),
            Paragraph(wie_str, styles['Normal'])
        ])

    # Tabel styling
    t = Table(table_data, colWidths=[80, 300, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 30))

   # Notulen sectie
    notulen_items = [
        ("Wat ging goed / Pluimen:", notulen.get('pluimen', '')),
        ("Aandachtspunten morgen:", notulen.get('morgen', '')),
        ("Kinderen / Situaties:", notulen.get('kinderen', '')),
        ("Avondritueel & Nachtverdeling:", notulen.get('nacht', '')),
    ]
    
    # Check of er überhaupt íéts is ingevuld
    heeft_notulen = any(inhoud.strip() for _, inhoud in notulen_items)
    
    if heeft_notulen:
        elements.append(Paragraph("<b>Notulen & Bespreking</b>", styles['Heading2']))
        for titel, inhoud in notulen_items:
            if inhoud.strip():  # Voegt dit blokje alleen toe als het niet leeg is
                elements.append(Paragraph(f"<b>{titel}</b>", styles['Heading3']))
                elements.append(Paragraph(inhoud, styles['Normal']))
                elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer
