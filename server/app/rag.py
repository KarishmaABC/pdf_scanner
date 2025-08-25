# server/app/rag.py
import os
import uuid
from typing import List, Dict, Any
import chromadb
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt

VECTOR_DB_PATH = os.environ.get("VECTOR_DB_PATH", "./storage")
EMBED_MODEL = os.environ.get("GEMINI_EMBED_MODEL", "text-embedding-004")
GEN_MODEL = os.environ.get("GEMINI_GENERATION_MODEL", "gemini-1.5-flash")

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

def _collection_name(doc_id: str) -> str:
    return f"doc_{doc_id}"

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
def embed_text(text: str, task_type: str = "retrieval_document") -> List[float]:
    resp = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type=task_type,
    )
    return resp["embedding"]

def upsert_embeddings(doc_id: str, texts: List[str], metadatas: List[Dict[str, Any]]):
    col = _client.get_or_create_collection(name=_collection_name(doc_id))
    ids = []
    embeds = []
    for i, t in enumerate(texts):
        ids.append(f"{doc_id}:{i:06d}")
        embeds.append(embed_text(t, task_type="retrieval_document"))
    col.add(ids=ids, embeddings=embeds, documents=texts, metadatas=metadatas)

def similarity_search(doc_id: str, query: str, k: int = 4):
    col = _client.get_or_create_collection(name=_collection_name(doc_id))
    q_emb = embed_text(query, task_type="retrieval_query")
    res = col.query(query_embeddings=[q_emb], n_results=k)
    results = []
    if res and res.get("documents"):
        docs = res["documents"][0]
        metas = res.get("metadatas", [[]])[0]
        ids = res.get("ids", [[]])[0]
        for _id, doc, meta in zip(ids, docs, metas):
            results.append({"id": _id, "text": doc, "meta": meta})
    return results

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def answer_with_context(question: str, contexts: List[Dict[str, Any]]) -> str:
    """
    Ask Gemini to answer using only provided context.
    We trim total context to reduce input tokens and free-tier usage.
    """
    from google.api_core.exceptions import ResourceExhausted

    model = genai.GenerativeModel(GEN_MODEL)

    # Build & trim context to a safe size (keeps citations)
    MAX_CONTEXT_CHARS = 12000  # ~ conservative for free tier
    parts = []
    running = 0
    for i, c in enumerate(contexts, start=1):
        page = c.get("meta", {}).get("page", "?")
        block = f"[Chunk {i} | p.{page}]:\n{c['text']}\n\n"
        if running + len(block) > MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        running += len(block)
    context_text = "".join(parts) if parts else "No context retrieved."

    system = (
        "You are a careful analyst of PDF documents. "
        "Use ONLY the provided context snippets to answer the user's question. "
        "If the answer cannot be found in the context, say you couldn't find it. "
        "Cite page numbers using [p.X] when relevant. Be concise and factual."
    )

    prompt = f"""{system}

Context:
{context_text}

Question: {question}

Answer:"""

    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except ResourceExhausted as e:
        # Map to a clearer message that our FastAPI route can pass through
        raise RuntimeError(
            "Gemini free-tier rate/usage limit hit. Please wait a bit or switch to a lighter model "
            "(e.g. gemini-1.5-flash-8b) / reduce context."
        ) from e
