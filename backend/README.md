# ⚙️ Sourcely Backend

FastAPI server for document processing and RAG-based questioning.

## 🚀 Setup

1. **python environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # on windows: venv\Scripts\activate
   ```

2. **install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **configure environment**:

   Create a `.env` file:

    ```env
    MISTRAL_API_KEY=your_mistral_api_key_here
    GROQ_API_KEY=your_groq_api_key_here
    ```

4. **run the server**:

   ```bash
   python main.py
   ```

## 🔍 requirements

- **mistral api**: you need a valid `MISTRAL_API_KEY` for embeddings.
- **groq api**: you need a valid `GROQ_API_KEY` for generation.
- **models**: 
  - Embeddings: `mistral-embed` (handled via API)
  - Generation: `llama-3.3-70b-versatile` (handled via Groq API)

## 🔌 endpoints

- `POST /session`: create a new session; returns `session_id`. Use this on app load.
- `POST /upload`: upload and index a PDF (query param: `session_id`). No disk write; state is in memory per session.
- `POST /query`: ask questions about the document for the given session (query params: `question`, `session_id`).
- `GET /status`: optional `session_id` for per-session index state.
- `GET /health`: health check.

## 📁 Project Structure

```text
backend/
├── main.py             # fastapi entry point & routes
├── session_store.py    # in-memory session state (chunks, FAISS index)
├── extraction.py       # pdf text extraction (stream-based)
├── chunking.py         # text segmentation strategies
├── embeddings.py       # embeddings & in-memory FAISS index build
├── generation.py       # rag logic & llm interaction
├── requirements.txt    # python dependencies
└── .env                # environment variables (local only)
```
