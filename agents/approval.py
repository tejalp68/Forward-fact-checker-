from langgraph.types import interrupt


def ask_approval(state):
    answer = interrupt(
        {
            "verdict": state["verdict"],
            "explanation": state["explanation"],
            "sources": state["sources"],
            "evidence": {
                claim: e["stance"] for claim, e in state["evidence"].items()
            },
        }
    )
    return {"approved": answer == "yes"}
