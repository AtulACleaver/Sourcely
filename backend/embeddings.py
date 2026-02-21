import numpy as np
import faiss
import json
import os
import logging
from mistralai import Mistral
from dotenv import load_dotenv


load_dotenv()

# Initialize Mistral client
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

logger = logging.getLogger(__name__)


# store index and metadata locally
VECTOR_STORE_DIR = "vector_store"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(VECTOR_STORE_DIR, "chunks.json")



def get_embedding(text: str) -> list[float]:
    """Get vector embedding for a single text."""
    return get_embeddings([text])[0]


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get vector embeddings for a list of texts (batch processing)."""
    logger.info(f"Getting embeddings for batch of {len(texts)} texts")
    try:
        response = mistral_client.embeddings.create(
            model="mistral-embed",
            inputs=texts
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Mistral API error: {str(e)}")
        raise


def build_index(chunks: list[dict]) -> tuple:
    """build and save a faiss index for the given chunks."""
    
    print(f"Embedding {len(chunks)} chunks... This may take a minute.")

    embeddings = []
    batch_size = 50  # Mistral supports up to 128 inputs per request
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_texts = [chunk["text"] for chunk in batch]
        
        print(f"  Embedding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
        batch_embeddings = get_embeddings(batch_texts)
        embeddings.extend(batch_embeddings)

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

    # get query embedding
    query_embedding = np.array([get_embedding(query)]).astype("float32")

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