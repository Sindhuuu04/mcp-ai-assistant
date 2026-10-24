"""Retrieval metrics. Labels are at DOC level; retrieval returns CHUNKS.
 - Precision@K: fraction of the K returned chunks whose doc is relevant (denominator = chunks actually returned;
   returns 0.0 for an empty result).
 - Recall@K: fraction of relevant docs that appear among the top-K chunks.
 - Reciprocal rank: 1/rank of the first chunk from a relevant doc (0 if none)."""
import json


def precision_at_k(ranked_doc_ids: list[str], relevant: set[str], k: int) -> float:
    top = ranked_doc_ids[:k]
    return sum(d in relevant for d in top) / len(top) if top else 0.0


def recall_at_k(ranked_doc_ids: list[str], relevant: set[str], k: int) -> float:
    return len(set(ranked_doc_ids[:k]) & relevant) / len(relevant) if relevant else 0.0


def reciprocal_rank(ranked_doc_ids: list[str], relevant: set[str]) -> float:
    for i, d in enumerate(ranked_doc_ids, start=1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def evaluate(retriever, queries: list[dict], k: int = 3) -> dict:
    rows = []
    for q in queries:
        rel = set(q["relevant_docs"])
        ranked = [r["doc_id"] for r in retriever.search(q["query"], k=k)]
        rows.append({"id": q["id"], "query": q["query"], "type": q.get("type", ""),
                     "retrieved": ranked, "relevant": sorted(rel),
                     "p@1": precision_at_k(ranked, rel, 1), "p@3": precision_at_k(ranked, rel, 3),
                     "r@3": recall_at_k(ranked, rel, 3), "rr": reciprocal_rank(ranked, rel)})
    n = len(rows)
    summary = {"n_queries": n,
               "precision@1": round(sum(r["p@1"] for r in rows) / n, 3),
               "precision@3": round(sum(r["p@3"] for r in rows) / n, 3),
               "recall@3": round(sum(r["r@3"] for r in rows) / n, 3),
               "mrr": round(sum(r["rr"] for r in rows) / n, 3)}
    return {"summary": summary, "rows": rows}


def load_queries(path: str = "data/eval_queries.json") -> list[dict]:
    return json.load(open(path, encoding="utf-8"))