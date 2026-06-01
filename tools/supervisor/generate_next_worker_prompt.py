"""
generate_next_worker_prompt.py -- Next Worker Prompt Generator
Generates a comprehensive mega-train execution prompt from supervisor review results,
POC target matrix, gap extraction fixtures, and a structural template.

Hybrid approach:
  - Fixed sections (prohibitions, validation, verdicts) come from mega-train-template.md
  - Variable sections (trains, groups, rework items) are synthesized programmatically

Exit codes:
  0 -- prompt generated
  1 -- missing inputs
  9 -- unexpected error
"""

import argparse
import json
import re
import string
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

TEMPLATE_PATH = REPO_ROOT / ".supervisor" / "prompts" / "mega-train-template.md"

READ_BEFORE_EXECUTION = [
    "AGENTS.md",
    "GOVERNANCE.md",
    "plans/master-plan.md",
    "registry/format-registry.yaml",
    "reports/supervisor/session-resume.md",
    "reports/supervisor/latest-review.md",
    ".supervisor/policies.yaml",
    "product-capability-matrix/poc-targets.yaml",
    "CLAUDE.md",
]

TRAIN_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Group definitions -- trains are organized into these groups
GROUP_DEFS = [
    {"id": "G1", "name": "Governance + Preflight", "priority": 1},
    {"id": "G2", "name": "Rework / Repair", "priority": 2},
    {"id": "G3", "name": "Commercial .NET Product", "priority": 3},
    {"id": "G4", "name": "FOSS / Reduced Product", "priority": 4},
    {"id": "G5", "name": "Dogfood Exports", "priority": 5},
    {"id": "G6", "name": "Package / Install Proof", "priority": 6},
    {"id": "G7", "name": "State / Memory / POC Matrix", "priority": 7},
    {"id": "G8", "name": "Evidence + Supervisor Loop", "priority": 8},
]


