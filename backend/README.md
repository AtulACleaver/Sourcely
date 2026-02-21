w# ⚙️ Sourcely Backend

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
   OLLAMA_BASE_URL=http://localhost:11434
   GENERATIONAL_MODEL=llama3
   ```

4. **run the server**:

   ```bash
   python main.py
   ```

## 🔍 requirements

- **ollama**: ensure ollama is running locally.
- **models**: pull the required models:

  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3
  ```

## 🔌 endpoints

- `POST /upload`: upload and index a pdf.
- `POST /query`: ask questions about indexed documents.
- `GET /status`: check the current index state.
