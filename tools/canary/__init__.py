"""tools/canary — Canary Control for Format Factory governance.

Implements staged promotion paths for portfolio-wide blast-radius operations:
- validator_promotion: shadow new governance validators before portfolio-wide rollout
- grader_promotion: shadow LLM grader provider switches
- compilation_diff: preview gap-ledger compilation priority changes before applying

Mission: clever-tickling-island
"""
from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["validator_promotion", "grader_promotion", "compilation_diff"]