def load_poc_targets(repo_root: Path) -> dict:
    """Load POC target matrix."""
    path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_gap_extraction(repo_root: Path) -> dict:
    """Load the most recent gap extraction fixture."""
    fixtures_dir = repo_root / ".supervisor" / "fixtures"
    if not fixtures_dir.exists():
        return {}
    gap_files = list(fixtures_dir.glob("*-poc-gap-extraction.yaml"))
    if not gap_files:
        return {}
    latest = max(gap_files, key=lambda p: p.stat().st_mtime)
    try:
        return yaml.safe_load(latest.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_template(template_path: Path = None) -> str:
    """Load the mega-train template."""
    path = template_path or TEMPLATE_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def suggest_next_sprint_id(prior_sprint_id: str) -> str:
    """Suggest next R-number from prior sprint ID."""
    m = re.search(r"R(\d+)", prior_sprint_id, re.IGNORECASE)
    if m:
        return f"R{int(m.group(1)) + 1}"
    return "RNEXT"


def detect_venv_path(repo_root: Path) -> str:
    """Detect the Python venv path."""
    venv = repo_root / ".local" / "venv"
    if (venv / "Scripts" / "python.exe").exists():
        return ".local/venv/Scripts/python"
    if (venv / "bin" / "python").exists():
        return ".local/venv/bin/python"
    return "python"


def synthesize_trains(review: dict, poc_targets: dict, gaps: dict) -> list[dict]:
    """Synthesize trains from review grades, POC targets, and gap fixtures.

    Each train is a dict with:
      letter, group, title, description, acceptance_criteria, files_touched, verification_command
    """
    trains = []
    letter_idx = 0

    def next_letter():
        nonlocal letter_idx
        if letter_idx < len(TRAIN_LETTERS):
            l = TRAIN_LETTERS[letter_idx]
            letter_idx += 1
            return l
        return f"Z{letter_idx - 25}"

    # --- G1: Governance preflight (always first) ---
    trains.append({
        "letter": next_letter(),
        "group": "G1",
        "title": "Governance Preflight",
        "description": "Read all governance files. Verify no policy violations from prior sprint. "
                       "Confirm MCP status, supervisor mode, and gate states.",
        "acceptance_criteria": [
            "All preflight files read",
            "No policy violations detected",
            "Gate states documented",
        ],
        "files_touched": ["reports/<run_id>/00-preflight.md"],
        "verification_command": "",
    })

    # --- G2: Rework trains (from review grades) ---
    rework_items = [
        g for g in review.get("item_grades", [])
        if g.get("supervisor_grade") in ("REWORK_REQUIRED", "OVERCLAIMED", "REJECTED")
    ]
    for item in rework_items:
        trains.append({
            "letter": next_letter(),
            "group": "G2",
            "title": f"Rework: {item.get('item_title', item.get('item_id', 'unknown'))}",
            "description": item.get("required_rework", "Fix issues identified in supervisor review."),
            "acceptance_criteria": [
                f"Evidence for {item['item_id']} passes supervisor inspection",
                "Tests pass for affected code",
            ],
            "files_touched": item.get("evidence_paths", []),
            "verification_command": "",
        })

    # --- G3: Commercial .NET product trains ---
    commercial = poc_targets.get("commercial_net_products", [])
    for product in commercial:
        fmt = product.get("format", "unknown")
        next_action = product.get("next_action", "")
        gate_11 = product.get("gate_11_status", "")
        dotnet_status = product.get("dotnet_status", {})

        # Find gaps for this product
        gap_report = gaps.get("poc_gap_report", {})
        product_gaps = [
            g for g in gap_report.get("capability_gaps", [])
            if fmt.lower() in g.get("product", "").lower()
            and g.get("suggested_sprint", "HOLD") != "HOLD"
        ]

        if product_gaps:
            for gap in product_gaps[:2]:  # Max 2 trains per product
                trains.append({
                    "letter": next_letter(),
                    "group": "G3",
                    "title": f"{fmt} .NET: {gap.get('capability', gap['id'])}",
                    "description": f"{gap.get('note', '')}. Status: {gap.get('current_status', 'unknown')}.",
                    "acceptance_criteria": [
                        f"New tests pass for {gap['id']}",
                        f"{fmt} .NET capability implemented or documented",
                    ],
                    "files_touched": [
                        f"src/net/{fmt.lower()}/",
                        f"tests/net/{fmt.lower()}/",
                    ],
                    "verification_command": f"dotnet test tests/net/{fmt.lower()}/ --verbosity quiet",
                })
        elif gate_11 not in ("passed", "not_applicable"):
            # Generic advancement train
            trains.append({
                "letter": next_letter(),
                "group": "G3",
                "title": f"{fmt} .NET Product Deepening",
                "description": f"Continue {fmt} commercial .NET product advancement. {next_action}",
                "acceptance_criteria": [
                    f"{fmt} .NET test count increased or new API proven",
                    f"dotnet_status in poc-targets.yaml updated",
                ],
                "files_touched": [
                    f"src/net/{fmt.lower()}/",
                    f"tests/net/{fmt.lower()}/",
                ],
                "verification_command": f"dotnet test tests/net/{fmt.lower()}/ --verbosity quiet",
            })

    # --- G4: FOSS/Reduced product trains ---
    foss = poc_targets.get("foss_reduced_products", [])
    for product in foss:
        fmt = product.get("format", "unknown")
        next_action = product.get("next_action", "")
        python_status = product.get("python_status", {})

        # Find NOT_IMPLEMENTED capabilities
        not_impl = [k for k, v in python_status.items()
                    if isinstance(v, str) and v in ("NOT_IMPLEMENTED", "PARTIAL")]

        if not_impl:
            cap = not_impl[0]
            trains.append({
                "letter": next_letter(),
                "group": "G4",
                "title": f"{fmt} Python: {cap.replace('_', ' ').title()}",
                "description": f"Implement {cap} for {fmt}. {next_action}",
                "acceptance_criteria": [
                    f"{cap} tests pass",
                    f"python_status.{cap} updated to PASS in poc-targets.yaml",
                ],
                "files_touched": [
                    f"src/python/{fmt.lower()}/",
                    f"tests/python/{fmt.lower()}/",
                ],
                "verification_command": f"python -m pytest tests/python/{fmt.lower()}/ -x -q",
            })
        else:
            trains.append({
                "letter": next_letter(),
                "group": "G4",
                "title": f"{fmt} Python Improvement",
                "description": f"Continue {fmt} FOSS product. {next_action}",
                "acceptance_criteria": [
                    f"{fmt} Python test count maintained or increased",
                ],
                "files_touched": [
                    f"src/python/{fmt.lower()}/",
                    f"tests/python/{fmt.lower()}/",
                ],
                "verification_command": f"python -m pytest tests/python/{fmt.lower()}/ -x -q",
            })

    # --- G5: Dogfood export trains ---
    dogfood_gaps = gaps.get("poc_gap_report", {}).get("dogfood_gaps", [])
    actionable_dogfood = [
        g for g in dogfood_gaps
        if g.get("suggested_sprint", "HOLD") != "HOLD"
        and g.get("current_status") != "IMPLEMENTED"
    ]
    for gap in actionable_dogfood[:2]:  # Max 2 dogfood trains
        trains.append({
            "letter": next_letter(),
            "group": "G5",
            "title": f"Dogfood: {gap.get('format', '?')} -> {gap.get('export_target', '?')}",
            "description": f"{gap.get('dogfood_blocker', '')}. Prerequisite: {gap.get('prerequisite', 'none')}.",
            "acceptance_criteria": [
                f"Export test passes using FF library",
                f"Dogfood status updated in poc-targets.yaml",
            ],
            "files_touched": [],
            "verification_command": "",
        })

    if not actionable_dogfood:
        # At least one dogfood maintenance train
        trains.append({
            "letter": next_letter(),
            "group": "G5",
            "title": "Dogfood Export Verification",
            "description": "Verify existing dogfood exports still pass. "
                           "Update dogfood-export-map.md if any new exports were added.",
            "acceptance_criteria": [
                "All existing dogfood export tests pass",
                "No regression in export chain",
            ],
            "files_touched": ["docs/export/dogfood-export-map.md"],
            "verification_command": "",
        })

    # --- G6: Package/install proof ---
    trains.append({
        "letter": next_letter(),
        "group": "G6",
        "title": "Package Build + Install Proof",
        "description": "Rebuild wheels/sdists for any changed packages. "
                       "Run installed-workflow smoke test from extracted wheel.",
        "acceptance_criteria": [
            "All changed packages rebuilt",
            "Installed import test passes",
            "Package artifacts present in evidence directory",
        ],
        "files_touched": ["packaging/"],
        "verification_command": "python -m pytest tests/evidence/ -x -q",
    })

    # --- G7: State/memory/POC matrix sync ---
    trains.append({
        "letter": next_letter(),
        "group": "G7",
        "title": "State + Memory + POC Matrix Sync",
        "description": "Update state/current-state.md, .supervisor/project-memory.md, "
                       "and product-capability-matrix/poc-targets.yaml with sprint results.",
        "acceptance_criteria": [
            "poc-targets.yaml reflects actual status (no overclaiming)",
            "state/current-state.md updated",
            "project-memory.md entry appended",
        ],
        "files_touched": [
            "state/current-state.md",
            ".supervisor/project-memory.md",
            "product-capability-matrix/poc-targets.yaml",
        ],
        "verification_command": "",
    })

    # --- G8: Evidence declaration + supervisor loop ---
    trains.append({
        "letter": next_letter(),
        "group": "G8",
        "title": "Evidence Declaration + Supervisor Autonomous-Cycle",
        "description": "Write evidence-declaration.yaml listing ALL work items. "
                       "Run autonomous-cycle. Verify session-resume.md is regenerated.",
        "acceptance_criteria": [
            "evidence-declaration.yaml written with all work items",
            "autonomous-cycle exits 0 or 3",
            "session-resume.md regenerated with current data",
            "approval-gates.md shows correct AUTONOMOUS_CONTINUE",
        ],
        "files_touched": [
            ".local/evidences/<run_id>/evidence-declaration.yaml",
            "reports/supervisor/session-resume.md",
        ],
        "verification_command": (
            "python tools/supervisor/supervisor_loop.py autonomous-cycle "
            "--declaration .local/evidences/<run_id>/evidence-declaration.yaml"
        ),
    })

    return trains


def format_train_manifest_table(trains: list[dict]) -> str:
    """Build a markdown table summarizing all trains."""
    lines = ["| Train | Group | Title |", "|-------|-------|-------|"]
    for t in trains:
        lines.append(f"| {t['letter']} | {t['group']} | {t['title']} |")
    return "\n".join(lines)


def format_train_details(trains: list[dict]) -> str:
    """Build detailed per-train sections."""
    sections = []
    current_group = None

    for t in trains:
        if t["group"] != current_group:
            current_group = t["group"]
            group_def = next((g for g in GROUP_DEFS if g["id"] == current_group), None)
            group_name = group_def["name"] if group_def else current_group
            sections.append(f"## Group {current_group}: {group_name}\n")

        sections.append(f"### Train {t['letter']}: {t['title']}\n")
        sections.append(f"{t['description']}\n")

        if t["acceptance_criteria"]:
            sections.append("**Acceptance Criteria:**")
            for criterion in t["acceptance_criteria"]:
                sections.append(f"- {criterion}")
            sections.append("")

        if t["files_touched"]:
            sections.append("**Files:**")
            for f in t["files_touched"]:
                sections.append(f"- `{f}`")
            sections.append("")

        if t["verification_command"]:
            sections.append("**Verification:**")
            sections.append(f"```bash\n{t['verification_command']}\n```")
            sections.append("")

    return "\n".join(sections)


def format_preflight_list() -> str:
    """Format the preflight file list."""
    lines = ["Read these files before writing any code:\n"]
    for i, f in enumerate(READ_BEFORE_EXECUTION, 1):
        lines.append(f"{i}. `{f}`")
    return "\n".join(lines)


def build_sprint_goal(review: dict, rework_items: list, trains: list) -> str:
    """Synthesize the sprint goal from review context."""
    rework_count = len(rework_items)
    product_trains = [t for t in trains if t["group"] in ("G3", "G4", "G5")]

    parts = []
    if rework_count > 0:
        parts.append(f"Repair {rework_count} item(s) flagged by supervisor review")
    if product_trains:
        product_names = [t["title"] for t in product_trains[:4]]
        parts.append(f"Advance product POC: {'; '.join(product_names)}")
    parts.append("Build evidence declaration and run supervisor autonomous-cycle")

    return "**Goal:** " + ". ".join(parts) + "."


def generate_prompt(review: dict, next_work: dict | None = None,
                    repo_root: Path = None) -> str:
    """Generate the mega-train execution prompt from review results and project data."""
    if repo_root is None:
        repo_root = REPO_ROOT

    # Load data sources
    poc_targets = load_poc_targets(repo_root)
    gaps = load_gap_extraction(repo_root)
    template = load_template()

    # Extract review context
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("overall_verdict", "unknown")
    autonomous = review.get("autonomous_continue", False)
    test_passed = review.get("test_results", {}).get("passed", 0)
    test_failed = review.get("test_results", {}).get("failed", 0)
    test_skipped = review.get("test_results", {}).get("skipped", 0)

    next_sprint = suggest_next_sprint_id(sprint_id)
    venv_path = detect_venv_path(repo_root)

    # Synthesize trains
    trains = synthesize_trains(review, poc_targets, gaps)

    rework_items = [
        g for g in review.get("item_grades", [])
        if g.get("supervisor_grade") in ("REWORK_REQUIRED", "OVERCLAIMED", "REJECTED")
    ]

    # Build template variables
    test_line = f"{test_passed} passed, {test_failed} failed, {test_skipped} skipped"
    sprint_goal = build_sprint_goal(review, rework_items, trains)

    # Determine .NET test command
    has_dotnet_trains = any(t["group"] == "G3" for t in trains)
    dotnet_test_cmd = "dotnet test tests/net/ --verbosity quiet" if has_dotnet_trains else "# (no .NET work this sprint)"

    if template:
        # Use template with variable substitution
        result = template.replace("{sprint_id}", next_sprint)
        result = result.replace("{timestamp}", datetime.now().isoformat())
        result = result.replace("{prior_sprint_id}", sprint_id)
        result = result.replace("{prior_verdict}", verdict)
        result = result.replace("{prior_test_line}", test_line)
        result = result.replace("{autonomous_continue}", str(autonomous))
        result = result.replace("{sprint_goal}", sprint_goal)
        result = result.replace("{preflight_file_list}", format_preflight_list())
        result = result.replace("{train_manifest_table}", format_train_manifest_table(trains))
        result = result.replace("{train_details}", format_train_details(trains))
        result = result.replace("{python_venv}", venv_path)
        result = result.replace("{dotnet_test_command}", dotnet_test_cmd)
        return result

    # Fallback: build prompt without template
    return _build_fallback_prompt(review, trains, sprint_goal, test_line,
                                  next_sprint, venv_path, dotnet_test_cmd)


def _build_fallback_prompt(review, trains, sprint_goal, test_line,
                           next_sprint, venv_path, dotnet_test_cmd):
    """Build prompt when template file is not available."""
    lines = []
    lines.append(f"# FORMAT-FACTORY-{next_sprint}-MEGA-TRAIN-001")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Prior Sprint: {review.get('sprint_id', 'unknown')}")
    lines.append(f"Prior Verdict: {review.get('overall_verdict', 'unknown')}")
    lines.append(f"Tests: {test_line}")
    lines.append("")
    lines.append(sprint_goal)
    lines.append("")

    lines.append("## Preflight")
    lines.append(format_preflight_list())
    lines.append("")

    lines.append("## Train Manifest")
    lines.append(format_train_manifest_table(trains))
    lines.append("")

    lines.append(format_train_details(trains))

    lines.append("## Hard Prohibitions")
    lines.append("- No git push without explicit user authorization.")
    lines.append("- No git commit without explicit user authorization.")
    lines.append("- No Gate 8 or Gate 11 approval.")
    lines.append("- No commercial_product_ready: true.")
    lines.append("- No PyPI/NuGet/GitHub release publication.")
    lines.append("- No paid external AI API or web automation.")
    lines.append("- No MCP activation unless MODE 4 already authorized.")
    lines.append("- No destructive git operations.")
    lines.append("- No PENDING markers in final state files.")
    lines.append("")

    lines.append("## Final Validation Sequence")
    lines.append(f"1. `{venv_path} -m pytest tests/ -x -q --tb=short`")
    lines.append(f"2. `{venv_path} -m py_compile tools/supervisor/autonomous_cycle.py`")
    lines.append(f"3. `{dotnet_test_cmd}`")
    lines.append(f"4. Write evidence-declaration.yaml")
    lines.append(f"5. Run autonomous-cycle")
    lines.append("")

    lines.append("## Evidence Declaration Requirements")
    lines.append("At sprint end, create `.local/evidences/<run_id>/evidence-declaration.yaml`")
    lines.append("Then run:")
    lines.append(f"```")
    lines.append(f"{venv_path} tools/supervisor/supervisor_loop.py autonomous-cycle \\")
    lines.append(f"  --declaration .local/evidences/<run_id>/evidence-declaration.yaml")
    lines.append(f"```")
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

    # Product-factory forward work from POC targets
    poc_targets = load_poc_targets(REPO_ROOT)
    for product in poc_targets.get("commercial_net_products", []):
        fmt = product.get("format", "unknown")
        items.append({
            "item_id": f"PRODUCT-{fmt.upper()}",
            "title": f"Advance {fmt} commercial .NET product",
            "lane": "product-advancement",
            "priority": priority,
            "description": product.get("next_action", f"Continue {fmt} product deepening"),
            "acceptance_criteria": "Test count increased, new APIs or features proven",
            "verification_command": "",
            "evidence_expected": "Test results, code changes",
            "source": "product-factory",
        })
        priority += 1

    for product in poc_targets.get("foss_reduced_products", []):
        fmt = product.get("format", "unknown")
        items.append({
            "item_id": f"FOSS-{fmt.upper()}",
            "title": f"Advance {fmt} FOSS product",
            "lane": "product-advancement",
            "priority": priority,
            "description": product.get("next_action", f"Continue {fmt} FOSS work"),
            "acceptance_criteria": "Test count maintained or increased",
            "verification_command": "",
            "evidence_expected": "Test results",
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
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repository root")
    args = parser.parse_args()

    if not args.review.exists():
        print(f"ERROR: Review not found: {args.review}", file=sys.stderr)
        return 1

    review = json.loads(args.review.read_text(encoding="utf-8"))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate prompt
    prompt = generate_prompt(review, repo_root=args.repo_root)
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
    print(f"  Train count: {len(prompt.splitlines())} lines in mega-train prompt")

    return 0


if __name__ == "__main__":
    sys.exit(main())
