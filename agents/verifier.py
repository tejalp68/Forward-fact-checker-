from typing import Literal

from pydantic import BaseModel

from llm import llm
from tools import web_search


class Query(BaseModel):
    query: str


class Finding(BaseModel):
    stance: Literal["supported", "contradicted", "unclear"]
    summary: str
    used: list[int]


def build_query(claim, feedback):
    if not feedback:
        return f"{claim} fact check"
    prompt = f"""Write one short web search query to check this claim.

Claim: {claim}
Problem with the earlier search: {feedback}"""
    return llm.with_structured_output(Query).invoke(prompt).query


def verify_claim(task):
    claim = task["claim"]
    query = build_query(claim, task["feedback"])
    results = web_search(query)

    pages = "\n\n".join(
        f"[{i}] {r['title']} ({r['url']})\n{r['content']}"
        for i, r in enumerate(results, 1)
    )
    prompt = f"""Check this claim using only the search results below.

Claim: {claim}

Search results:
{pages}

Answer with:
- stance: supported, contradicted, or unclear if the results do not settle it
- summary: two sentences on what the results say about the claim
- used: the numbers of the results you relied on"""
    finding = llm.with_structured_output(Finding).invoke(prompt)

    sources = [
        results[i - 1]["url"] for i in finding.used if 0 < i <= len(results)
    ]
    evidence = {
        "stance": finding.stance,
        "summary": finding.summary,
        "sources": sources,
    }
    return {"evidence": {claim: evidence}}
