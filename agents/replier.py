from pydantic import BaseModel

from llm import llm


class Reply(BaseModel):
    message: str


def draft_reply(state):
    prompt = f"""Write a short WhatsApp reply to a family group that shared this forward.

Forward:
{state["forward"]}

Verdict: {state["verdict"]}
Why: {state["explanation"]}

Rules:
- Use the same language and script as the forward (English, Hindi, Marathi, or whatever it is).
- Be warm and polite. Never blame or shame the person who shared it.
- Say clearly what is true and what is not, and what people should do instead.
- Keep it to five sentences or fewer.
- Do not add links, they are added separately."""
    result = llm.with_structured_output(Reply).invoke(prompt)

    text = result.message
    if state["sources"]:
        text += "\n\nSources:\n" + "\n".join(state["sources"][:3])
    return {"reply": text}
