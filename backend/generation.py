from embeddings import search_index
import os
from dotenv import load_dotenv
import re
from groq import Groq


load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def retrieve_context(question: str, session_id: str, k: int = 5) -> list[dict]:
    results = search_index(question, session_id, k)
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
    """Generate an answer using Groq's mistral-saba-24b model."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

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

def ask_question(question: str, session_id: str, k: int = 5) -> dict:
    """the full rag pipeline: retrieve, prompt, generate, and parse."""
    retrieved = retrieve_context(question, session_id, k=k)

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
    }