from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


source = Path("Figures/Figure_1_Machine_Sketch.pdf")
target = Path("Figures/Figure_1_Machine_Sketch.corrected.pdf")

reader = PdfReader(source)
page = reader.pages[0]
width = float(page.mediabox.width)
height = float(page.mediabox.height)

overlay_stream = BytesIO()
overlay = canvas.Canvas(overlay_stream, pagesize=(width, height))
overlay.setFillColorRGB(1, 1, 1)
overlay.rect(25, 148, 136, 24, fill=1, stroke=0)
overlay.setFillColorRGB(0, 0, 0)
overlay.setFont("Times-Roman", 13)
overlay.drawString(30, 156, "P")
overlay.setFont("Times-Roman", 9)
overlay.drawString(37, 153, "i")
overlay.setFont("Times-Roman", 13)
overlay.drawString(42, 156, ", Water injection")
overlay.save()

overlay_stream.seek(0)
page.merge_page(PdfReader(overlay_stream).pages[0])

writer = PdfWriter()
writer.add_page(page)
with target.open("wb") as output:
    writer.write(output)
