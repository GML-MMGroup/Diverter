#!/usr/bin/env python3
"""Inject the Diverter Session Contract into a root Codex session."""

import json
import os
from pathlib import Path


CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "diverter"
    / "references"
    / "session-contract.md"
)


def load_policy() -> str:
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    path = codex_home / "diverter" / "config.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        policy = data.get("delegation_policy") if isinstance(data, dict) else None
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
        return "ask"
    return policy if policy in {"ask", "auto"} else "ask"


def build_contract(policy: str) -> str:
    contract = CONTRACT_PATH.read_text(encoding="utf-8").rstrip()
    return f"{contract}\n\ndelegation_policy: {policy}\n"


if __name__ == "__main__":
    print(build_contract(load_policy()), end="")
