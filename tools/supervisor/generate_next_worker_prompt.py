"""
generate_next_worker_prompt.py — Next Worker Prompt Generator
Generates a comprehensive next-worker prompt from supervisor review results,
including rework lanes, product-factory advancement, and evidence requirements.

Exit codes:
  0 — prompt generated
  1 — missing inputs
  9 — unexpected error
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Product-factory priorities from R85+ policies
PRODUCT_FACTORY_TARGETS = {
    "commercial_net": ["FODS", "FODT", "Netpbm/QOI"],
    "foss_reduced": ["ZST", "PBM/PGM/PPM", "SYLK/DIF"],
    "dogfood_exports": {
        "FODS": "CSV/HTML table",
        "FODT": "TXT/Markdown/HTML",
        "QOI/Netpbm": "PPM/PGM/PBM",
        "SYLK/DIF": "CSV",
    },
}

READ_BEFORE_EXECUTION = [
    "AGENTS.md",
    "GOVERNANCE.md",
    "plans/master-plan.md",
    "registry/format-registry.yaml",
    "reports/supervisor/session-resume.md",
    "reports/supervisor/latest-review.md",
    ".supervisor/policies.yaml",
]


def generate_prompt(review: dict, next_work: dict | None = None) -> str:
    """Generate the next worker prompt from review results."""
    run_id = review.get("run_id", "unknown")
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("overall_verdict", "unknown")
    autonomous = review.get("autonomous_continue", False)
    rework_items = [g for g in review.get("item_grades", []) if g["supervisor_grade"] in ("REWORK_REQUIRED", "OVERCLAIMED")]
    accepted_items = [g for g in review.get("item_grades", []) if g["supervisor_grade"] in ("ACCEPTED", "ACCEPTED_WITH_WARNINGS")]
    blocked_items = [g for g in review.get("item_grades", []) if g["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"]

    lines = []

    # Header
    lines.append(f"# Next Worker Prompt")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Previous Sprint: {sprint_id}")
    lines.append(f"Previous Verdict: {verdict}")
    lines.append(f"Previous Run: {run_id}")
    lines.append(f"Autonomous Continue: {autonomous}")
    lines.append("")

    # Read-before-execution
    lines.append("## Read Before Execution")
    lines.append("Read these files before taking any action:")
    for doc in READ_BEFORE_EXECUTION:
        lines.append(f"- {doc}")
    lines.append("")

    # Previous accepted items
    if accepted_items:
        lines.append("## Previously Accepted Items")
        for g in accepted_items:
            lines.append(f"- {g['item_id']}: {g['item_title']} ({g['supervisor_grade']})")
        lines.append("")

    # Rework lane
    if rework_items:
        lines.append("## Rework Lane (Priority 1)")
        lines.append("These items failed review and must be fixed before new work:")
        for g in rework_items:
            lines.append(f"### {g['item_id']}: {g['item_title']}")
            lines.append(f"- Grade: {g['supervisor_grade']}")
            lines.append(f"- Required rework: {g.get('required_rework', 'See review')}")
            if g.get("next_prompt_instruction"):
                lines.append(f"- Instruction: {g['next_prompt_instruction']}")
            lines.append("")

    # System-healing lane
    lines.append("## System-Healing Lane (Priority 2)")
    lines.append("Fix any system-level defects blocking automation:")
    lines.append("- Ensure supervisor tools compile: `python -m py_compile tools/supervisor/*.py`")
    lines.append("- Ensure tests pass: `python -m pytest tests/supervisor/ -v --tb=short`")
    lines.append("")

    # Product-advancement lane
    lines.append("## Product-Advancement Lane (Priority 3)")
    lines.append("Advance Format Factory product work:")
    lines.append(f"- Commercial .NET targets: {', '.join(PRODUCT_FACTORY_TARGETS['commercial_net'])}")
    lines.append(f"- FOSS/reduced targets: {', '.join(PRODUCT_FACTORY_TARGETS['foss_reduced'])}")
    lines.append("- Dogfood exports:")
    for fmt, target in PRODUCT_FACTORY_TARGETS["dogfood_exports"].items():
        lines.append(f"  - {fmt} -> {target}")
    lines.append("- Evidence is support rail, not the main product")
    lines.append("")

    # Evidence-hardening lane
    lines.append("## Evidence-Hardening Lane (Priority 4)")
    lines.append("- Ensure evidence directory is complete and validates")
    lines.append("- Run `python tools/supervisor/supervisor_loop.py validate-declaration --declaration <path>`")
    lines.append("")

    # State/taskcard/memory sync
    lines.append("## State/Taskcard/Memory Sync Lane (Priority 5)")
    lines.append("- Update taskcards if present")
    lines.append("- Update state/current-state.md if changed")
    lines.append("- Memory sync handled by supervisor after review")
    lines.append("")

    # Verification lane
    lines.append("## Independent Verification Lane (Priority 6)")
    lines.append("- Run all tests: `python -m pytest tests/ -v --tb=short`")
    lines.append("- Compile check: `python -m py_compile tools/supervisor/*.py`")
    lines.append("")

    # Blocked items (informational)
    if blocked_items:
        lines.append("## Blocked Items (Do Not Attempt)")
        for g in blocked_items:
            lines.append(f"- {g['item_id']}: {g['item_title']} (BLOCKED_EXTERNAL_GATE)")
        lines.append("")

    # Hard prohibitions
    lines.append("## Hard Prohibitions")
    lines.append("- No git push")
    lines.append("- No PyPI/NuGet/GitHub release publication")
    lines.append("- No Gate 8 or Gate 11 approval")
    lines.append("- No commercial_product_ready=true")
    lines.append("- No paid external AI API or web automation")
    lines.append("- No MCP activation unless already authorized")
    lines.append("- No destructive git cleanup")
    lines.append("")

    # Final evidence declaration requirements
    lines.append("## Final Evidence Declaration Requirements")
    lines.append("At sprint end, create:")
    lines.append("- `.local/evidences/<run_id>/evidence-declaration.yaml`")
    lines.append("- `.local/evidences/<run_id>/evidence-manifest.yaml`")
    lines.append("- Include all evidence artifacts, test results, and changed files")
    lines.append("- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>`")
    lines.append("")

    return "\n".join(lines)


def generate_next_work_items(review: dict) -> dict:
    """Generate next-work-items.yaml from review."""
    items = []
    priority = 1

    # Rework items first
    for g in review.get("item_grades", []):
        if g["supervisor_grade"] in ("REWORK_REQUIRED", "OVERCLAIMED"):
            items.append({
                "item_id": f"REWORK-{g['item_id']}",
                "title": f"Rework: {g['item_title']}",
                "lane": "rework",
                "priority": priority,
                "description": g.get("required_rework", ""),
                "acceptance_criteria": "Evidence found and tests pass",
                "verification_command": "",
                "evidence_expected": f"Evidence at declared paths for {g['item_id']}",
                "source": "rework-from-prior",
            })
            priority += 1

    # Product-factory forward work
    for target in PRODUCT_FACTORY_TARGETS["commercial_net"]:
        items.append({
            "item_id": f"PRODUCT-{target.replace('/', '-')}",
            "title": f"Advance {target} commercial .NET product",
            "lane": "product-advancement",
            "priority": priority,
            "description": f"Continue {target} product deepening per master plan",
            "acceptance_criteria": "Test count increased, new APIs or features proven",
            "verification_command": "",
            "evidence_expected": "Test results, code changes",
            "source": "product-factory",
        })
        priority += 1

    return {
        "run_id": review.get("run_id", "unknown"),
        "sprint_id": review.get("sprint_id", "unknown"),
        "generated_at": datetime.now().isoformat(),
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate next worker prompt")
    parser.add_argument("--review", type=Path, required=True, help="Path to supervisor-review.json")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    if not args.review.exists():
        print(f"ERROR: Review not found: {args.review}", file=sys.stderr)
        return 1

    review = json.loads(args.review.read_text(encoding="utf-8"))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate prompt
    prompt = generate_prompt(review)
    prompt_path = args.output_dir / "combined-next-worker-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    # Generate next work items
    next_work = generate_next_work_items(review)
    work_path = args.output_dir / "next-work-items.yaml"
    work_path.write_text(yaml.dump(next_work, default_flow_style=False, sort_keys=False), encoding="utf-8")
    (args.output_dir / "next-work-items.json").write_text(json.dumps(next_work, indent=2), encoding="utf-8")

    print(f"PROMPT_GENERATED: {prompt_path}")
    print(f"NEXT_WORK_ITEMS: {work_path}")
    print(f"  Rework items: {len([i for i in next_work['items'] if i['lane'] == 'rework'])}")
    print(f"  Product items: {len([i for i in next_work['items'] if i['lane'] == 'product-advancement'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
