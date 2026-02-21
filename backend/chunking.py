def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """split extracted pages into overlapping chunks for better retrieval."""
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