
import asyncio

from app.rag import retrieve

perguntas = [
    "O que significa REST?",
    "Qual código indica que um recurso não foi encontrado?",
    "Qual a diferença entre HTTP e REST?",
]


async def main():
    for pergunta in perguntas:
        print(f"\n### Pergunta: {pergunta}")

        resultados = await retrieve(pergunta)

        for resultado in resultados:
            print(
                f"\nFonte: {resultado['source']} "
                f"| trecho: {resultado['chunk_id']} "
                f"| score: {resultado['score']:.3f}"
            )
            print(resultado["text"][:350])


if __name__ == "__main__":
    asyncio.run(main())
