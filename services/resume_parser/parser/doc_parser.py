import docx
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from pdf_parser import parse_pdf

def docx_to_pdf(docx_path, pdf_path):
    doc = docx.Document(docx_path)
    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter

    for paragraph in doc.paragraphs:
        text = paragraph.text
        c.drawString(72, height - 72, text)
        height -= 14  # move to the next line

        if height < 72:  # new page if necessary
            c.showPage()
            height = letter[1]

    c.save()

    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())


def parse_doc(docx_path):
    pdf_path = docx_path.replace('.docx', '.pdf')
    
    docx_to_pdf(docx_path, pdf_path)
    
    text, links = parse_pdf(pdf_path)
    
    os.remove(pdf_path)

    print(links)
    
    return text, links
