"""Connects all the agents into one graph and decides which step runs next."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy, Send

from agents.approval import ask_approval
from agents.extractor import extract_claims
from agents.judge import give_verdict
from agents.replier import draft_reply
from agents.reviewer import review_evidence
from agents.verifier import verify_claim
from config import MAX_REVIEWS
from state import State


def send_to_verify(state):
    if not state["claims"]:
        return END
    return [Send("verify", {"claim": c, "feedback": ""}) for c in state["claims"]]


def after_review(state):
    if state["rejected"] and state["attempts"] < MAX_REVIEWS:
        return [
            Send("verify", {"claim": c, "feedback": state["feedback"].get(c, "")})
            for c in state["rejected"]
        ]
    return "verdict"


def after_approval(state):
    return "reply" if state["approved"] else END


builder = StateGraph(State)

builder.add_node("extract", extract_claims)
builder.add_node("verify", verify_claim, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node("review", review_evidence)
builder.add_node("verdict", give_verdict)
builder.add_node("approval", ask_approval)
builder.add_node("reply", draft_reply)

builder.add_edge(START, "extract")
builder.add_conditional_edges("extract", send_to_verify)
builder.add_edge("verify", "review")
builder.add_conditional_edges("review", after_review)
builder.add_edge("verdict", "approval")
builder.add_conditional_edges("approval", after_approval)
builder.add_edge("reply", END)

graph = builder.compile(checkpointer=InMemorySaver())