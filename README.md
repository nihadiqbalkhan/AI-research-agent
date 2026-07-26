# AI-research-agent
A research agent that answers questions from your source documents with per-claim citations, and says so plainly when the answer isn't in the sources.

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

## Sample outputs

```json
[
  {
    "question": "How has the cost of solar panels changed since 2010?",
    "answer": "The cost of solar panels has decreased by approximately 90% since 2010. This significant reduction is attributed to factors such as increased manufacturing scale, the use of thinner silicon wafers, and advancements in automated production techniques. As a result, solar energy has become the cheapest source of new electricity generation in many regions, even without subsidies [S1].",
    "citations": [
      "solar_power.txt#2",
      "battery_storage.txt#2",
      "solar_power.txt#1",
      "policy_incentives.txt#2"
    ],
    "found_answer": true
  },
  {
    "question": "Why do offshore wind farms have higher capacity factors than onshore wind farms?",
    "answer": "Offshore wind farms have higher capacity factors than onshore wind farms primarily because they benefit from stronger, steadier winds over open water. Typically, offshore capacity factors range from 40-50%, while onshore capacity factors are between 25-35% [S1]. This difference is attributed to the more favorable wind conditions found offshore compared to land-based locations. However, it's important to note that offshore projects incur significantly higher costs due to the necessary marine foundations, subsea cabling, and specialized vessels for their construction and maintenance [S1].",
    "citations": [
      "wind_power.txt#2",
      "wind_power.txt#3",
      "wind_power.txt#1",
      "solar_power.txt#1"
    ],
    "found_answer": true
  },
  {
    "question": "How much storage duration do most grid-scale batteries provide today?",
    "answer": "Most grid-scale batteries installed today provide between two and four hours of storage at rated power. This duration is sufficient for shifting renewable generation across several hours but does not support multi-day gaps in wind or solar output [S1].",
    "citations": [
      "battery_storage.txt#3",
      "battery_storage.txt#1",
      "grid_challenges.txt#3",
      "battery_storage.txt#2"
    ],
    "found_answer": true
  },
  {
    "question": "What makes it difficult to add large amounts of solar and wind to the electricity grid?",
    "answer": "Adding large amounts of solar and wind to the electricity grid is challenging primarily due to their variable nature and the need for grid stability. Traditional electricity grids were designed for a few large power plants that could adjust output to meet demand. In contrast, solar and wind generation fluctuate based on weather conditions, making it difficult for grid operators to manage and match supply with demand [S1].\n\nFurthermore, maintaining frequency stability is essential for grid operation, traditionally supported by the inertia from large spinning generators. As the proportion of solar and wind energy increases, which do not provide this spinning inertia, operators must find alternative solutions, such as batteries and grid-forming inverters, to ensure stability [S2]. Additionally, wind generation can suffer from periods of low output when wind speeds are calm, further complicating integration efforts [S4].",
    "citations": [
      "grid_challenges.txt#1",
      "grid_challenges.txt#3",
      "wind_power.txt#4",
      "wind_power.txt#3"
    ],
    "found_answer": true
  },
  {
    "question": "What policy tools do governments use to encourage renewable energy adoption?",
    "answer": "Governments use several policy tools to encourage the adoption of renewable energy. One key tool is renewable portfolio standards, which require utilities to source a minimum percentage of their electricity from renewable sources by a specific target year. This has been a significant driver for the deployment of wind and solar energy on a utility scale [S2].\n\nAdditionally, governments often implement tax credits, such as investment tax credits or production tax credits, to reduce the effective cost of building solar and wind projects. These credits lower the project developer's tax liability, either as a percentage of the capital costs or by providing a fixed amount per unit of electricity generated [S3].\n\nThese measures work together to promote the transition to renewable energy sources.",
    "citations": [
      "policy_incentives.txt#1",
      "policy_incentives.txt#3",
      "policy_incentives.txt#2",
      "battery_storage.txt#1"
    ],
    "found_answer": true
  },
  {
    "question": "What is the current cost of building a nuclear fusion power plant?",
    "answer": "The provided sources do not contain information to answer this question.",
    "citations": [],
    "found_answer": false
  }
]
```

```json
[
  {
    "question": "what is the best renewabal electrical energy source available and what is the consumption rate as of today",
    "answer": "The provided sources do not contain information to answer this question.",
    "citations": [],
    "found_answer": false
  },
  {
    "question": "what are the renewable energy sources available?",
    "answer": "The provided sources do not contain information to answer this question.",
    "citations": [
      "policy_incentives.txt#1",
      "policy_incentives.txt#3",
      "battery_storage.txt#1",
      "grid_challenges.txt#4"
    ],
    "found_answer": true
  },
  {
    "question": "what are lithium-aio batteries",
    "answer": "The provided sources do not contain information specifically about \"lithium-aio batteries.\" They focus on lithium-ion batteries, discussing their characteristics, such as battery degradation, advantages for grid-scale energy storage, and cost trends. If you meant lithium-ion batteries, they are noted for their high energy density, fast response times, and the ability to provide short-term storage for renewable energy sources [S1][S2][S4].",
    "citations": [
      "battery_storage.txt#4",
      "battery_storage.txt#1",
      "battery_storage.txt#3",
      "battery_storage.txt#2"
    ],
    "found_answer": true
  }
]
```

