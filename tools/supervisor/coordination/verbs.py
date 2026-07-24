"""Canonical coordination verb set -- the provider-parity source of truth.

AGENTS.md Section CO, docs/governance/codex-adapter.md and
docs/governance/kilo-adapter.md must reference exactly these verbs;
validator V194 parses those documents against this list.
"""

VERBS = (
    "register",
    "status",
    "who",           # alias of status
    "claim",
    "check",
    "preflight",
    "heartbeat",
    "release",
    "complete",
    "abandon",
    "record-write",
    "conflicts",
    "takeover",
    "precommit-check",
    "guard-run",
    "mode",
    "doctor",
)

# Verbs every provider adapter MUST document as mandatory protocol steps.
REQUIRED_ADAPTER_VERBS = (
    "register",
    "claim",
    "preflight",
    "record-write",
    "heartbeat",
    "release",
    "complete",
)
