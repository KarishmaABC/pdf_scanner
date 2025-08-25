import io
import os
import uuid
from typing import List
from . import config 

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from fastapi import HTTPException

from .schemas import ChatRequest, UploadResponse
from .chunker import chunk_text
from .rag import upsert_embeddings, similarity_search, answer_with_context

app = FastAPI(title="PDF RAG Chat (Gemini)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    # Read PDF bytes
    pdf_bytes = await file.read()
    try:
        pdf = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    page_texts = []
    for i, page in enumerate(pdf.pages):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        page_texts.append((i+1, t))

    if not any(t for _, t in page_texts):
        raise HTTPException(status_code=400, detail="No extractable text found in this PDF.")

    # Create a new doc_id per upload
    doc_id = uuid.uuid4().hex

    # Chunk + embed per page to handle very large PDFs
    total_chunks = 0
    chunks = []
    metas = []
    for page_no, text in page_texts:
        if not text.strip():
            continue
        page_chunks = chunk_text(text, chunk_size=2000, overlap=200)
        for c in page_chunks:
            chunks.append(c)
            metas.append({"page": page_no})
        total_chunks += len(page_chunks)

    if total_chunks == 0:
        raise HTTPException(status_code=400, detail="PDF has no usable text after chunking.")

    # Upsert into vector store
    upsert_embeddings(doc_id, chunks, metas)

    return UploadResponse(doc_id=doc_id, page_count=len(page_texts), chunks=total_chunks)

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        hits = similarity_search(req.doc_id, req.question, k=4)
        answer = answer_with_context(req.question, hits)
        return {
            "answer": answer,
            "citations": [{"page": h.get("meta", {}).get("page"), "id": h["id"]} for h in hits],
        }
    except Exception as e:
        # If it's our 429-style message, use 429; else 500
        msg = str(e)
        status = 429 if "free-tier" in msg.lower() or "rate" in msg.lower() else 500
        raise HTTPException(status_code=status, detail=f"Chat failed: {msg}")

