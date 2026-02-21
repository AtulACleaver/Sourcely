import numpy as np
import faiss
import os
import logging
from mistralai import Mistral
from dotenv import load_dotenv


load_dotenv()

mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
logger = logging.getLogger(__name__)


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


def build_index(chunks: list[dict]) -> faiss.Index:
    """Build a FAISS index for the given chunks. No disk write."""
    logger.info(f"Embedding {len(chunks)} chunks...")
    embeddings = []
    batch_size = 50

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_texts = [c["text"] for c in batch]
        batch_embeddings = get_embeddings(batch_texts)
        embeddings.extend(batch_embeddings)

    matrix = np.array(embeddings).astype("float32")
    dimension = matrix.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(matrix)
    logger.info(f"FAISS index built with {index.ntotal} vectors")
    return index
