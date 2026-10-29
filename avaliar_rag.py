
import asyncio

from app.rag import retrieve


CASOS_DE_TESTE = [
    {
        "pergunta": "O que significa REST?",
        "termos_esperados": [
            "Representational State Transfer",
        ],
        "fonte_esperada": "rest.md",
    },
    {
        "pergunta": "Qual código indica que um recurso não foi encontrado?",
        "termos_esperados": [
            "404",
            "não foi encontrado",
        ],
        "fonte_esperada": "status-http.md",
    },
    {
        "pergunta": "Qual a diferença entre HTTP e REST?",
        "termos_esperados": [
            "protocolo",
            "estilo arquitetural",
        ],
        "fonte_esperada": "http.md",
    },
    {
        "pergunta": "Qual é a finalidade do código HTTP 401?",
        "termos_esperados": [
            "autenticação válida",
        ],
        "fonte_esperada": "status-http.md",
    },
]


async def main():
    total = len(CASOS_DE_TESTE)
    acertos_resposta = 0
    acertos_fonte = 0

    print("AVALIAÇÃO DA RECUPERAÇÃO RAG")
    print("=" * 40)

    for caso in CASOS_DE_TESTE:
        pergunta = caso["pergunta"]
        resultados = await retrieve(pergunta)

        textos = " ".join(
            resultado["text"] for resultado in resultados
        ).lower()

        resposta_correta = all(
            termo.lower() in textos
            for termo in caso["termos_esperados"]
        )

        fonte_correta = any(
            resultado["source"] == caso["fonte_esperada"]
            for resultado in resultados
        )

        acertos_resposta += resposta_correta
        acertos_fonte += fonte_correta

        print(f"\nPergunta: {pergunta}")
        print(
            "Conteúdo esperado recuperado: "
            f"{'PASSOU' if resposta_correta else 'FALHOU'}"
        )
        print(
            "Fonte esperada recuperada: "
            f"{'PASSOU' if fonte_correta else 'FALHOU'}"
        )

        for resultado in resultados:
            print(
                f"  - {resultado['source']} "
                f"(score: {resultado['score']:.3f})"
            )

    print("\n" + "=" * 40)
    print(f"Conteúdo esperado: {acertos_resposta}/{total}")
    print(f"Fontes esperadas: {acertos_fonte}/{total}")


if __name__ == "__main__":
    asyncio.run(main())
