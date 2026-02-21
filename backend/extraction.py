import pdfplumber


def extract_text(pdf_stream) -> list[dict]:
    """Extract text from a PDF file-like object (e.g. BytesIO)."""
    pages = []
    with pdfplumber.open(pdf_stream) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip()
                })
    return pages
