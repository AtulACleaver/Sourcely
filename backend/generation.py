from embeddings import search_index

def retrieve_context(question: str, k: int = 5) -> list[dict]:
    results = search_index(question, k)
    return results