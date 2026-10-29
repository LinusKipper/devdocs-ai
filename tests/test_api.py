
import asyncio

from fastapi.testclient import TestClient

import app.main as main


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "message": {
                "content": (
                    "REST significa Representational State Transfer."
                )
            }
        }


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def post(self, *args, **kwargs):
        return FakeResponse()


def test_chat_returns_answer_and_sources(monkeypatch):
    async def fake_retrieve(question):
        assert question == "O que significa REST?"

        return [
            {
                "source": "rest.md",
                "chunk_id": 0,
                "text": "REST significa Representational State Transfer.",
                "score": 0.54,
            }
        ]

    monkeypatch.setattr(main, "retrieve", fake_retrieve)
    monkeypatch.setattr(
        main.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    client = TestClient(main.app)

    response = client.post(
        "/chat",
        json={"question": "O que significa REST?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "Representational State Transfer" in data["answer"]
    assert data["model"] == "qwen2.5:1.5b"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source"] == "rest.md"
    assert data["sources"][0]["score"] == 0.54


def test_chat_abstains_when_no_relevant_sources(monkeypatch):
    async def fake_retrieve(question):
        return [
            {
                "source": "rest.md",
                "chunk_id": 0,
                "text": "Conteúdo sobre REST.",
                "score": 0.10,
            }
        ]

    def unexpected_ollama_call(*args, **kwargs):
        raise AssertionError(
            "O Ollama não deveria ser chamado sem contexto relevante."
        )

    monkeypatch.setattr(main, "retrieve", fake_retrieve)
    monkeypatch.setattr(
        main.httpx,
        "AsyncClient",
        unexpected_ollama_call,
    )

    client = TestClient(main.app)

    response = client.post(
        "/chat",
        json={"question": "Quem criou a linguagem Python?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "Não encontrei informações relevantes" in data["answer"]
    assert data["sources"] == []


def test_chat_rejects_empty_question():
    client = TestClient(main.app)

    response = client.post(
        "/chat",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_chat_returns_model_answer_and_sources(monkeypatch):
    async def fake_retrieve(question):
        return [
            {
                "source": "status-http.md",
                "chunk_id": 3,
                "text": (
                    "404 Not Found: o recurso solicitado "
                    "não foi encontrado."
                ),
                "score": 0.62,
            }
        ]

    monkeypatch.setattr(main, "retrieve", fake_retrieve)
    monkeypatch.setattr(
        main.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    client = TestClient(main.app)

    response = client.post(
        "/chat",
        json={
            "question": (
                "Qual código indica que um recurso "
                "não foi encontrado?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "Representational State Transfer" in data["answer"]
    assert data["sources"][0]["source"] == "status-http.md"