---

## 1. Install

Requires Python 3.10+.

```bash
git clone <this-repo-url>
cd research-agent-citations
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure API keys

The agent calls the Anthropic API to synthesize and cite answers. Create a `.env` file in the project root (never commit this file — it's already in `.gitignore`):

```bash
cp .env.example .env
```

Then edit `.env` and add your key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

You can generate a key from the [Anthropic Console](https://console.anthropic.com/settings/keys). The agent loads this automatically via `python-dotenv` at startup — no need to export it manually in your shell.

## 3. Run the agent end to end

**Step 1 — Add your source documents**
Drop plain-text files into `sources/`. Each file is chunked and indexed for retrieval:

```bash
sources/
  solar_power.txt
  wind_power.txt
  battery_storage.txt
  policy_incentives.txt
  grid_challenges.txt
```

**Step 2 — Define your questions**
Edit `questions.json` with a list of questions:

```json
[
  "How has the cost of solar panels changed since 2010?",
  "What is the current cost of building a nuclear fusion power plant?"
]
```

**Step 3 — Run the agent**

```bash
python run_agent.py --questions questions.json --sources sources/ --output output/
```

This will:
1. Chunk and index all files in `sources/`
2. Retrieve the top-matching passages for each question
3. Call the Anthropic API to synthesize a cited answer per question
4. Write results to `output/cited_answers.json` and a full transcript to `output/chat_log.json`

**Step 4 — Review results**

```bash
cat output/cited_answers.json
```

Each entry includes the `answer`, the `citations` (source file + chunk number), and a `found_answer` boolean flagging whether the sources actually supported a response.

Optional flags:

```bash
python run_agent.py --questions questions.json --sources sources/ --output output/ --model claude-sonnet-4-6 --top-k 5
```

| Flag | Description | Default |
|---|---|---|
| `--model` | Anthropic model to use | `claude-sonnet-4-6` |
| `--top-k` | Number of passages retrieved per question | `4` |
| `--chunk-size` | Characters per chunk when splitting sources | `800` |

## 4. Design choices

- **Chunk-level citations, not document-level.** Sources are split into numbered chunks (`file.txt#1`, `file.txt#2`, …) so citations point to a specific passage rather than an entire document, making claims easier to verify.
- **Retrieval before generation.** The agent retrieves the top-k most relevant chunks for a question before calling the model, rather than stuffing all source text into the prompt. This keeps the context focused and reduces the chance of the model citing irrelevant passages.
- **Explicit "not found" handling.** The prompt instructs the model to say plainly when the retrieved passages don't answer the question, rather than filling gaps from its own general knowledge. This is enforced with a `found_answer` boolean in the output so it's machine-checkable, not just a sentence buried in the answer text.
- **Structured JSON output.** Answers, citations, and the found/not-found flag are returned as JSON (not free-form prose) so results can be validated, diffed, or fed into other tooling.
- **Full transcript logging.** `chat_log.json` stores the raw prompts and model responses for each question, separate from the cleaned-up `cited_answers.json`, to make debugging and auditing retrieval quality easier.

## 5. Tradeoffs and limitations

- **Retrieval is simple, not semantic-first.** Chunking and top-k retrieval work well for small, well-organized source sets but won't scale gracefully to large corpora or highly overlapping documents without a proper vector index.
- **Citation ≠ guaranteed accuracy.** The model is instructed to cite the passage it used, but citation accuracy depends on the model following instructions correctly — it's a strong mitigation against hallucination, not a hard guarantee. Spot-checking citations against source text is still recommended.
- **`found_answer` can be inconsistent.** As seen in the sample outputs above, the model occasionally sets `found_answer: true` while also stating the sources don't cover the question (or vice versa). This is a known edge case worth tightening in the prompt or adding a post-hoc consistency check.
- **No multi-hop reasoning across documents.** The agent answers well when one or two chunks directly contain the answer, but struggles with questions that require synthesizing facts scattered across many chunks or documents.
- **Single-turn only.** The agent doesn't currently support follow-up/clarifying questions within a session — each question is answered independently.
- **Cost and latency scale with question count.** Each question triggers a separate API call; large question sets will take longer and cost more. Batch processing isn't implemented yet.
