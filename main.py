"""Command line entry point. Runs the graph and handles the approval step."""

import os
import sys
import uuid

from langgraph.types import Command

from graph import graph


def read_forward():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, encoding="utf-8") as f:
                return f.read()
        return arg
    return input("Paste the forward: ")


def show_verdict(payload):
    print("\nClaims checked")
    for claim, stance in payload["evidence"].items():
        print(f"  - {claim} ({stance})")
    print(f"\nVerdict: {payload['verdict'].upper()}")
    print(payload["explanation"])
    print("\nSources")
    for url in payload["sources"]:
        print(f"  {url}")


def main():
    forward = read_forward()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result = graph.invoke({"forward": forward}, config)

    if "__interrupt__" not in result:
        print("\nNo checkable claims found in this message.")
        return

    show_verdict(result["__interrupt__"][0].value)
    answer = input("\nDraft a reply based on this verdict? (yes/no): ").strip().lower()
    result = graph.invoke(Command(resume=answer), config)

    if result.get("reply"):
        print("\nReply for the group\n")
        print(result["reply"])
    else:
        print("\nStopped. No reply drafted.")


if __name__ == "__main__":
    main()