import re
from pathlib import Path


DOCUMENTS_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "documents"
)

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_documents() -> list[dict]:
    """Lê os arquivos de documentação suportados."""
    documents = []

    if not DOCUMENTS_DIR.exists():
        return documents

    for path in sorted(DOCUMENTS_DIR.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        content = path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append(
            {
                "source": path.relative_to(
                    DOCUMENTS_DIR
                ).as_posix(),
                "text": content,
            }
        )

    return documents

def split_into_chunks(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[str]:
    """Divide o texto em trechos, priorizando frases e linhas completas."""
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser positivo.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap deve ser >= 0 e menor que chunk_size.")

    text = text.strip()
    if not text:
        return []

    # Sem espaços, não há limites de palavras que possamos preservar.
    if not any(char.isspace() for char in text):
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            if start + chunk_size >= len(text):
                break
            start += chunk_size - overlap
        return chunks

    units = []

    def add_paragraph(lines: list[str]) -> None:
        paragraph = " ".join(lines).strip()
        if paragraph:
            units.extend(
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
                if sentence.strip()
            )

    for block in re.split(r"\n\s*\n", text):
        lines = block.splitlines()
        paragraph_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Mantém títulos Markdown como unidades separadas.
            if line.startswith("#"):
                add_paragraph(paragraph_lines)
                paragraph_lines = []
                units.append(line)

            # Mantém cada item de lista separado.
            elif line.startswith("- "):
                add_paragraph(paragraph_lines)
                paragraph_lines = []
                units.append(line)

            else:
                paragraph_lines.append(line)

        add_paragraph(paragraph_lines)


    # Divide unidades longas por palavras, sem cortar palavras.
    small_units = []

    for unit in units:
        if len(unit) <= chunk_size:
            small_units.append(unit)
            continue

        words = unit.split()
        current = ""

        for word in words:
            if len(word) > chunk_size:
                if current:
                    small_units.append(current)
                    current = ""

                for position in range(0, len(word), chunk_size):
                    small_units.append(word[position:position + chunk_size])
                continue

            candidate = f"{current} {word}".strip()

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    small_units.append(current)
                current = word

        if current:
            small_units.append(current)

    chunks = []
    current = []

    for unit in small_units:
        candidate = "\n".join(current + [unit])

        if len(candidate) <= chunk_size:
            current.append(unit)
        else:
            if current:
                chunks.append("\n".join(current))

            # Mantém a última unidade como contexto, se couber.
            previous = current[-1:] if current else []
            current = (
                previous + [unit]
                if previous and len("\n".join(previous + [unit])) <= chunk_size
                else [unit]
            )

    if current:
        final_chunk = "\n".join(current)
        if not chunks or chunks[-1] != final_chunk:
            chunks.append(final_chunk)

    return chunks

def load_chunks() -> list[dict]:
    """Lê os documentos e retorna seus trechos identificados."""
    chunks = []

    for document in load_documents():
        document_chunks = split_into_chunks(
            document["text"]
        )

        for index, chunk_text in enumerate(document_chunks):
            chunks.append(
                {
                    "source": document["source"],
                    "chunk_id": index,
                    "text": chunk_text,
                }
            )

    return chunks
