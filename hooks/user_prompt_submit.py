#!/usr/bin/env python3
"""Remind Root turns to apply the active Diverter Session Contract."""

import json
import sys


TURN_REMINDER = (
    "Mandatory turn preflight: Before any user-visible message or task work, "
    "apply the active Diverter "
    "Session Contract to this prompt and deliberate the task shape before "
    "deciding. Native Proactive Delegation ownership is a terminal silent bypass. "
    "Otherwise, if eligible or the Contract is missing, load $diverter silently "
    "and make its routing receipt the first user-visible output. "
    "For an ordinary ROOT_ONLY decision, emit exactly one "
    "`Routing: ROOT_ONLY — <one task-shape reason>` receipt; keep bypass, "
    "explicit opt-out, and native unavailability silent. The first routing "
    "result is final for this prompt; never re-route after task work starts."
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
