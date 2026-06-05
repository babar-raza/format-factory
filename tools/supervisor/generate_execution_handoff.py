"""Generate structured execution handoff documents for unmatched product gaps.

When no governed skill exists for a gap, this tool produces a handoff YAML
that constrains the worker agent with:
- allowed/forbidden file paths
- required tests and evidence outputs
- rollback instructions
- capability matrix update requirements
- safety gates

v2 improvements (R101):
- implementation_steps: ordered work steps
- stop_conditions: when to abort
- evidence_declaration_entries: pre-built declaration snippet
- purpose field
- source_track classification
- raw_logs path
- product_code_ledger path
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from choose_skill_or_handoff import classify_source_track


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

TRACK_FILE_RULES = {
    "commercial_net": {
        "allowed_src": ["src/net/{format}/"],
        "allowed_tests": ["tests/net/{format}/"],
        "forbidden": ["src/python/", "tools/supervisor/"],
    },
    "foss_reduced": {
        "allowed_src": ["src/python/{format}/"],
        "allowed_tests": ["tests/python/{format}/"],
        "forbidden": ["src/net/", "tools/supervisor/"],
    },
}

DEFAULT_SAFETY_GATES = [
    "No src/* changes outside allowed paths",
    "All new tests must pass before closing",
    "Update poc-targets.yaml capability status",
    "Write lane execution ledger entry",
    "No git push or commit without human approval",
]


def generate_handoff(
    gap: dict[str, Any],
    sprint_id: str = "unknown",
) -> dict[str, Any]:
    """Generate a structured execution handoff for one gap."""
    track = gap.get("product_track", "foss_reduced")
    fmt = gap.get("format", "unknown").lower()
    cap = gap.get("capability_path", "unknown")
    work_type = gap.get("work_type", "unknown")
    decision = gap.get("decision", "GOVERNED_HANDOFF_REQUIRED")

    file_rules = TRACK_FILE_RULES.get(track, TRACK_FILE_RULES["foss_reduced"])
    allowed_src = [p.format(format=fmt) for p in file_rules["allowed_src"]]
    allowed_tests = [p.format(format=fmt) for p in file_rules["allowed_tests"]]
    forbidden = list(file_rules["forbidden"])

    evidence_outputs = [
        f"reports/{sprint_id.lower()[:20]}/handoff-{fmt}-{cap.replace('.', '-')}.md",
        f".local/evidences/{sprint_id}/evidence-declaration.yaml",
    ]

    rollback = f"git checkout -- {' '.join(allowed_src + allowed_tests)}"

    tests_required = []
    if work_type == "product_source_change":
        tests_required.append(f"New unit tests in {allowed_tests[0]}")
        tests_required.append("Existing test suite must pass with no regressions")
    elif work_type == "test_only_change":
        tests_required.append(f"New test file in {allowed_tests[0]}")
    elif work_type == "package_proof":
        tests_required.append("pip install --no-deps wheel smoke test")
        tests_required.append("import proof log captured")
    elif work_type == "dogfood_export":
        tests_required.append("End-to-end export test with fixture file")
        tests_required.append("Output diff against reference")
    else:
        tests_required.append(f"At least one test in {allowed_tests[0]}")

    matrix_update = {
        "file": "product-capability-matrix/poc-targets.yaml",
        "path": cap,
        "expected_transition": f"{gap.get('current_status', '?')} -> DONE or PARTIAL",
    }

    # Implementation steps based on work type
    impl_steps = []
    if work_type == "product_source_change":
        impl_steps = [
            f"1. Read existing source in {allowed_src[0]}",
            f"2. Implement {cap} capability",
            f"3. Add tests in {allowed_tests[0]}",
            "4. Run full test suite — no regressions",
            "5. Update product-code-change-ledger.json",
            "6. Update poc-targets.yaml capability status",
        ]
    elif work_type == "test_only_change":
        impl_steps = [
            f"1. Create test file in {allowed_tests[0]}",
            "2. Run tests — all pass",
        ]
    elif work_type == "dogfood_export":
        impl_steps = [
            f"1. Implement export in {allowed_src[0]}",
            f"2. Add export tests in {allowed_tests[0]}",
            "3. Verify output against fixture",
            "4. Update dogfood_status in poc-targets.yaml",
        ]
    else:
        impl_steps = [f"1. Implement changes in {allowed_src[0]}", "2. Add tests", "3. Verify"]

    stop_conditions = [
        "Test suite fails",
        "Files modified outside allowed_files",
        "Gate or release state change needed",
        "Scope exceeds single capability",
    ]

    evidence_declaration_entries = [
        {
            "item_id": f"{sprint_id}-{fmt}-{cap.replace('.', '-')}",
            "title": f"{fmt} {cap} implementation",
            "status": "completed",
            "evidence_paths": evidence_outputs,
        }
    ]

    source_track = gap.get("source_track", classify_source_track(gap) if "product_track" in gap else "unknown")

    return {
        "handoff_id": f"handoff-{fmt}-{cap.replace('.', '-')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "purpose": f"Implement {cap} for {fmt} ({track})",
        "gap_id": gap.get("gap_id", ""),
        "format": fmt,
        "product_track": track,
        "source_track": source_track,
        "capability_path": cap,
        "work_type": work_type,
        "decision": decision,
        "allowed_files": allowed_src + allowed_tests,
        "forbidden_files": forbidden,
        "implementation_steps": impl_steps,
        "tests_required": tests_required,
        "raw_logs": [f".local/supervisor/raw-logs/handoff-{fmt}-{cap.replace('.', '-')}.log"],
        "product_code_ledger": "reports/r90/product-code-change-ledger.json",
        "rollback": rollback,
        "evidence_outputs": evidence_outputs,
        "evidence_declaration_entries": evidence_declaration_entries,
        "ledger_requirements": [
            "Record lane start via record_lane_execution.py start",
            "Record lane close with files_changed and test counts",
        ],
        "capability_matrix_update": matrix_update,
        "stop_conditions": stop_conditions,
        "safety_gates": DEFAULT_SAFETY_GATES,
    }


def generate_handoffs_for_gaps(
    gaps: list[dict[str, Any]],
    sprint_id: str = "unknown",
) -> list[dict[str, Any]]:
    """Generate handoffs for all gaps that require handoff."""
    handoffs = []
    for gap in gaps:
        decision = gap.get("decision", "")
        if decision in ("GOVERNED_HANDOFF_REQUIRED", "NEED_PLAN_HARDENING"):
            handoffs.append(generate_handoff(gap, sprint_id))
    return handoffs


def write_handoffs(
    gaps_path: Path,
    output_dir: Path,
    sprint_id: str = "unknown",
) -> dict[str, Any]:
    """Load gaps, generate handoffs, write YAML files."""
    data = json.loads(gaps_path.read_text(encoding="utf-8"))
    gaps = data.get("selected_gaps", data if isinstance(data, list) else [])
    handoffs = generate_handoffs_for_gaps(gaps, sprint_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for h in handoffs:
        path = output_dir / f"{h['handoff_id']}.yaml"
        path.write_text(yaml.dump(h, default_flow_style=False, sort_keys=False), encoding="utf-8")
        written.append(str(path))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "total_gaps": len(gaps),
        "handoffs_generated": len(handoffs),
        "files_written": written,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaps", type=Path, required=True, help="selected-product-gaps.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sprint-id", default="unknown")
    args = parser.parse_args()

    result = write_handoffs(args.gaps, args.output_dir, args.sprint_id)
    print(f"HANDOFFS_GENERATED: {result['handoffs_generated']}")
    for f in result["files_written"]:
        print(f"  {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
