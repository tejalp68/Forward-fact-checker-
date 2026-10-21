# Forward Fact-Checker

A multi-agent system built with LangGraph. Paste a suspicious WhatsApp forward and it pulls out the claims, checks each one on the web, reviews the evidence, gives a verdict, asks for your approval, and drafts a polite reply for the family group.

```
uv run main.py "Drinking hot lemon water every morning cures cancer. Forward to everyone!"
```

## Graph

```
              START
                │
                ▼
            extract
                │
                │  send_to_verify()  ── fan-out with Send
    ┌───────────┼───────────┐
    ▼           ▼           ▼
 verify      verify      verify       one node instance per claim
    └───────────┼───────────┘
                │                     fan-in via merge_evidence reducer
                ▼
             review
                │
                │  after_review()
       ┌────────┴────────┐
       │                 │
weak and             all strong or
attempts < 2         out of attempts
       │                 │
       ▼                 ▼
verify (only          verdict
weak ones)               │
       │                 ▼
       └──► review    approval        interrupt() pauses the graph
                         │
                         │  after_approval()
                  ┌──────┴──────┐
                 yes            no
                  │             │
                  ▼             ▼
                reply          END
                  │
                  ▼
                 END
```

## Nodes

| Node       | Type                   | Reads                 | Writes                              |
| ---------- | ---------------------- | --------------------- | ----------------------------------- |
| `extract`  | LLM, structured output | `forward`             | `claims`                            |
| `verify`   | LLM + Tavily search    | `VerifyTask`          | `evidence[claim]`                   |
| `review`   | LLM, structured output | `evidence`            | `rejected`, `feedback`, `attempts`  |
| `verdict`  | LLM, structured output | `forward`, `evidence` | `verdict`, `explanation`, `sources` |
| `approval` | Human (`interrupt`)    | verdict, explanation  | `approved`                          |
| `reply`    | LLM, structured output | verdict, explanation  | `reply`                             |

## Verdicts

`true`, `false`, `misleading`, or `unverified` when the evidence does not settle it.

## Design Decisions

- **Sources come from the search tool, not the LLM.** The verifier only says which numbered results it used, so links cannot be made up.
- **The reply agent writes only the message.** Code appends the source links.
- **Targeted retries.** Only claims with weak evidence are searched again, with the reviewer's feedback.
- **Bounded loop.** `MAX_REVIEWS = 2` stops the reviewer from looping forever.
- **Replies match the forward's language.** Hindi and Marathi forwards get Hindi and Marathi replies.

## File Structure

```
fact-checker/
├── main.py              CLI entry. Runs the graph, handles the approval pause and resume
├── graph.py             Nodes, edges, routing functions, checkpointer
├── state.py             Shared State, Evidence, VerifyTask, merge_evidence reducer
├── config.py            Loads .env and constants
├── llm.py               Shared Gemini client
├── tools.py             web_search() via Tavily
├── agents/
│   ├── extractor.py     Claim extractor
│   ├── verifier.py      Verifier with web search
│   ├── reviewer.py      Evidence reviewer
│   ├── judge.py         Verdict agent
│   ├── approval.py      Human approval with interrupt()
│   └── replier.py       Reply drafter
├── .env.example
└── pyproject.toml
```

## Setup

```
cd fact-checker
uv sync
cp .env.example .env
```

Fill in `.env`:

- `GOOGLE_API_KEY` from [AI Studio](https://aistudio.google.com/apikey)
- `TAVILY_API_KEY` from [Tavily](https://app.tavily.com)

Run with text or a file:

```
uv run main.py "paste the forward here"
uv run main.py forward.txt
```

## Build Steps

| Step     | Adds                               |
| -------- | ---------------------------------- |
| `step-0` | Setup and key check                |
| `step-1` | State and claim extractor          |
| `step-2` | One verifier with web search       |
| `step-3` | Parallel verifiers with `Send`     |
| `step-4` | Evidence reviewer and retry loop   |
| `step-5` | Verdict, approval, and reply draft |

## Stack

LangGraph, Gemini, Tavily, uv
