#!/usr/bin/env python3
"""Remind Root turns to apply the active Diverter Session Contract."""

import json
import sys


TURN_REMINDER = (
    "Mandatory turn preflight: Before any user-visible message or task work, "
    "apply the active Diverter "
    "Session Contract to this prompt and deliberate the task shape before "
    "deciding. Native Proactive Delegation ownership is a terminal silent bypass. "
    "Otherwise, load $diverter silently only when eligible and make its routing "
    "receipt the first user-visible output. If ROOT_ONLY, continue silently "
    "without mentioning routing or internal checks. A silent ROOT_ONLY may be "
    "reconsidered once only after clarification or lightweight read-only discovery "
    "materially changes the task shape before implementation."
)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeError):
        return

    if isinstance(event, dict) and "agent_id" not in event:
        print(TURN_REMINDER)


if __name__ == "__main__":
    main()
