from pydantic import BaseModel

from config import MAX_CLAIMS
from llm import llm


class Claims(BaseModel):
    claims: list[str]


def extract_claims(state):
    prompt = f"""Read this forwarded message and list the factual claims in it that can be checked.

Rules:
- Ignore greetings, opinions, blessings and requests like "forward to everyone".
- Write each claim as one short sentence that makes sense on its own.
- Return at most {MAX_CLAIMS} claims, most important first.
- If nothing can be checked, return an empty list.

Message:
{state["forward"]}"""
    result = llm.with_structured_output(Claims).invoke(prompt)
    return {
        "claims": result.claims[:MAX_CLAIMS],
        "rejected": [],
        "feedback": {},
        "attempts": 0,
    }
