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

- `POST /upload`: upload and index a pdf.
- `POST /query`: ask questions about indexed documents.
- `GET /status`: check the current index state.

## 📁 Project Structure

```text
backend/
├── main.py             # fastapi entry point & routes
├── extraction.py       # pdf text extraction logic
├── chunking.py         # text segmentation strategies
├── embeddings.py       # faiss index & embedding utilities
├── generation.py       # rag logic & llm interaction
├── requirements.txt    # python dependencies
├── .env                # environment variables (local only)
├── uploads/            # temporary storage for pdfs
└── vector_store/       # faiss index & chunk metadata
```
