import json
import random
import sys
from pathlib import Path

import yaml

from llm import decide

DATA_DIR = Path(__file__).parent.parent / "data"

INTRO_FILE = Path(__file__).parent / "intro.yaml"
LINES_FILE = Path(__file__).parent / "lines.yaml"

# Attempts the candidate gets after their first answer, whether Neo clarifies or redirects
MAX_FOLLOW_UPS = 2


def load_intro():
    with open(INTRO_FILE) as f:
        return yaml.safe_load(f)


def load_lines():
    with open(LINES_FILE) as f:
        return yaml.safe_load(f)


def load_questions(role_file):
    with open(DATA_DIR / role_file) as f:
        return json.load(f)


def greet(candidate_name, role, num_questions):
    intro = load_intro()
    print(intro["greeting"].format(candidate_name=candidate_name, role=role, num_questions=num_questions))
    print(intro["rules_header"])
    for rule in intro["rules"]:
        print(f"- {rule}")
    print()
    input(intro["ready_prompt"])
    print()


def ask_question(question):
    """Talk with the candidate about one question until the model moves on."""
    exchange = []
    for attempt in range(MAX_FOLLOW_UPS + 1):
        exchange.append({"role": "candidate", "text": input("> ")})

        # Last attempt always moves on, so use a fixed acknowledgement instead of an LLM call
        if attempt == MAX_FOLLOW_UPS:
            line = random.choice(load_lines()["acknowledgements"])
            exchange.append({"role": "interviewer", "text": line, "action": "move_on"})
            print(f"Neo: {line}")
            break

        decision = decide(question, exchange)
        exchange.append({"role": "interviewer", "text": decision.line, "action": decision.action})
        print(f"Neo: {decision.line}")

        if decision.action == "move_on":
            break

    return exchange


def run_interview(role_file, candidate_name):
    data = load_questions(role_file)
    questions = data["questions"]
    transcript = []

    greet(candidate_name, data["role"], len(questions))

    for i, q in enumerate(questions, start=1):
        print(f"Question {i}/{len(questions)}: {q['question']}")
        exchange = ask_question(q["question"])
        transcript.append({"id": q["id"], "question": q["question"], "exchange": exchange})
        print()

    print("That's the end of the interview. Thank you!")
    return transcript


if __name__ == "__main__":
    role_file = sys.argv[1] if len(sys.argv) > 1 else "associate_ai_engineer.json"
    candidate_name = sys.argv[2] if len(sys.argv) > 2 else "John"
    run_interview(role_file, candidate_name)
