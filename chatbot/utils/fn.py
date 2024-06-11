import re
from os.path import normpath
from pathlib import Path
from typing import Optional

import jsonpickle
from langchain_core.load import dumps, loads


def _get_safe_file_path(chats_path, chat_id: str) -> Optional[Path]:
    if not re.search(r"[^A-Za-z0-9_\-\\]", chat_id):
        return Path(normpath(f"{chats_path}/{chat_id}.json"))


def _get_safe_feedback_path(chat_id: str) -> Optional[Path]:
    if not re.search(r"[^A-Za-z0-9_\-\\]", chat_id):
        return Path(normpath(f"feedback/{chat_id}.json"))


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        json = file.read()
        return jsonpickle.decode(json)


def reciprocal_rank_fusion(results: list[list], k=60, top_n=5):
    fused_scores = {}
    for docs in results:
        # Assumes the docs are returned in sorted order of relevance
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            # previous_score = fused_scores[doc_str]  TODO: Remove or keep
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = []

    for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True):
        reranked_results.append((loads(doc), score))

    return reranked_results[:top_n]
