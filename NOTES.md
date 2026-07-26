# Retrieval / Tool Approach

## Pipeline

1. **Load & chunk sources** (`research_agent/chunking.py`) — each `.txt`
   file in `sources/` is split into paragraph-level passages, each given a
   stable id like `solar_power.txt#2`. Chunking at the paragraph level
   keeps each passage focused enough to cite precisely, without being so
   small that it loses context.

2. **Retrieve** (`research_agent/retriever.py`) — a `TfidfRetriever`
   vectorizes every passage with TF-IDF and ranks passages against the
   question by cosine similarity. This is the "search tool": it plays the
   same role a web-search or vector-database call would, but runs fully
   offline against the fixed document set, so the agent works with no
   network access or API key.

3. **Relevance gate** (`research_agent/agent.py`) — if the best-matching
   passage scores below `RELEVANCE_THRESHOLD` (0.22), the agent reports
   that the sources don't contain the answer instead of guessing. The
   threshold was set by measuring scores on `questions.json`: the five
   in-scope questions score 0.28-0.48, while the one deliberately
   out-of-scope question ("nuclear fusion power plant cost" — not covered
   by any source) scores 0.19. Real deployments should re-calibrate this
   threshold against their own corpus and question distribution.

4. **Synthesize** — the top passages are turned into an answer with a
   citation on every claim:
   - If `ANTHROPIC_API_KEY` is set, `research_agent/llm.py` sends the
     question plus the numbered, retrieved passages to Claude with a
     system prompt that requires every claim to cite `[S1]`, `[S2]`, etc.
     and forbids using outside knowledge.
   - If no key is set, `ResearchAgent._extractive_synthesis` falls back to
     stitching the retrieved passages together verbatim, each tagged with
     its source id — no generation, so it's still fully offline and
     citations are exact by construction.

## Why TF-IDF instead of a vector/embedding search

TF-IDF needs no model download, no API key, and no GPU, and is easy to
reason about and debug (you can inspect the exact term weights driving a
match). For a larger or more semantically diverse corpus, `retriever.py`
is the only file that would need to change — swap `TfidfRetriever` for an
embedding-based retriever (e.g. `sentence-transformers` + a vector index)
behind the same `retrieve(question, top_k) -> [(Passage, score)]`
interface used by `agent.py`.

## Why passage-level citations instead of a single "source list"

Citing the specific passage (`solar_power.txt#2`) rather than just the
file lets a reader verify exactly which sentence(s) support a claim,
rather than having to search a whole document. This is the same idea used
in `gpt_researcher`'s human-in-the-loop workflow — checkable claims — kept
minimal here to match the four stated requirements.

## Swapping in a real web-search tool

To use live web search instead of / in addition to fixed source
documents, replace `TfidfRetriever` with a retriever that:
1. Calls a search API (e.g. Tavily, Bing, SerpAPI) for the question.
2. Fetches and chunks the returned pages into `Passage` objects the same
   way `chunk_documents` does for local files.
3. Ranks those passages by relevance (TF-IDF, or the search API's own
   ranking) and returns the same `(Passage, score)` tuples.

No changes to `agent.py` or `llm.py` are required, since both only depend
on the `Passage` interface and the `retrieve()` contract.
