"""Step 2: verify you have working access to an AI model.

Works with either provider — whichever API key you've set. Run this after
`pip install -r requirements.txt` and after setting an API key. It sends
one test message and prints the reply. If you see a response printed
below, the hardest part of setup is done and you can move on to `run.py`
or `chat.py`.

Usage (pick one):
    export ANTHROPIC_API_KEY=your-key-here
    python test_connection.py

    export OPENAI_API_KEY=your-key-here
    python test_connection.py
"""
import os
import sys

from research_agent.env import load_dotenv
load_dotenv()


def main():
    from research_agent.llm import get_active_provider, get_active_model

    provider = get_active_provider()
    if not provider:
        print("No API key found.")
        print("Set ONE of the following, then re-run this script:")
        print("  export ANTHROPIC_API_KEY=your-key-here   (Claude)")
        print("  export OPENAI_API_KEY=your-key-here      (OpenAI)")
        sys.exit(1)

    model = get_active_model()
    print(f"Provider: {provider}")
    print(f"Sending a test message to {model} ...")

    if provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            print("The `anthropic` package isn't installed. Run: pip install -r requirements.txt")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Reply with a short one-sentence hello."}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")

    else:  # openai
        try:
            import openai
        except ImportError:
            print("The `openai` package isn't installed. Run: pip install -r requirements.txt")
            sys.exit(1)
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Reply with a short one-sentence hello."}],
        )
        text = response.choices[0].message.content

    print("\nResponse received:")
    print(text)
    print("\nSetup is working. You can now run: python run.py")


if __name__ == "__main__":
    main()
