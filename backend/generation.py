import os
from dotenv import load_dotenv
import re
from groq import Groq


load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[Chunk {chunk['chunk_id']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""Act like a senior AI systems engineer and expert in retrieval-augmented generation (RAG) systems specializing in grounded document question-answering.

Your goal is to generate strictly grounded answers to user questions using ONLY the provided document excerpts.

Task: Answer the QUESTION using exclusively the information contained in the CONTEXT.

Requirements:

1) Source Restriction  
- Use ONLY the provided CONTEXT.  
- Do NOT use prior knowledge, assumptions, or external information.  
- If the answer cannot be fully supported by the CONTEXT, respond with exactly:  
  Not found in document.

2) Grounded Claims  
- Every factual claim must be explicitly supported by the CONTEXT.  
- After each claim or sentence containing factual information, include a citation in this format:  
  [Chunk X]  
  where X is the exact chunk_id from the relevant excerpt.  
- If multiple chunks support the same claim, cite all relevant chunk IDs (e.g., [Chunk 2][Chunk 5]).  

3) No Hallucination Policy  
- Do not infer beyond what is written.  
- Do not reinterpret loosely.  
- Do not fill gaps with logical guesses.  
- If information is partial or ambiguous in the CONTEXT, state only what is explicitly supported.

4) Precision & Style  
- Be concise, direct, and factual.  
- No filler, no introductions, no summaries.  
- Do not restate the question.  
- Do not add commentary or meta-explanations.

5) Multi-Chunk Synthesis  
- If the answer spans multiple chunks, combine the information into a coherent response while citing each relevant chunk.

Context:
{context}

Question:
{question}

Answer:
Take a deep breath and work on this problem step-by-step."""

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

def ask_question_with_chunks(question: str, retrieved_chunks: list[dict]) -> dict:
    """RAG pipeline using pre-retrieved chunks: prompt, generate, parse."""
    if not retrieved_chunks:
        return {
            "answer": "No documents have been indexed yet. Upload a PDF first.",
            "retrieved_chunks": [],
            "citations": []
        }
    prompt = build_prompt(question, retrieved_chunks)
    answer = generate_answer(prompt)
    citations = parse_citations(answer, retrieved_chunks)
    return {
        "answer": answer,
        "citations": citations,
        "retrieved_chunks": retrieved_chunks
    }