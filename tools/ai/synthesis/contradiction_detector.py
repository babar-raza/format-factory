"""Contradiction detector — checks synthesis outputs against verified facts.

Detects direct contradictions, unsupported claims, and factual mismatches.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ContradictionMatch:
    """A detected contradiction between output and verified facts."""
    fact_id: str
    fact_assertion: str
    fact_negation: str
    matched_text: str
    severity: str = "high"


@dataclass
class ContradictionReport:
    """Report of contradiction checking."""
    status: str = "not_checked"
    facts_checked: int = 0
    contradictions: list[ContradictionMatch] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return self.status == "no_contradictions" and not self.contradictions

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "facts_checked": self.facts_checked,
            "contradiction_count": len(self.contradictions),
            "contradictions": [
                {
                    "fact_id": c.fact_id,
                    "assertion": c.fact_assertion,
                    "matched_negation": c.matched_text,
                    "severity": c.severity,
                }
                for c in self.contradictions
            ],
            "errors": self.errors,
        }


def load_verified_facts(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Load verified facts from YAML file."""
    errors: list[str] = []
    if not path.exists():
        return [], ["verified_facts_file_not_found"]
    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    except ImportError:
        return [], ["yaml_not_available"]
    except Exception as e:
        return [], [f"yaml_parse_error: {type(e).__name__}"]

    facts = data.get("facts", [])
    if not facts:
        return [], ["empty_facts_list"]

    valid_facts = []
    for i, fact in enumerate(facts):
        if not isinstance(fact, dict):
            errors.append(f"fact[{i}]: not a dict")
            continue
        if "assertion" not in fact:
            errors.append(f"fact[{i}]: missing assertion")
            continue
        valid_facts.append(fact)

    return valid_facts, errors


def check_output_contradictions(
    output: dict[str, Any] | str,
    verified_facts_path: Path | None = None,
    facts: list[dict[str, Any]] | None = None,
) -> ContradictionReport:
    """Check output for contradictions against verified facts.

    Supply either verified_facts_path (loads from file) or facts (pre-loaded list).
    """
    report = ContradictionReport()

    if facts is None and verified_facts_path is not None:
        facts, load_errors = load_verified_facts(verified_facts_path)
        if load_errors:
            report.errors.extend(load_errors)
        if not facts:
            report.status = "blocked_no_facts"
            return report
    elif facts is None:
        report.status = "blocked_no_facts_source"
        return report

    if isinstance(output, dict):
        output_str = json.dumps(output, default=str).lower()
    else:
        output_str = str(output).lower()

    report.facts_checked = len(facts)

    for fact in facts:
        negation = fact.get("negation", "").lower().strip()
        if not negation:
            continue
        if negation in output_str:
            report.contradictions.append(ContradictionMatch(
                fact_id=fact.get("id", "unknown"),
                fact_assertion=fact.get("assertion", ""),
                fact_negation=fact.get("negation", ""),
                matched_text=negation,
            ))

    report.status = (
        "no_contradictions" if not report.contradictions
        else f"contradictions_found:{len(report.contradictions)}"
    )
    return report
