# Research Agent (with Citations)

> **My agent takes a user's question (plus a set of source documents or a
> search tool) and produces a cited answer — one that names exactly which
> source passage supports each claim, and says so plainly if the sources
> don't cover the question.**

## What it does

- Accepts a question and a set of source documents (`sources/*.txt`)
- Retrieves the relevant passages and synthesizes an answer
- Cites which source passage each claim came from
- Clearly states when the provided sources do not contain the answer

## Deliverables (in this repo)

| Requirement | File |
|---|---|
| Question set | `questions.json` |
| Source documents | `sources/*.txt` |
| Cited answers | `output/cited_answers.json`, `output/chat_log.json` |
| Note on retrieval/tool approach | `NOTES.md` |

---

## 1. Install

```bash
git clone <this-repo-url>
cd research-agent-citations
pip install -r requirements.txt
```

Requires Python 3.9+.

## 2. Configure your API key

This agent works with either Anthropic (Claude) or OpenAI (GPT) — set
whichever one you have a key for.

**Option A — .env file (recommended):**
```bash
cp .env.example .env
# then open .env and paste your key in
```

**Option B — environment variable:**
```bash
export ANTHROPIC_API_KEY=your-key-here   # or OPENAI_API_KEY
```

Get an Anthropic key at https://console.anthropic.com, or an OpenAI key at
https://platform.openai.com/api-keys. `.env` is gitignored, so your key
never gets committed.

Verify your setup with one test message before doing anything else:

```bash
python test_connection.py
```

It auto-detects which provider you configured and prints the model's
reply. If a response prints to your screen, setup is done — move on to
step 3.

**No key? No problem.** The agent still runs without one: it automatically
falls back to an offline extractive mode (stitches together the most
relevant source passages instead of asking an LLM to write fluent prose).
Every other capability — retrieval, citations, "not found" detection —
works identically either way. This is on purpose, so the project is
runnable out of the box while you're getting a key.

## 3. Run it

**Batch mode** — answers every question in `questions.json` and saves results:

```bash
python run.py
```

Prints each cited answer to the screen and writes them all to
`output/cited_answers.json`.

**Interactive mode** — ask your own questions in a loop:

```bash
python chat.py
```

Type a question, get a cited answer, repeat. Type `quit` to exit. Every
exchange is appended to `output/chat_log.json`.

## 4. Use it in code

```python
from research_agent.agent import ResearchAgent

agent = ResearchAgent(sources_dir="sources")
result = agent.ask("How has the cost of solar panels changed since 2010?")

print(result.answer)          # cited answer text
print(result.citations)       # e.g. ["solar_power.txt#2", "battery_storage.txt#2"]
print(result.found_answer)    # False if the sources didn't cover the question
```

---

## How it was built (matches the 6-step process)

1. **The one job** — see the sentence at the top of this README.
2. **AI model access** — Anthropic API, verified with `test_connection.py`
   (Step 2 script — sends one message, prints the reply).
3. **System prompt** — lives in its own file, `research_agent/prompts.py`,
   so it's easy to find and tune. It tells the model who it is, what its
   job is, and the rules it must follow (cite every claim, never use
   outside knowledge, say "I don't know" when the sources don't cover it).
4. **Data / tools** — `research_agent/chunking.py` loads and chunks the
   source `.txt` files; `research_agent/retriever.py` is the "search tool"
   (TF-IDF passage search) that pulls the relevant chunks into the prompt.
   This is retrieval-augmented generation: read the docs, paste the
   relevant parts into the prompt.
5. **The loop** — `chat.py` implements Input → Fetch data → Prompt+context
   to model → Answer → Display → Save, repeatedly. `run.py` runs the same
   loop non-interactively over a fixed question set.
6. **Test + README** — `output/cited_answers.json` holds 6 real,
   reproducible examples; this README is the result of that step.

## Design choices

- **TF-IDF retrieval, not embeddings.** No model download, no API key, no
  GPU needed just to search the documents — and it's easy to inspect why a
  passage matched. Trade-off: purely lexical, so it can miss passages that
  are relevant but use different wording than the question. Swapping in an
  embedding-based retriever only requires changing `retriever.py` (see
  `NOTES.md` for the exact interface to preserve).
- **Paragraph-level chunking.** Small enough that a citation points to a
  specific, checkable claim; large enough to keep sentences in context.
- **Calibrated relevance threshold (0.22).** Below this, the agent refuses
  to answer rather than guessing. Set by measuring real question scores
  (see `NOTES.md`) — on-topic questions scored 0.28–0.48 against this
  corpus, and the one deliberately out-of-scope question ("nuclear fusion
  power plant cost") scored 0.19.
- **LLM call is optional, not required.** The offline extractive fallback
  means the project is fully runnable and demoable with zero setup cost,
  and the LLM path is a pure quality upgrade on top of the same retrieval
  and citation logic.

## Tradeoffs and what I'd improve with more time

- **Corpus size.** Only 5 short documents / 19 passages are included.
  TF-IDF works well here, but at a larger scale (hundreds of documents) an
  embedding-based retriever would likely find semantically relevant
  passages that don't share exact keywords with the question.
- **Relevance threshold is corpus-specific.** 0.22 was tuned for this
  exact document set and question phrasing; a different corpus would need
  its own calibration pass, or a more robust approach (e.g. an LLM-based
  relevance check instead of a fixed cosine-similarity cutoff).
- **Extractive fallback quality.** Without an API key, answers are
  stitched-together source text rather than a synthesized summary — clear
  and honest, but less readable than the LLM path.
- **Single-provider LLM support.** Only Anthropic is wired up. Adding
  OpenAI/Groq would mean adding a small adapter behind the same
  `synthesize_with_llm(question, ranked_passages) -> str` interface used
  in `research_agent/llm.py`.
- **No multi-turn memory.** `chat.py` treats each question independently;
  it doesn't use earlier turns as context for follow-up questions.

## Project layout

```
research_agent/
  chunking.py   # load .txt sources, split into cited passages
  retriever.py  # TF-IDF "search tool" over the passages
  prompts.py    # the system prompt (the agent's instructions)
  llm.py        # optional Claude-based synthesis (used if ANTHROPIC_API_KEY is set)
  agent.py      # ResearchAgent: ties retrieval + synthesis + citations together
sources/            # sample source documents (renewable energy topic)
questions.json      # sample question set (5 answerable + 1 intentionally not)
test_connection.py  # Step 2: verify API key + SDK work
run.py              # Step 5/6: batch mode, answers questions.json, saves output
chat.py             # Step 5: interactive input/output loop
output/             # cited_answers.json and chat_log.json are written here
NOTES.md            # explains the retrieval/tool approach and how to extend it
```
