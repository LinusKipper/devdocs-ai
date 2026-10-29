
from app.knowledge import load_chunks

for chunk in load_chunks():
    print(
        f"{chunk['source']} | "
        f"chunk {chunk['chunk_id']} | "
        f"{len(chunk['text'])} caracteres"
    )
    print(chunk["text"])
    print("-" * 50)
