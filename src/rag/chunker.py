"""Split documents into overlapping word-window chunks."""


def chunk_document(doc: dict, size: int = 60, overlap: int = 15) -> list[dict]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    words = doc["text"].split()
    step = size - overlap
    chunks, i, n = [], 0, 0
    while i < len(words):
        window = words[i:i + size]
        chunks.append({"chunk_id": f"{doc['doc_id']}#{n}", "doc_id": doc["doc_id"],
                       "text": " ".join(window)})
        n += 1
        if i + size >= len(words):
            break
        i += step
    return chunks


def chunk_all(docs: list[dict], size: int = 60, overlap: int = 15) -> list[dict]:
    return [c for d in docs for c in chunk_document(d, size, overlap)]