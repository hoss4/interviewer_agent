# Interviewer Agent

AI agent that runs first-round technical interviews as a text chatbot.

## Setup

```bash
uv sync
uv run main.py
```

## Data

`data/` holds example question sets, one JSON file per role. Each question has:

- `topic`: short phrase used in transitions ("Let's move on to {topic}").
- `question`: shown to the candidate word for word.
- `key_points`: what a good answer covers. Used only by the evaluation step, never by the live agent.
