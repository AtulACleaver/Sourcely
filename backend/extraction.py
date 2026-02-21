import pdfplumber

# extract text from a pdf file
def extract_text(pdf_path: str) -> list[dict]:

    pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip()
                })
    return pages