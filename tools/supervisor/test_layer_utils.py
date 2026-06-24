"""Shared utilities for test-layer adequacy checking.

Used by:
- tools/supervisor/sprint_executor_validate.py (declaration validation)
- tools/supervisor/grade_declared_work.py (item grading)

Created: 2026-06-23, TC-FSLAY02-SHARED-001
"""
from __future__ import annotations

import datetime as _datetime
from fnmatch import fnmatch
from pathlib import Path

_MANIFEST_PATH = Path(__file__).resolve().parent.parent.parent / "registry" / "test-layer-manifest.yaml"

# Date after which test_layer adequacy warnings escalate to errors for ALL item types
ADEQUACY_ESCALATION_DATE = _datetime.date(2026, 7, 18)

# Item types that trigger immediate enforcement (before escalation date)
PRODUCT_ITEM_TYPES = frozenset({"PRODUCT_SOURCE", "PRODUCT_TEST"})


def load_change_impact_rules(manifest_path: Path | None = None) -> list[dict]:
    """Load change_impact rules from the test-layer manifest.

    Returns empty list on failure (caller should skip adequacy check).
    """
    try:
        import yaml
        p = manifest_path or _MANIFEST_PATH
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("change_impact", [])
    except Exception:
        return []


def compute_required_layer(changed_files: list[str], rules: list[dict]) -> tuple[int, list[str]]:
    """Compute minimum required test layer from changed files and manifest rules.

    Returns (max_required_layer, list_of_triggering_files_with_reasons).
    Returns (0, []) if changed_files is empty or rules is empty.
    """
    if not changed_files or not rules:
        return 0, []

    max_layer = 0
    triggers: list[str] = []

    for f in changed_files:
        f_norm = f.replace("\\", "/")
        matched = False
        for rule in rules:
            pat = rule.get("pattern", "")
            if pat == "_default":
                if not matched:
                    layer = rule.get("min_layer", 6)
                    if layer > max_layer:
                        max_layer = layer
                        triggers.append(f"{f_norm} -> default rule (layer {layer})")
                break
            if fnmatch(f_norm, pat):
                layer = rule.get("min_layer", 0)
                if layer > max_layer:
                    max_layer = layer
                    triggers.append(f"{f_norm} -> '{pat}' (layer {layer})")
                matched = True
                break

    return max_layer, triggers


def is_escalation_active() -> bool:
    """Check whether the adequacy escalation date has passed."""
    return _datetime.date.today() >= ADEQUACY_ESCALATION_DATE
