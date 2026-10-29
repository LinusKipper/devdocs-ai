
import httpx


API_URL = "http://127.0.0.1:8000/chat"

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
        "pergunta": "Qual é a finalidade do código HTTP 401?",
        "termos_esperados": [
            "401",
            "autenticação válida",
        ],
        "fonte_esperada": "status-http.md",
    },
    {
        "pergunta": "Qual é a diferença entre GET e POST?",
        "termos_esperados": [
            "GET",
            "POST",
            "consulta",
            "cria",
        ],
        "termos_proibidos": [
            "enviados na URL",
            "não altera o estado",
            "não podem ser alterados",
        ],
        "fonte_esperada": "rest.md",
    },
    {
        "pergunta": "Qual é o código HTTP para redirecionamento?",
        "termos_esperados": [
            "redirecionamento",
        ],
        "termos_esperados_alternativos": [
            "3xx",
            "redirecionamento",
        ],
        "fonte_esperada": "status-http.md",
    },
    {
    "pergunta": "Qual é a diferença entre HTTP e REST?",
    "termos_esperados": [
        "protocolo",
        "arquitetural",
    ],
    "fonte_esperada": "rest.md",
    },
    {
        "pergunta": "O que significa o código HTTP 503?",
        "termos_esperados": [
            "503",
        ],
        "termos_esperados_alternativos": [
            "temporariamente indisponível",
            "temporariamente não disponível",
            "serviço indisponível",
        ],
        "fonte_esperada": "status-http.md",
    },
    {
        "pergunta": "Qual é a complexidade de tempo do algoritmo QuickSort?",
        "termos_esperados": [],
        "fonte_esperada": None,
        "deve_abster": True,
    },
    {
        "pergunta": "Quem criou a linguagem Python?",
        "termos_esperados": [],
        "fonte_esperada": None,
        "deve_abster": True,
    },
]

def avaliar_resposta(resposta, caso):
    resposta_normalizada = resposta.lower()

    if caso.get("deve_abster", False):
        indicadores_abstencao = [
            "não encontrei informações relevantes",
            "não há dados suficientes",
            "não há informações suficientes",
            "não consigo determinar",
            "não é possível determinar",
        ]

        return any(
            indicador in resposta_normalizada
            for indicador in indicadores_abstencao
        )

    termos_presentes = all(
        termo.lower() in resposta_normalizada
        for termo in caso["termos_esperados"]
    )

    termos_proibidos_presentes = any(
        termo.lower() in resposta_normalizada
        for termo in caso.get("termos_proibidos", [])
    )

    return termos_presentes and not termos_proibidos_presentes

def main():
    total = len(CASOS_DE_TESTE)
    acertos_resposta = 0
    acertos_fonte = 0
    acertos_abstencao = 0
    total_abstencao = 0

    print("AVALIAÇÃO DAS RESPOSTAS DO RAG")
    print("=" * 45)

    with httpx.Client(timeout=180.0) as client:
        for caso in CASOS_DE_TESTE:
            pergunta = caso["pergunta"]

            response = client.post(
                API_URL,
                json={"question": pergunta},
            )
            response.raise_for_status()
            resultado = response.json()

            resposta = resultado["answer"]
            fontes = resultado["sources"]

            #if "QuickSort" in pergunta:
                #print(f"Fontes retornadas no QuickSort: {fontes}")
            
            resposta_correta = avaliar_resposta(
                resposta,
                caso,
            )

            fonte_esperada = caso.get("fonte_esperada")

            if caso.get("deve_abster", False):
                fonte_correta = len(fontes) == 0
            elif fonte_esperada is None:
                fonte_correta = True
            else:
                fonte_correta = any(
                    fonte["source"] == fonte_esperada
                    for fonte in fontes
                )

            abstencao_correta = True

            if caso.get("deve_abster", False):
                abstencao_correta = (
                    len(fontes) == 0
                    and "não encontrei informações relevantes"
                    in resposta.lower()
                )

            acertos_resposta += resposta_correta
            acertos_fonte += fonte_correta

            if caso.get("deve_abster", False):
                total_abstencao += 1
                acertos_abstencao += abstencao_correta

            print(f"\nPergunta: {pergunta}")
            print(f"Resposta do modelo: {resposta}")
            print(
                "Termos esperados: "
                f"{'PASSOU' if resposta_correta else 'FALHOU'}"
            )
            print(
                "Fonte esperada: "
                f"{'PASSOU' if fonte_correta else 'FALHOU'}"
            )

            if caso.get("deve_abster", False):
                print(
                    "Abstenção: "
                    f"{'PASSOU' if abstencao_correta else 'FALHOU'}"
                )

    print("\n" + "=" * 45)
    print(f"Respostas corretas: {acertos_resposta}/{total}")
    print(f"Fontes esperadas: {acertos_fonte}/{total}")
    print(
        f"Abstenção correta: "
        f"{acertos_abstencao}/{total_abstencao}"
    )


if __name__ == "__main__":
    main()
