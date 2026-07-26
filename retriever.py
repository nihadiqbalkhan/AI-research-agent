"""TF-IDF based passage retriever.

This is the "search tool" the agent uses to find relevant passages inside
the provided source documents. It runs entirely offline (no network, no
API key), so the agent is usable out of the box. See NOTES.md for how to
swap this for a real web-search API or a vector-store retriever.
"""
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .chunking import Passage


class TfidfRetriever:
    def __init__(self, passages: List[Passage]):
        self.passages = passages
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([p.text for p in passages])

    def retrieve(self, question: str, top_k: int = 4) -> List[Tuple[Passage, float]]:
        """Return the top_k (passage, similarity_score) pairs for a question,
        ranked by cosine similarity of TF-IDF vectors, highest first."""
        query_vec = self._vectorizer.transform([question])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(zip(self.passages, scores), key=lambda pair: pair[1], reverse=True)
        return ranked[:top_k]
