"""Run the research agent over questions.json and write cited answers to
output/cited_answers.json.

Usage:
    python run.py
"""
import json
from pathlib import Path

from research_agent.env import load_dotenv
load_dotenv()

from research_agent.agent import ResearchAgent, CitedAnswer

ROOT = Path(__file__).parent
SOURCES_DIR = ROOT / "sources"
QUESTIONS_FILE = ROOT / "questions.json"
OUTPUT_FILE = ROOT / "output" / "cited_answers.json"


def answer_to_dict(a: CitedAnswer) -> dict:
    return {
        "question": a.question,
        "answer": a.answer,
        "citations": a.citations,
        "found_answer": a.found_answer,
    }


def main():
    agent = ResearchAgent(SOURCES_DIR)
    questions = json.loads(QUESTIONS_FILE.read_text())

    results = []
    for q in questions:
        result = agent.ask(q)
        results.append(answer_to_dict(result))
        print(f"Q: {q}")
        print(f"A: {result.answer}")
        print(f"Cited passages: {result.citations}")
        print(f"Found answer in sources: {result.found_answer}")
        print("-" * 80)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"\nSaved {len(results)} cited answers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
