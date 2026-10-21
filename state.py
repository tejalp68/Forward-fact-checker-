from typing import Annotated, TypedDict


class Evidence(TypedDict):
    stance: str
    summary: str
    sources: list[str]


class VerifyTask(TypedDict):
    claim: str
    feedback: str


def merge_evidence(old, new):
    return {**(old or {}), **new}


class State(TypedDict):
    forward: str
    claims: list[str]
    evidence: Annotated[dict[str, Evidence], merge_evidence]
    rejected: list[str]
    feedback: dict[str, str]
    attempts: int
    verdict: str
    explanation: str
    sources: list[str]
    approved: bool
    reply: str
