"""Load plain-text documents from a folder."""
from pathlib import Path


def load_documents(data_dir: str = "data") -> list[dict]:
    docs = []
    for p in sorted(Path(data_dir).glob("*_policy.txt")):
        docs.append({"doc_id": p.stem, "text": p.read_text(encoding="utf-8")})
    return docs