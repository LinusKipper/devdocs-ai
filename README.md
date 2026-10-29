# DevDocs AI

Assistente de documentação técnica que utiliza Retrieval-Augmented Generation (RAG) e um modelo de linguagem executado localmente para responder perguntas com base em documentos, apresentar fontes e se abster quando não encontra informações relevantes.

## Objetivo

O projeto explora a construção de uma aplicação de IA com foco em recuperação de informações, geração de respostas fundamentadas, avaliação de resultados e execução local de modelos de linguagem.

## Funcionalidades

- API REST construída com FastAPI.
- Recuperação de trechos de documentos por similaridade semântica.
- Geração de respostas com um modelo local via Ollama.
- Apresentação das fontes utilizadas nas respostas.
- Filtro de relevância para descartar trechos pouco relevantes.
- Abstenção quando não há contexto considerado relevante.
- Testes automatizados e scripts de avaliação do RAG.

## Tecnologias

- Python 3.11
- FastAPI
- Ollama
- Qwen 2.5 1.5B
- BGE-M3 para embeddings
- NumPy
- Pytest

## Estrutura do projeto

```text
devdocs-ai/
├── app/
│   ├── main.py
│   ├── knowledge.py
│   ├── rag.py
│   └── __init__.py
├── data/
│   └── documents/
│       ├── http.md
│       ├── rest.md
│       └── status-http.md
├── tests/
│   ├── test_api.py
│   └── test_knowledge.py
├── avaliar_busca.py
├── avaliar_rag.py
├── avaliar_respostas.py
├── inspecionar_chunks.py
├── requirements.txt
└── .gitignore
```

## Requisitos

- Python 3.11
- [Ollama](https://ollama.com/)
- Modelos locais necessários para geração e embeddings.

## Instalação

Clone o repositório e entre na pasta do projeto.

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Baixe os modelos necessários no Ollama:

```powershell
ollama pull qwen2.5:1.5b
ollama pull bge-m3
```

Certifique-se de que o Ollama esteja em execução antes de iniciar a aplicação.

## Executando a aplicação

Na raiz do projeto, execute:

```powershell
python -m uvicorn app.main:app --reload
```

A API ficará disponível em:

- API: http://127.0.0.1:8000
- Documentação interativa: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/health

O endpoint `POST /chat` recebe uma pergunta e retorna a resposta gerada, o modelo utilizado e as fontes recuperadas.

## Testes

Execute os testes automatizados:

```powershell
python -m pytest -v
```

Para avaliar a recuperação e as respostas do RAG, com a API em execução, utilize:

```powershell
python avaliar_busca.py
python avaliar_rag.py
python avaliar_respostas.py
```

Os scripts de avaliação verificam aspectos como recuperação de documentos, presença de fontes esperadas e abstenção em perguntas que não podem ser respondidas com a documentação disponível.

## Limitações atuais

- A base de conhecimento é pequena e contém documentos técnicos sobre HTTP e REST.
- O desempenho depende da relevância dos trechos recuperados e das respostas do modelo local.
- O limite de similaridade e os critérios de avaliação são configurações iniciais, que precisam ser validadas em conjuntos de testes mais abrangentes.
- Os resultados dos testes não representam uma garantia de precisão para perguntas arbitrárias.

## Próximos passos

- Ampliar a base de conhecimento e os casos de avaliação.
- Melhorar a avaliação da relevância e da fundamentação das respostas.
- Medir falsos positivos e falsos negativos na recuperação.
- Documentar experimentos e limitações.
- Desenvolver uma interface para interação com o assistente.
