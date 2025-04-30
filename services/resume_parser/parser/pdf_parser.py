import fitz

def parse_pdf(file_path):
    import os
    print(f"[DEBUG] parse_pdf called with path: {file_path}")
    print(f"[DEBUG] os.path.exists(path): {os.path.exists(file_path)}")
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