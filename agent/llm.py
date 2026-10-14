import os
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

PROMPTS_FILE = Path(__file__).parent / "prompts.yaml"
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

client = OpenAI()


class Decision(BaseModel):
    action: Literal["move_on", "clarify", "redirect"]
    line: str


def load_prompts():
    with open(PROMPTS_FILE) as f:
        return yaml.safe_load(f)


def decide(question, exchange):
    """Return the model's action and line for the latest candidate message.

    exchange is the talk about the current question only:
    a list of {"role": "candidate" | "interviewer", "text": str}.
    """
    prompts = load_prompts()
    actions = prompts["actions"]
    instructions = prompts["interviewer"].format(
        question=question,
        actions="\n".join(f"- {a}" for a in actions.values()),
    )

    messages = [
        {"role": "user" if m["role"] == "candidate" else "assistant", "content": m["text"]}
        for m in exchange
    ]

    response = client.responses.parse(
        model=MODEL,
        instructions=instructions,
        input=messages,
        text_format=Decision,
    )
    return response.output_parsed
