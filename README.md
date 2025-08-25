# PDF Q&A (RAG) — Gemini Free API

End-to-end web app to upload a PDF and ask questions about its content using a Retrieval-Augmented Generation (RAG) flow.
- **Backend**: FastAPI (Python), ChromaDB vector store (persistent), Gemini (`text-embedding-004` for embeddings, `gemini-1.5-pro` for answers)
- **Frontend**: Vite + React + Tailwind (chat UI similar to the screenshot)

---

## 1) Prerequisites
- Python 3.10+
- Node 18+
- A **Gemini API key** (free) → set it in `server/.env` as `GOOGLE_API_KEY=...`

## 2) Setup & Run

### Backend (FastAPI)
```bash
cd server
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # add your GOOGLE_API_KEY
python main.py
# server runs on http://localhost:8000
```

### Frontend (React)
```bash
cd web
npm i
cp .env.example .env
npm run dev
# open http://localhost:5173
```

## 3) How it works (RAG Flow)
1. **Upload PDF** → server extracts text page-by-page with `pypdf`.
2. **Chunking** → text is split into ~2000‑char chunks with 200 overlap (good for long PDFs, 500+ pages supported).
3. **Embeddings** → each chunk is embedded using Gemini `text-embedding-004` and stored in **ChromaDB** (persistent on disk).
4. **Question** → user asks a question; the question is embedded and a **similarity search** retrieves top chunks.
5. **LLM Answer** → Gemini `gemini-1.5-pro` receives the question + retrieved context and returns a grounded answer with page hints.

## 4) Notes
- Storage path is `server/storage` by default (change with `VECTOR_DB_PATH` in `server/.env`).
- For very large PDFs or strict quotas, embeddings are retried with exponential backoff.
- The model is instructed to only use provided context; if it can’t find the answer, it will say so.
- Max 10 MB upload is enforced on the client for demo; adjust as you like.
- To reset, simply delete the `server/storage` folder (this clears the vector DB).
