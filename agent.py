"""Core research agent: question -> retrieved passages -> cited answer."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from .chunking import Passage, chunk_documents, load_documents
from .retriever import TfidfRetriever

# Similarity below this is treated as "not relevant enough" -> no answer found.
# Calibrated on questions.json: on-topic questions score ~0.28-0.48 against
# this corpus; an out-of-scope question (fusion power) scores ~0.19.
RELEVANCE_THRESHOLD = 0.22


@dataclass
class CitedAnswer:
    question: str
    answer: str
    citations: List[str] = field(default_factory=list)  # passage ids actually used
    found_answer: bool = True


class ResearchAgent:
    """Answers a question from a fixed set of source documents, with citations.

    Pipeline:
      1. load_documents / chunk_documents -> Passage objects (source text)
      2. TfidfRetriever.retrieve(question) -> top-k relevant passages + scores
      3. synthesize an answer from those passages (LLM if ANTHROPIC_API_KEY
         or OPENAI_API_KEY is set, otherwise an offline extractive
         fallback), tagging every claim with the passage(s) it came from
      4. if nothing in the sources is relevant, say so explicitly rather
         than guessing or using outside knowledge
    """

    def __init__(self, sources_dir: str, top_k: int = 4):
        self.sources_dir = Path(sources_dir)
        docs = load_documents(self.sources_dir)
        if not docs:
            raise FileNotFoundError(f"No .txt source documents found in {self.sources_dir}")
        self.passages = chunk_documents(docs)
        self.retriever = TfidfRetriever(self.passages)
        self.top_k = top_k

    def ask(self, question: str) -> CitedAnswer:
        ranked = self.retriever.retrieve(question, top_k=self.top_k)
        ranked = [(p, s) for p, s in ranked if s > 0]  # drop zero-similarity noise

        if not ranked or ranked[0][1] < RELEVANCE_THRESHOLD:
            return CitedAnswer(
                question=question,
                answer="The provided sources do not contain information to answer this question.",
                citations=[],
                found_answer=False,
            )

        if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
            from .llm import synthesize_with_llm
            answer_text = synthesize_with_llm(question, ranked)
        else:
            answer_text = self._extractive_synthesis(ranked)

        return CitedAnswer(
            question=question,
            answer=answer_text,
            citations=[p.id for p, _ in ranked],
        )

    @staticmethod
    def _extractive_synthesis(ranked: List[Tuple[Passage, float]]) -> str:
        """Offline fallback used automatically when no ANTHROPIC_API_KEY is
        set: stitches together the most relevant passages, each tagged with
        its source, so the agent is fully runnable with no network access."""
        return "\n\n".join(f"{p.text.strip()} (Source: {p.id})" for p, _score in ranked)
