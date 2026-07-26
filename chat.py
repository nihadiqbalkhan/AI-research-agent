"""Step 5: the agent as an interactive loop.

    User Input -> Fetch relevant passages -> Send prompt+context to the
    model -> Receive answer -> Display answer -> (optional) save result

Usage:
    python chat.py
Type a question, get a cited answer, repeat. Type 'quit' to exit.
Every exchange is appended to output/chat_log.json.
"""
import json
from pathlib import Path

from research_agent.env import load_dotenv
load_dotenv()

from research_agent.agent import ResearchAgent

ROOT = Path(__file__).parent
SOURCES_DIR = ROOT / "sources"
LOG_FILE = ROOT / "output" / "chat_log.json"


def load_log() -> list:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []


def save_log(log: list) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, indent=2))


def main():
    agent = ResearchAgent(SOURCES_DIR)
    log = load_log()

    print("Research Agent (with Citations)")
    print(f"Loaded {len(agent.passages)} passages from {SOURCES_DIR}/")
    print("Ask a question, or type 'quit' to exit.\n")

    while True:
        question = input("What's your question? > ").strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break

        result = agent.ask(question)

        print(f"\n{result.answer}\n")
        print(f"Cited passages: {result.citations}")
        print(f"Found answer in sources: {result.found_answer}\n")

        log.append({
            "question": result.question,
            "answer": result.answer,
            "citations": result.citations,
            "found_answer": result.found_answer,
        })
        save_log(log)

    print(f"\nSaved {len(log)} exchange(s) to {LOG_FILE}")


if __name__ == "__main__":
    main()
