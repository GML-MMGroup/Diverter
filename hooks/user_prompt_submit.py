#!/usr/bin/env python3
"""Remind Root turns to apply the active Diverter Session Contract."""

import json
import sys


TURN_REMINDER = (
    "Mandatory turn preflight: Before task work, apply the active Diverter "
    "Session Contract to this prompt. If eligible or the Contract is missing, "
    "load $diverter first; otherwise continue silently in Root."
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
