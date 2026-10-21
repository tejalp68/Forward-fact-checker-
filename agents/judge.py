from typing import Literal

from pydantic import BaseModel

from llm import llm


class Verdict(BaseModel):
    verdict: Literal["true", "false", "misleading", "unverified"]
    explanation: str


def give_verdict(state):
    lines = "\n".join(
        f"- {claim}: {e['stance']}. {e['summary']}"
        for claim, e in state["evidence"].items()
    )
    prompt = f"""Give one overall verdict for this forwarded message.

Message:
{state["forward"]}

Evidence for each claim:
{lines}

Verdict rules:
- true: every important claim is supported
- false: the main claim is contradicted
- misleading: some claims are true but the message is wrong, exaggerated or missing key context
- unverified: the evidence does not settle the main claim

Write the explanation in three simple sentences that anyone in a family group can follow."""
    result = llm.with_structured_output(Verdict).invoke(prompt)

    sources = list(
        dict.fromkeys(
            url for e in state["evidence"].values() for url in e["sources"]
        )
    )
    return {
        "verdict": result.verdict,
        "explanation": result.explanation,
        "sources": sources,
    }
