"""Utilities for loading source documents and splitting them into
retrievable passages."""
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Passage:
    """A single retrievable chunk of text from a source document."""
    id: str       # e.g. "solar_power.txt#2"
    source: str   # source document filename
    text: str


def load_documents(sources_dir: Path) -> dict:
    """Read every .txt file in sources_dir into {filename: raw_text}."""
    docs = {}
    for path in sorted(Path(sources_dir).glob("*.txt")):
        docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def chunk_documents(docs: dict, min_chars: int = 40) -> List[Passage]:
    """Split each document into paragraph-level passages.

    Paragraphs shorter than `min_chars` (e.g. stray headers) are merged
    into the following paragraph so retrieval never operates on fragments.
    """
    passages: List[Passage] = []
    for source, text in docs.items():
        raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        buffer = ""
        idx = 0
        for para in raw_paragraphs:
            buffer = f"{buffer} {para}".strip() if buffer else para
            if len(buffer) >= min_chars:
                idx += 1
                passages.append(Passage(id=f"{source}#{idx}", source=source, text=buffer))
                buffer = ""
        if buffer:
            idx += 1
            passages.append(Passage(id=f"{source}#{idx}", source=source, text=buffer))
    return passages
