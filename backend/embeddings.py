import requests
import numpy as np
import faiss
import json
import os
import logging

logger = logging.getLogger(__name__)


# store index and metadata locally
VECTOR_STORE_DIR = "vector_store"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(VECTOR_STORE_DIR, "chunks.json")



def get_embedding(text: str, prefix: str = "") -> list[float]:
    """get vector embedding from ollama with the required prefix."""

    logger.info(f"Getting embedding for text (prefix: {prefix})")
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": prefix + text
        }
    )
    if response.status_code != 200:
        logger.error(f"Ollama API error: {response.status_code} - {response.text}")
    response.raise_for_status()  # Raises an error if Ollama isn't running
    return response.json()["embedding"]


def build_index(chunks: list[dict]) -> tuple:
    """build and save a faiss index for the given chunks."""
    
    print(f"Embedding {len(chunks)} chunks... This may take a minute.")

    embeddings = []
    for i, chunk in enumerate(chunks):
        # IMPORTANT: "search_document: " prefix tells nomic this is a document chunk
        emb = get_embedding(chunk["text"], prefix="search_document: ")
        embeddings.append(emb)

        # Progress indicator (prints to your terminal)
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Embedded {i + 1}/{len(chunks)} chunks")

    # Convert to numpy array (FAISS requires float32)
    embedding_matrix = np.array(embeddings).astype("float32")

    # Get the dimension (number of floats per embedding)
    dimension = embedding_matrix.shape[1]
    print(f"  Embedding dimension: {dimension}")

    # brute force search using l2 distance
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    print(f"  FAISS index built with {index.ntotal} vectors")

    # Save FAISS index to disk
    faiss.write_index(index, INDEX_PATH)

    # save metadata to map results back to text
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"  Saved index to {INDEX_PATH}")
    print(f"  Saved chunk metadata to {CHUNKS_PATH}")

    return index, chunks


def load_index() -> tuple:
    """load index and metadata from disk."""

    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        return None, None

    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    return index, chunks


def search_index(query: str, k: int = 5) -> list[dict]:
    """find the k most similar chunks for a query."""
    
    index, chunks = load_index()

    if index is None:
        return []

    # IMPORTANT: "search_query: " prefix tells nomic this is a search query
    query_embedding = np.array([get_embedding(query, prefix="search_query: ")]).astype("float32")

    # Search FAISS - returns distances and indices of closest vectors
    distances, indices = index.search(query_embedding, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):  # Safety check
            result = {
                "chunk_id": chunks[idx]["chunk_id"],
                "text": chunks[idx]["text"],
                "page_number": chunks[idx]["page_number"],
                "distance": float(distances[0][i])  # Lower = more similar
            }
            results.append(result)

    return results