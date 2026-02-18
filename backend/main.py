from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from extraction import extract_text


app = FastAPI(title="Sourcely API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# if pdf is not created, create it
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {"message": "Sourcely is running!!"}


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
    # Check if the file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed!!")
    
    # Save the PDF file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = extract_text(file_path)

    if not pages:
        raise HTTPException(
            status_code=400,
            detail="No text found in the PDF. This pdf might be scanned/image pdf!"
        )
    
    return {"filename": file.filename,
            "status": "uploaded",
            "num_pages_extracted": len(pages),
            "preview": pages[0]["text"][:500],
            "pages": pages
    }