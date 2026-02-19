
"""
    Takes extracted pages and splits them into overlapping chunks.

    Args:
        pages: Output from extract_text() - list of {"page_number": int, "text": str}
        chunk_size: Max characters per chunk (default 500)
        overlap: Characters shared between consecutive chunks (default 100)

    Returns:
        List of chunk dicts, each with:
        - "chunk_id": int (unique, 0-indexed)
        - "text": str (the chunk content)
        - "page_number": int (which page this chunk came from)
        - "start_char": int (where in the page this chunk starts)
"""


def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    chunks = []
    chunk_id = 0

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text_content = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_content,
                "page_number": page_number,
                "start_char": start
            })

            chunk_id += 1
            start += chunk_size - overlap

    return chunks