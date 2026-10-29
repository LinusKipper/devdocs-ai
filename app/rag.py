
import hashlib

import httpx
import numpy as np

from app.knowledge import load_chunks


OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "bge-m3"

# Índice mantido em memória enquanto a aplicação estiver executando.
_cached_signature = None
_cached_chunks = []
_cached_vectors = None


async def embed_text(text: str) -> np.ndarray:
    """Converte um texto em um vetor usando o Ollama."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text,
            },
        )
        response.raise_for_status()

    embedding = response.json()["embedding"]
    return np.array(embedding, dtype=np.float32)


async def build_index() -> None:
    """Gera embeddings dos documentos e guarda o índice em memória."""
    global _cached_signature
    global _cached_chunks
    global _cached_vectors

    chunks = load_chunks()

    # Identifica alterações no conteúdo dos documentos.
    signature_data = "\n".join(
        f"{chunk['source']}:{chunk['text']}"
        for chunk in chunks
    )
    signature = hashlib.sha256(
        signature_data.encode("utf-8")
    ).hexdigest()

    if signature == _cached_signature:
        return

    if not chunks:
        _cached_chunks = []
        _cached_vectors = None
        _cached_signature = signature
        return

    vectors = []

    for chunk in chunks:
        vector = await embed_text(chunk["text"])
        vectors.append(vector)

    _cached_chunks = chunks
    _cached_vectors = np.vstack(vectors)
    _cached_signature = signature


async def retrieve(
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Recupera os trechos mais semelhantes à pergunta."""
    await build_index()

    if not _cached_chunks or _cached_vectors is None:
        return []

    question_vector = await embed_text(question)

    # Similaridade de cosseno entre a pergunta e cada trecho.
    document_norms = np.linalg.norm(
        _cached_vectors, axis=1
    )
    question_norm = np.linalg.norm(question_vector)

    if question_norm == 0 or np.any(document_norms == 0):
        return []

    similarities = (
        _cached_vectors @ question_vector
    ) / (document_norms * question_norm)

    # Ordena do trecho mais semelhante para o menos semelhante.
    best_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in best_indices:
        chunk = _cached_chunks[int(index)]

        results.append(
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": float(similarities[index]),
            }
        )

    return results
