# backend/embeddings.py

import requests
import numpy as np
import faiss
import json
import os
import logging

logger = logging.getLogger(__name__)


# --- Directory for storing the FAISS index and chunk metadata ---
VECTOR_STORE_DIR = "vector_store"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(VECTOR_STORE_DIR, "chunks.json")



# Sends text to Ollama's local API and gets back an embedding vector.

# Args:
#     text: Any string you want to embed
#     prefix: Task prefix required by nomic-embed-text.
#             Use "search_document: " when embedding chunks (documents).
#             Use "search_query: " when embedding questions (queries).
#             Without these prefixes, all embeddings will be nearly identical
#             and FAISS will just return chunks in order (0, 1, 2...).

# Returns:
#     A list of floats (the embedding vector, 768 dimensions for nomic-embed-text)

def get_embedding(text: str, prefix: str = "") -> list[float]:

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


    # Takes a list of text chunks, embeds each one, and stores them in FAISS.

    # This function does 3 things:
    # 1. Calls get_embedding() on every chunk's text (with "search_document: " prefix)
    # 2. Builds a FAISS index from all the embeddings
    # 3. Saves the index and chunk metadata to disk

    # Args:
    #     chunks: Output from chunk_text() - list of dicts with "chunk_id", "text", etc.

    # Returns:
    #     Tuple of (faiss_index, chunks_with_embeddings)


def build_index(chunks: list[dict]) -> tuple:
    
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

    # Create the FAISS index
    # IndexFlatL2 = brute force search using L2 (Euclidean) distance
    # "Flat" means it checks every single vector. Fast enough for thousands of chunks.
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    print(f"  FAISS index built with {index.ntotal} vectors")

    # Save FAISS index to disk
    faiss.write_index(index, INDEX_PATH)

    # Save chunk metadata to disk (we need this to map search results back to text)
    # NOTE: We do NOT save the embeddings in chunks.json - they're in the FAISS index
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"  Saved index to {INDEX_PATH}")
    print(f"  Saved chunk metadata to {CHUNKS_PATH}")

    return index, chunks


def load_index() -> tuple:
    """
    Loads a previously saved FAISS index and chunk metadata from disk.

    Returns:
        Tuple of (faiss_index, chunks) or (None, None) if no index exists
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        return None, None

    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    return index, chunks


# Searches the FAISS index for chunks most similar to the query.

# Args:
#     query: The question/search text
#     k: Number of results to return (default 5)

# Returns:
#     List of dicts with chunk data + similarity distance

def search_index(query: str, k: int = 5) -> list[dict]:
    
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