"""
tools/governance/check_docs_placement.py — Documentation Placement Validator

Enforces the documentation root-placement policy defined in
docs/governance/documentation-placement-policy.yaml.

Exit codes:
  0 — all checks pass
  1 — one or more violations found

Usage:
  python tools/governance/check_docs_placement.py [--full] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_ROOT = REPO_ROOT / "docs"

ROOT_ALLOWLIST = {
    "README.md",
    "agent-methodology-index.md",
    "planning-methodology.md",
    "agent-execution-handoff-standard.md",
    "plan-hardening-checklist.md",
    "fresh-chat-continuity-brief.md",
    "gates.md",
    "spec-to-feature-correction-plan-summary.md",
}

STUB_ALLOWLIST = {
    "acquisition-workflow.md",
    "architecture.md",
    "current-state-and-evidence-authority.md",
    "legal-and-licensing.md",
    "release-control.md",
    "security.md",
    "specification-cache.md",
}


def check_stub(path: Path) -> list[str]:
    """Validate a stub file."""
    errors = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > 50:
        errors.append(f"STUB_TOO_LARGE: {path.name} has {len(lines)} lines (max 50)")
    if "stub_metadata:" not in text and "DEPRECATED" not in text:
        errors.append(f"STUB_MISSING_METADATA: {path.name} lacks stub_metadata block")
    if "canonical_path:" not in text:
        errors.append(f"STUB_MISSING_CANONICAL: {path.name} lacks canonical_path field")
    # Check canonical exists
    import re
    m = re.search(r"canonical_path:\s*(.+)", text)
    if m:
        canonical = m.group(1).strip()
        canonical_path = REPO_ROOT / canonical
        if not canonical_path.exists():
            errors.append(f"CANONICAL_MISSING: {canonical} does not exist (stub: {path.name})")
    return errors


def run_checks(full: bool = False) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check 1: No unallowlisted files at docs/ root
    for path in sorted(DOCS_ROOT.iterdir()):
        if path.is_dir():
            continue
        name = path.name
        if name in ROOT_ALLOWLIST:
            continue
        if name in STUB_ALLOWLIST:
            # Check 2: Stubs must be valid
            stub_errors = check_stub(path)
            errors.extend(stub_errors)
            continue
        # File at root that's not in allowlist and not a known stub
        errors.append(f"UNALLOWLISTED_ROOT_FILE: docs/{name} is not in root allowlist or stub allowlist")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check documentation placement policy")
    parser.add_argument("--full", action="store_true", help="Full repository check")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    errors, warnings = run_checks(full=args.full)

    if args.json:
        result = {
            "pass": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
        }
        print(json.dumps(result, indent=2))
    else:
        if errors:
            for e in errors:
                print(f"[FAIL] {e}")
            print(f"\n{len(errors)} violation(s) found.")
        else:
            print("[PASS] Documentation placement policy satisfied.")
            if warnings:
                for w in warnings:
                    print(f"[WARN] {w}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
