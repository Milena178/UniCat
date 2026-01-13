from io import BytesIO
from reportlab.pdfgen import canvas

def generate_produkt_pdf(produkt):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 800, f"Produkt: {produkt.name}")
    p.drawString(100, 780, f"Beschreibung: {produkt.beschreibung}")
    p.drawString(100, 760, f"Mindestpreis: {produkt.mindestpreis} €")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer