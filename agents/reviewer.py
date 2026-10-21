from pydantic import BaseModel

from llm import llm


class Review(BaseModel):
    number: int
    strong: bool
    feedback: str


class Reviews(BaseModel):
    reviews: list[Review]


def review_evidence(state):
    to_review = state["rejected"] or state["claims"]

    items = []
    for number, claim in enumerate(to_review, 1):
        e = state["evidence"][claim]
        items.append(
            f"{number}. Claim: {claim}\n"
            f"   Stance: {e['stance']}\n"
            f"   Summary: {e['summary']}\n"
            f"   Sources: {len(e['sources'])}"
        )

    prompt = f"""You are a strict reviewer of fact-checking work.

For each item decide if the evidence is strong enough to give a verdict.
Strong means at least one reliable source clearly speaks to the claim.
Weak means the stance is unclear, there are no sources, or the sources do not match the claim.
If weak, say in one sentence what kind of search would fix it.

{chr(10).join(items)}"""
    result = llm.with_structured_output(Reviews).invoke(prompt)

    rejected = []
    feedback = {}
    for review in result.reviews:
        if not review.strong and 0 < review.number <= len(to_review):
            claim = to_review[review.number - 1]
            rejected.append(claim)
            feedback[claim] = review.feedback

    return {
        "rejected": rejected,
        "feedback": feedback,
        "attempts": state["attempts"] + 1,
    }
