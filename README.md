# 📄 Sourcely - RAG-Powered PDF Research Assistant

An AI-powered research assistant that allows users to upload PDF documents and ask questions about their content. Sourcely uses Retrieval-Augmented Generation (RAG) to provide accurate answers with direct citations from the uploaded source.

![Sourcely](https://img.shields.io/badge/Sourcely-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-19-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green)
![FAISS](https://img.shields.io/badge/FAISS-1.13.2-yellow)

## ✨ Features

- **📂 smart parsing**: extract text from pdf documents.
- **🔍 vector search**: high-performance document retrieval using faiss.
- **💬 ai answers**: answers questions using local ollama models.
- **📍 citations**: provides source citations for every answer.

## 🏗️ Architecture Overview

```mermaid
flowchart TB
    subgraph Frontend["React + Vite (Port 5173)"]
        A["FileUpload.jsx"] --> B["api/client.js (Axios)"]
        C["ChatInput.jsx"] --> B
        B --> D["AnswerDisplay.jsx"]
    end
    
    subgraph Backend["FastAPI (Port 8000)"]
        E["/upload endpoint"] --> F["extraction.py"]
        F --> G["chunking.py"]
        G --> H["embeddings.py"]
        I["/query endpoint"] --> J["FAISS Search"]
        J --> K["Prompt Builder"]
        K --> L["LLM Generation"]
    end
    
    subgraph Storage["Local Storage"]
        M["uploads/ (PDFs)"]
        N["vector_store/ (FAISS + JSON)"]
    end
    
    subgraph Models["AI Models"]
        O["Ollama: nomic-embed-text"]
        P["Ollama: llama3"]
        Q["OpenAI (optional upgrade)"]
    end
    
    B -->|"HTTP requests"| E
    B -->|"HTTP requests"| I
    H --> N
    H --> O
    L --> P
    L -.->|"later"| Q
    E --> M
    J --> N
```

## 🚀 Getting Started

The project is split into two main parts. Follow the instructions in each directory:

- [Backend Setup](./backend/README.md) - python, fastapi, and ollama.
- [Frontend Setup](./frontend/README.md) - react, vite, and tailwind.

## 💻 Tech Stack

- **backend**: fastapi, pdfminer, faiss, langchain.
- **frontend**: react 19, vite, tailwind css, axios.
- **llm**: local inference powered by ollama.

## 💡 Troubleshooting

- **PDF Extraction Failed**: Ensure the PDF is not password-protected or purely image-based (OCR not currently supported).
- **Ollama Connection Error**: Verify that Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3`).
- **Memory Issues**: Large PDFs may require significant RAM for embedding generation.

## 📝 License

MIT License - feel free to use and modify!

---

**Note**: This project is designed for local research and document analysis. Ensure you have the rights to the documents you upload.
