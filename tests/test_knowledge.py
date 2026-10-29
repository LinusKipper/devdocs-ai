
import pytest

from app.knowledge import load_documents, split_into_chunks


def test_split_into_chunks_returns_text():
    chunks = split_into_chunks("REST é um estilo arquitetural.")

    assert len(chunks) == 1
    assert chunks[0] == "REST é um estilo arquitetural."


def test_split_into_chunks_returns_empty_list_for_empty_text():
    assert split_into_chunks("") == []
    assert split_into_chunks("   ") == []


def test_split_into_chunks_preserves_all_text():
    text = "A" * 2000

    chunks = split_into_chunks(
        text,
        chunk_size=500,
        overlap=50,
    )

    assert len(chunks) > 1

    # Cada trecho deve respeitar o tamanho máximo.
    assert all(len(chunk) <= 500 for chunk in chunks)

    # A sobreposição não deve fazer conteúdo desaparecer.
    reconstructed = "".join(
        chunk if index == 0 else chunk[50:]
        for index, chunk in enumerate(chunks)
    )

    assert reconstructed == text


def test_split_into_chunks_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        split_into_chunks("texto", chunk_size=100, overlap=100)


def test_load_documents_finds_rest_document():
    documents = load_documents()

    assert any(
        document["source"] == "rest.md"
        for document in documents
    )

    rest_document = next(
        document
        for document in documents
        if document["source"] == "rest.md"
    )

    assert "Representational State Transfer" in rest_document["text"]


def test_split_into_chunks_preserves_words_at_boundaries():
    text = (
        "REST é um estilo arquitetural. "
        "HTTP é um protocolo de comunicação. "
    ) * 20

    chunks = split_into_chunks(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert not chunk.startswith(" ")
        assert not chunk.endswith(" ")


def test_split_into_chunks_respects_maximum_size():
    text = "REST é um estilo arquitetural. " * 30

    chunks = split_into_chunks(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert all(len(chunk) <= 100 for chunk in chunks)
