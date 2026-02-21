from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback
from dotenv import load_dotenv

load_dotenv()

from extraction import extract_text
from chunking import chunk_text
from embeddings import build_index, get_embedding
from generation import ask_question_with_chunks
from session_store import create_session, get_session, cleanup_sessions

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Sourcely API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sourcely-rag.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"message": "Sourcely is running!!"}


@app.get("/status")
def status(session_id: str = ""):
    if not session_id:
        return {"index_loaded": False, "num_chunks": 0}
    session = get_session(session_id)
    if not session or not session.index:
        return {"index_loaded": False, "num_chunks": 0}
    return {
        "index_loaded": True,
        "num_chunks": len(session.chunks)
    }


@app.post("/session")
def new_session():
    cleanup_sessions()
    sid = create_session()
    return {"session_id": sid}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = ""):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed!!")

    try:
        contents = await file.read()
        pdf_stream = BytesIO(contents)
        pages = extract_text(pdf_stream)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No text found in the PDF. This pdf might be scanned/image pdf!"
            )

        logger.info(f"Chunking {len(pages)} pages")
        chunks = chunk_text(pages, chunk_size=500, overlap=100)

        logger.info(f"Building index for {len(chunks)} chunks")
        index = build_index(chunks)

        session.chunks = chunks
        session.index = index
        session.filename = file.filename

        return {
            "filename": file.filename,
            "num_chunks": len(chunks),
            "num_pages_extracted": len(pages),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during /upload: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/query")
def search(question: str, session_id: str = "", k: int = 5):
    session = get_session(session_id)
    if not session or not session.index:
        raise HTTPException(
            status_code=404,
            detail="No document loaded. Upload a PDF first."
        )

    try:
        query_emb = np.array([get_embedding(question)]).astype("float32")
        distances, indices = session.index.search(query_emb, k)
        results = [
            session.chunks[idx] for idx in indices[0]
            if 0 <= idx < len(session.chunks)
        ]

        result = ask_question_with_chunks(question, results)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

    return {
        "question": question,
        "answer": result["answer"],
        "citations": result["citations"],
        "retrieved_chunks": result["retrieved_chunks"]
    }
