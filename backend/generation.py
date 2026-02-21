import requests
from embeddings import search_index
import os
from dotenv import load_dotenv
import re

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip().strip('"').strip("'")
GENERATIONAL_MODEL = os.getenv("GENERATIONAL_MODEL", "mistral").strip().strip('"').strip("'")


def retrieve_context(question: str, k: int = 5) -> list[dict]:
    results = search_index(question, k)
    return results


def build_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[Chunk {chunk['chunk_id']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""You are a document Q&A assistant. Your job is to answer questions based ONLY on the provided document excerpts.

    RULES (follow these strictly):
    1. ONLY use information from the context below. Do not use any outside knowledge.
    2. If the answer is not in the context, respond with exactly: "Not found in document."
    3. Cite your sources by including [Chunk X] after each claim, where X is the chunk_id.
    4. Be concise and direct. No filler.
    5. If the answer spans multiple chunks, cite all relevant ones.

    CONTEXT (document excerpts):
    {context}

    QUESTION: {question}

    ANSWER:"""

    return prompt

def generate_answer(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": GENERATIONAL_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2 # lower temperature for more focused answers
                }
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"]
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Can't connect to Ollama. Check server running!!"
        )
    except KeyError:
        raise Exception(
            f"Unexpected response from Ollama: {response.text[:200]}"
        )

def parse_citations(answer: str, chunks: list[dict]) -> list[dict]:
    cited_ids_raw = re.findall(r'\[Chunk (\d+)\]', answer)
    cited_ids = list(set(int(cid) for cid in cited_ids_raw))

    citations = []
    for cid in cited_ids:
        for chunk in chunks:
            if chunk["chunk_id"] == cid:
                citations.append({
                    "chunk_id": cid,
                    "page_number": chunk["page_number"],
                    "excerpt": chunk["text"][:150]
                })
                break

    citations.sort(key=lambda c: c["chunk_id"])

    return citations

def ask_question(question: str, k: int = 5) -> dict:
    """the full rag pipeline: retrieve, prompt, generate, and parse."""
    retrieved = retrieve_context(question, k=k)

    if not retrieved:
        return {
            "answer": "No documents have been indexed yet. Upload a PDF File",
            "retrieved_chunks": []
        }

    prompt = build_prompt(question, retrieved)
    answer = generate_answer(prompt)
    citations = parse_citations(answer, retrieved)

    return {
        "answer": answer,
        "citations": citations,
        "retrieved_chunks": retrieved
    }ww