from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging
import traceback
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# internal modules
from extraction import extract_text
from chunking import chunk_text
from embeddings import build_index, load_index
from generation import ask_question


# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI(title="Sourcely API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sourcely-rag.vercel.app/"  # add after deploying frontend
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# if pdf is not created, create it
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {"message": "Sourcely is running!!"}

@app.get("/status")
def status():    
    index, chunks = load_index()
    return {
        "index_loaded": index is not None,
        "num_chunks": len(chunks) if chunks else 0
    }

# workflow
"""
1. Upload PDF
2. Extract text from PDF
3. Chunk text into smaller chunks
4. Generate embeddings for each chunk
5. Store embeddings in ChromaDB
6. Search for relevant chunks based on query
7. Generate response based on relevant chunks
"""

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Check if the file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed!!")
        
        # Save the PDF file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        logger.info(f"Saving uploaded file to {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Extracting text from {file_path}")
        pages = extract_text(file_path)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No text found in the PDF. This pdf might be scanned/image pdf!"
            )

        # chunking the text
        logger.info(f"Chunking {len(pages)} pages")
        chunks = chunk_text(pages, chunk_size=500, overlap=100)

        #  Embed and store in FAISS
        logger.info(f"Building index for {len(chunks)} chunks")
        build_index(chunks)
        
        return {"filename": file.filename,
                "status": "uploaded & chunked",
                "num_pages_extracted": len(pages),
                "num_chunks": len(chunks),
                "sample_chunks": chunks[:3], # checking frst 3 chunks
                "preview": pages[0]["text"][:500],
        }
    except HTTPException as he:
        # Re-raise HTTPExceptions as-is
        raise he
    except Exception as e:
        logger.error(f"Error during /upload: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/query")
def search(question: str, k: int = 5):
    
    index, chunks = load_index()

    if index is None:
        raise HTTPException(
            status_code=404,
            detail="No index found. Upload a PDF first."
        )

    try:
        result = ask_question(question, k=k)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )

    return {
        "question": question,
        "answer": result["answer"],
        "citations": result["citations"],
        "retrieved_chunks": result["retrieved_chunks"]
    }