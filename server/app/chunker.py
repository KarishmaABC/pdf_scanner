from __future__ import annotations
from typing import Iterable, List, Tuple

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Simple recursive-overlap chunker by characters.
    Works well for Gemini; tweak sizes as needed.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be < chunk_size")

    start = 0
    n = len(text)
    chunks = []
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
