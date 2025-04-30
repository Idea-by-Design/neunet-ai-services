import docx
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import fitz

def docx_to_pdf(docx_path, pdf_path):
    import os
    print(f"[DEBUG] docx_to_pdf called with docx_path: {docx_path}")
    print(f"[DEBUG] os.path.exists(docx_path): {os.path.exists(docx_path)}")
    print(f"[DEBUG] Intended pdf_path: {pdf_path}")
    try:
        doc = docx.Document(docx_path)
    except Exception as e:
        print(f"[DEBUG] ERROR opening docx_path: {e}")
        raise
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
    print(f"[DEBUG] PDF written to: {pdf_path}, exists after write: {os.path.exists(pdf_path)}")


def parse_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    links = []
    for _, page in enumerate(doc):
        text += page.get_text()
        link_dicts = page.get_links()
        for link in link_dicts:
            rect = fitz.Rect(link["from"])
            # Get the text corresponding to the hyperlink area
            link_text = page.get_text("text", clip=rect)
            link_info = {
                "link_text": link_text.strip(),
                "link": link.get("uri") or link.get("file", "")
            }
            links.append(link_info)
    doc.close()

    return text, links


def parse_doc(docx_path):
    import os
    print(f"[DEBUG] parse_doc called with docx_path: {docx_path}")
    print(f"[DEBUG] os.path.exists(docx_path): {os.path.exists(docx_path)}")
    pdf_path = docx_path.replace('.docx', '.pdf')
    
    docx_to_pdf(docx_path, pdf_path)
    
    text, links = parse_pdf(pdf_path)
    
    os.remove(pdf_path)

    print(links)
    
    return text, links
