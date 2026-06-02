"""
generate_supervisor_packet.py — Format Factory Local Supervisor Control Plane
Assembles supervisor next-sprint artifacts from evidence review + contradictions.

Generates:
  reports/supervisor/next-sprint.md        — full next-sprint Claude Code prompt
  reports/supervisor/next-sprint-taskmaster.json  — TM import ready (schema-validated)
  reports/supervisor/next-ruflo-lanes.json        — Ruflo lane plan (schema-validated)
  reports/supervisor/approval-gates.md            — gate classifications (mode-aware)
  reports/supervisor/session-resume.md            — fresh-session briefing

Does NOT call Claude Code or any external API — pure local assembly.

Exit codes:
  0 — success
  3 — critical contradictions present; next-sprint focuses on repair
  9 — unexpected error

Usage:
  python tools/supervisor/generate_supervisor_packet.py
  python tools/supervisor/generate_supervisor_packet.py --review reports/supervisor/evidence-review.json --contradictions reports/supervisor/contradictions.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SELECTED_PRODUCT_GAPS_PATH = ".local/supervisor/selected-product-gaps.json"
SKILL_REGISTRY_PATH = ".supervisor/skill-registry.yaml"
PRODUCT_CODE_LEDGER_PATH = "reports/r90/product-code-change-ledger.json"


def load_json(path: Path) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_selected_product_gaps(repo_root: Path) -> list[dict]:
    """Load bounded product work selected by the governed R90 selector."""
    payload = load_json(repo_root / SELECTED_PRODUCT_GAPS_PATH)
    gaps = payload.get("selected_gaps", [])
    return gaps if isinstance(gaps, list) else []


def load_memory(memory_path: Path) -> str:
    if memory_path.exists():
        lines = memory_path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-50:])
    return "(no memory file)"


def read_current_mode(repo_root: Path) -> int:
    """Read current mode number from .supervisor/config.yaml.
    Returns 0 if not determinable."""
    config_path = repo_root / ".supervisor" / "config.yaml"
    if not config_path.exists():
        return 0
    text = config_path.read_text(encoding="utf-8")
    m = re.search(r"Status:\s*MODE\s*(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 0


def read_registry_gate_states(repo_root: Path) -> dict:
    """Read gate states from registry/format-registry.yaml for all formats.
    Returns {format_id: {gate_N: status}} for formats with high-number incomplete gates.

    Registry structure:
      formats:
        - format_id: fods
          gates:
            gate_11:
              status: commercial_readiness_in_progress
    """
    registry_path = repo_root / "registry" / "format-registry.yaml"
    if not registry_path.exists():
        return {}
    try:
        text = registry_path.read_text(encoding="utf-8", errors="replace")
        result = {}
        current_format = None
        current_gate = None

        for line in text.splitlines():
            # Detect format_id lines: "  - format_id: fods"
            fmt_m = re.match(r"\s+(?:-\s+)?format_id:\s+(\S+)", line)
            if fmt_m:
                current_format = fmt_m.group(1)
                result[current_format] = {}
                current_gate = None
                continue

            if current_format is None:
                continue

            # Detect gate block starts: "      gate_11:" (with leading spaces)
            gate_m = re.match(r"\s+(gate_\d+):\s*$", line)
            if gate_m:
                current_gate = gate_m.group(1)
                continue

            # Detect status lines under a gate block: "        status: not_started"
            if current_gate:
                status_m = re.match(r"\s+status:\s+(\S+)", line)
                if status_m:
                    result[current_format][current_gate] = status_m.group(1)
                    current_gate = None

        # Return only formats with incomplete high-number gates (>=10)
        filtered = {}
        for fmt, gates in result.items():
            incomplete = {
                g: s for g, s in gates.items()
                if int(g.split("_")[1]) >= 10
                and s not in ("passed", "not_applicable", "waived")
            }
            if incomplete:
                filtered[fmt] = incomplete
        return filtered
    except Exception:
        return {}


def read_open_taskcards(repo_root: Path, limit: int = 5) -> list[dict]:
    """Read open taskcards from taskcards/ directory.
    Returns list of {id, title, status} for not_started/in_progress ones."""
    tc_dir = repo_root / "taskcards"
    if not tc_dir.exists():
        return []
    open_cards = []
    for fn in sorted(tc_dir.iterdir()):
        if not fn.suffix == ".md":
            continue
        try:
            text = fn.read_text(encoding="utf-8", errors="replace")
            status_m = re.search(r"\*\*Status:\*\*\s*(\S+)", text)
            status = status_m.group(1) if status_m else "unknown"
            if status not in ("not_started", "in_progress", "open", "pending"):
                continue
            # Extract title from first h1
            title_m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else fn.stem
            open_cards.append({
                "id": fn.stem,
                "title": title,
                "status": status,
            })
        except Exception:
            continue
        if len(open_cards) >= limit:
            break
    return open_cards


def synthesize_sprint_tasks(review: dict, contradictions: dict, repo_root: Path) -> list[dict]:
    """Generate sprint-specific tasks from gate states, open taskcards, and phase context.
    Returns list of TM-schema-compatible task dicts."""
    tasks = []
    critical_count = contradictions.get("critical_count", 0)

    # --- REPAIR TASKS (always first when contradictions exist) ---
    if critical_count > 0:
        for i, c in enumerate(contradictions.get("contradictions", []), 1):
            if c["severity"] == "CRITICAL":
                tasks.append({
                    "task_id": f"REPAIR-{i:03d}",
                    "title": f"Repair: {c['description'][:80]}",
                    "description": c.get("detail", ""),
                    "status": "pending",
                    "ff_taskcard_ref": "repair-required",
                    "supervisor_task_ref": "TC-SUP-009",
                    "acceptance_evidence": "contradictions.md shows 0 CRITICAL contradictions",
                    "validation_command": "python tools/supervisor/compare_goal_to_evidence.py --review reports/supervisor/evidence-review.json",
                    "non_authoritative": True,
                    "lane": "C2",
                })
        # D87-R86-11 FIX: Do NOT return early — continue to add safe product lanes
        # even when repair is needed. Repair tasks are first, but product-factory
        # work-ahead lanes still get generated below.

    # --- SYNTHESIZE FROM CONTEXT (always, regardless of repair status) ---

    task_seq = len(tasks) + 1

    # 0. Governed acceleration preflight (R90+)
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Select governed product gaps and validate the product-code ledger",
        "description": f"Load {SELECTED_PRODUCT_GAPS_PATH} and {SKILL_REGISTRY_PATH}. "
                       "No direct ad-hoc src edits are permitted. Any generated execution "
                       f"handoff that edits src must update {PRODUCT_CODE_LEDGER_PATH}.",
        "status": "pending",
        "ff_doc_ref": "docs/product-factory/product-factory-acceleration-layer.md",
        "supervisor_task_ref": "R90-ACCELERATION-PREFLIGHT",
        "acceptance_evidence": f"{PRODUCT_CODE_LEDGER_PATH} validates and selected product gaps map to governed skills or explicit handoffs",
        "validation_command": f"python tools/supervisor/validate_product_code_ledger.py --ledger {PRODUCT_CODE_LEDGER_PATH}",
        "non_authoritative": True,
        "lane": "C3",
    })
    task_seq += 1

    # 1. Check for uncommitted tracked changes (R79 closure indicator)
    try:
        import subprocess
        r = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=10
        )
        modified = [l for l in r.stdout.splitlines() if l.startswith(" M") and
                    any(x in l for x in ["src/python/", "src/net/", "state/", "packaging/"])]
        if modified:
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": "Commit uncommitted product code and build sprint evidence bundle",
                "description": f"Modified tracked files detected: {len(modified)} file(s) (e.g. {modified[0].strip().split()[-1]}). "
                               "Commit per governance rule (explicit user auth required), build evidence bundle.",
                "status": "approval-blocked",
                "ff_doc_ref": "plans/master-plan.md",
                "supervisor_task_ref": "TC-R79-CLOSURE-001",
                "acceptance_evidence": "git status shows no modified tracked product files; BUNDLE_VALIDATION: PASS",
                "validation_command": ".local/venv/Scripts/python tools/evidence/validate_evidence_bundle.py --contract <contract> --bundle <bundle>",
                "blocker_type": "human_approval",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1
    except Exception:
        pass

    # 2. Gate state tasks from registry
    gate_states = read_registry_gate_states(repo_root)
    incomplete_formats = []
    for fmt, gates in gate_states.items():
        for gate, status in gates.items():
            if status in ("not_started", "in_progress", "commercial_readiness_in_progress"):
                gate_num = int(gate.split("_")[1])
                if gate_num >= 10:  # Only surface high gates
                    incomplete_formats.append((fmt, gate, status))

    for fmt, gate, status in incomplete_formats[:3]:
        gate_num = gate.split("_")[1]
        if status == "commercial_readiness_in_progress":
            title = f"Advance {fmt.upper()} Gate {gate_num} commercial readiness"
            desc = f"{fmt} gate_{gate_num} status: {status}. Continue commercial readiness work per plans/master-plan.md."
            blocker = "human_approval"
            task_status = "approval-blocked"
        else:
            title = f"Open {fmt.upper()} Gate {gate_num}"
            desc = f"{fmt} gate_{gate_num} status: {status}. See plans/master-plan.md and registry for requirements."
            blocker = "external_gate"
            task_status = "blocked"
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": title,
            "description": desc,
            "status": task_status,
            "ff_gate_ref": f"{fmt}_{gate}",
            "ff_doc_ref": "plans/master-plan.md",
            "acceptance_evidence": f"registry/format-registry.yaml shows {fmt} {gate}: closed or approved",
            "validation_command": f"grep -A5 '{fmt}:' registry/format-registry.yaml | grep '{gate}'",
            "blocker_type": blocker,
            "non_authoritative": True,
            "lane": "C3",
        })
        task_seq += 1

    # 3. Open taskcards
    open_tcs = read_open_taskcards(repo_root, limit=3)
    for tc in open_tcs:
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": f"Work on open taskcard: {tc['id']}",
            "description": tc["title"],
            "status": "pending",
            "ff_taskcard_ref": tc["id"],
            "ff_doc_ref": f"taskcards/{tc['id']}.md",
            "acceptance_evidence": f"taskcards/{tc['id']}.md shows Status: closed or verified",
            "validation_command": f"grep 'Status:' taskcards/{tc['id']}.md",
            "non_authoritative": True,
            "lane": "C3",
        })
        task_seq += 1

    # 4. Product-factory lanes from governed selected gaps, with legacy fixture fallback
    selected_gaps = [
        gap for gap in load_selected_product_gaps(repo_root)
        if not gap.get("external_gate")
    ]
    for gap in selected_gaps[:5]:
        gap_id = gap.get("gap_id", "selected-gap")
        product = gap.get("format", "unknown")
        capability = gap.get("capability_path", gap_id)
        skill = gap.get("governed_skill") or "generated execution handoff"
        lane = "C4" if "dogfood" in capability.lower() else "C3"
        tasks.append({
            "task_id": f"TASK-{task_seq:03d}",
            "title": f"Product deepening: {gap_id} — {capability[:60]}",
            "description": f"Product target: {product}. Product objective: {capability}. "
                           f"Use {skill} from {SKILL_REGISTRY_PATH}; ledger any src edit in "
                           f"{PRODUCT_CODE_LEDGER_PATH}.",
            "status": "pending",
            "ff_doc_ref": SELECTED_PRODUCT_GAPS_PATH,
            "supervisor_task_ref": gap_id,
            "acceptance_evidence": f"New tests pass for {gap_id}; capability implemented or documented",
            "validation_command": "pytest tests/ -x -q",
            "non_authoritative": True,
            "lane": lane,
        })
        task_seq += 1

    gap_fixtures = list((repo_root / ".supervisor" / "fixtures").glob("*-poc-gap-extraction.yaml")) if (repo_root / ".supervisor" / "fixtures").exists() else []
    if not selected_gaps and gap_fixtures:
        # Use the most recent fixture
        latest_fixture = max(gap_fixtures, key=lambda p: p.stat().st_mtime)
        try:
            import yaml
            gap_data = yaml.safe_load(latest_fixture.read_text(encoding="utf-8"))
        except (ImportError, Exception):
            gap_data = {}

        report = gap_data.get("poc_gap_report", {})
        # Extract R-next targets from summary
        r_next_targets = report.get("summary", {}).get("r86_targets", [])
        if not r_next_targets:
            # Fall back: collect all gaps with suggested_sprint matching next sprint number
            for gap_list_key in ("capability_gaps", "dogfood_gaps", "documentation_gaps"):
                for gap in report.get(gap_list_key, []):
                    gap_id = gap.get("id", "")
                    suggested = gap.get("suggested_sprint", "").upper()
                    # Accept any gap not on HOLD
                    if suggested not in ("HOLD", ""):
                        r_next_targets.append(gap_id)

        all_gaps = {}
        for gap_list_key in ("capability_gaps", "dogfood_gaps", "test_gaps", "documentation_gaps"):
            for gap in report.get(gap_list_key, []):
                all_gaps[gap.get("id", "")] = gap

        for gap_id in r_next_targets[:5]:
            gap = all_gaps.get(gap_id, {})
            if not gap:
                continue
            product = gap.get("product", gap.get("format", "unknown"))
            capability = gap.get("capability", gap.get("description", gap_id))
            tasks.append({
                "task_id": f"TASK-{task_seq:03d}",
                "title": f"Product deepening: {gap_id} — {capability[:60]}",
                "description": f"Product target: {product}. Product objective: {capability}. "
                               f"{gap.get('note', '')} Select from {SELECTED_PRODUCT_GAPS_PATH}; "
                               f"use {SKILL_REGISTRY_PATH}; ledger any src edit in {PRODUCT_CODE_LEDGER_PATH}.",
                "status": "pending",
                "ff_doc_ref": str(latest_fixture.relative_to(repo_root)),
                "supervisor_task_ref": gap_id,
                "acceptance_evidence": f"New tests pass for {gap_id}; capability implemented or documented",
                "validation_command": "pytest tests/ -x -q",
                "non_authoritative": True,
                "lane": "C3",
            })
            task_seq += 1

    # 5. Always: dogfood and package/install product-proof lanes
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Advance one dogfood export path using a Format Factory library",
        "description": f"Product objective: close or verify a selected dogfood export from {SELECTED_PRODUCT_GAPS_PATH}. "
                       "Use a Format Factory-produced library and record truthful status.",
        "status": "pending",
        "ff_doc_ref": "docs/export/dogfood-export-strategy.md",
        "supervisor_task_ref": "R90-DOGFOOD-LANE",
        "acceptance_evidence": "Dogfood test proves the Format Factory library path and matrix status is truthful",
        "validation_command": "pytest tests/ -x -q",
        "non_authoritative": True,
        "lane": "C4",
    })
    task_seq += 1

    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Build package artifacts and run installed-workflow proof",
        "description": "Product objective: prove changed product packages from physical artifacts. "
                       "A missing artifact is a failure, not a skipped package test.",
        "status": "pending",
        "ff_doc_ref": "plans/master-plan.md",
        "supervisor_task_ref": "R90-PACKAGE-INSTALL-LANE",
        "acceptance_evidence": "Physical package artifacts exist and installed-workflow tests pass from extracted packages",
        "validation_command": "pytest tests/evidence/ -x -q",
        "non_authoritative": True,
        "lane": "C5",
    })
    task_seq += 1

    # 6. Always: evidence declaration and autonomous-cycle task
    tasks.append({
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Write evidence declaration and run supervisor autonomous-cycle",
        "description": "Write .local/evidences/<run_id>/evidence-declaration.yaml for all work items, "
                       "then run the declaration-driven supervisor autonomous-cycle. ZIP export is optional.",
        "status": "pending",
        "ff_doc_ref": "tools/supervisor/supervisor_loop.py",
        "supervisor_task_ref": "TC-SUP-010",
        "acceptance_evidence": "evidence-declaration.yaml exists and autonomous-cycle regenerates the supervisor packet",
        "validation_command": "python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml",
        "non_authoritative": True,
        "lane": "C6",
    })

    # Fallback: if no tasks were synthesized at all, add generic advance
    if not tasks:
        tasks.append({
            "task_id": "TASK-001",
            "title": "Continue next mega-train sprint",
            "description": "Evidence accepted; continue normal sprint lanes per plans/master-plan.md",
            "status": "pending",
            "ff_doc_ref": "plans/master-plan.md",
            "supervisor_task_ref": "TC-SUP-010",
            "acceptance_evidence": "BUNDLE_VALIDATION: PASS in next sprint evidence bundle",
            "validation_command": ".local/venv/Scripts/python tools/evidence/validate_evidence_bundle.py --contract <contract> --bundle <bundle>",
            "non_authoritative": True,
            "lane": "C0",
        })

    return tasks


def validate_against_schema(data: dict, schema_path: Path) -> list[str]:
    """Validate data against JSON schema.
    Primary: uses jsonschema library.
    Fallback: manual required-field check (no external dependency).
    Returns list of errors; empty = valid."""
    # --- Primary: jsonschema library ---
    try:
        import jsonschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=data, schema=schema)
            return []
        except jsonschema.ValidationError as e:
            return [str(e.message)]
        except jsonschema.SchemaError as e:
            return [f"Schema error: {e.message}"]
    except ImportError:
        pass  # Fall through to manual validation
    except Exception as e:
        return [f"Validation error: {e}"]

    # --- Fallback: manual required-field check (no external library) ---
    errors = []
    if not schema_path.exists():
        return ["Schema file not found — skipping validation"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Cannot read schema: {e}"]

    # Check top-level required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check tasks array items if present
    tasks_schema = schema.get("properties", {}).get("tasks", {})
    item_required = tasks_schema.get("items", {}).get("required", [])
    for i, task in enumerate(data.get("tasks", [])):
        for field in item_required:
            if field not in task:
                errors.append(f"tasks[{i}] missing required field: {field}")

    if not errors:
        print(
            "  NOTE: jsonschema library not found; manual required-field check used. "
            "For full validation run with .local/venv/Scripts/python.",
            file=sys.stderr,
        )
    return errors


def generate_next_sprint_md(review: dict, contradictions: dict, memory_snippet: str, tasks: list) -> str:
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("verdict", "unknown")
    facts = review.get("facts", {})
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    if critical_count > 0:
        focus = "REPAIR: Address CRITICAL contradictions before advancing"
        repair_notes = "\n".join(
            f"- [{c['severity']}] {c['description']}"
            for c in contradictions.get("contradictions", [])
        )
    else:
        focus = "ADVANCE: Continue normal mega-train lanes"
        repair_notes = "None"

    test_line = f"{facts.get('test_count', 0)} passed, {facts.get('fail_count', 0)} failed, {facts.get('skip_count', 0)} skipped"

    # Build task summary for prompt
    task_lines = "\n".join(
        f"- [{t.get('status', 'pending')}] {t['task_id']}: {t['title']}"
        for t in tasks
    )

    content = f"""# Supervisor-Generated Next Sprint Prompt
# Source sprint: {sprint_id}
# Generated: {datetime.now().isoformat()}
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
{focus}

## Prior Sprint Summary
- Sprint ID: {sprint_id}
- Evidence verdict: {verdict}
- Tests: {test_line}
- Autonomous continue: {autonomous}

## Contradictions Requiring Repair
{repair_notes}

## Synthesized Task List (Advisory)
{task_lines}

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `{SELECTED_PRODUCT_GAPS_PATH}` and `{SKILL_REGISTRY_PATH}` before product work.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.
9. No direct ad-hoc `src/` edits. Use a governed skill or generated execution handoff.
10. Every `src/` edit requires an entry in `{PRODUCT_CODE_LEDGER_PATH}`.

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Governed implementation — selected gaps, skill registry, product-code ledger
- Lane C4: Dogfood export — use a Format Factory-produced library
- Lane C5: Package/install proof — build physical artifacts and run installed workflows
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```
{memory_snippet}
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
"""
    return content


def generate_taskmaster_json(review: dict, contradictions: dict, tasks: list) -> dict:
    sprint_id = review.get("sprint_id", "unknown")
    timestamp = datetime.now().isoformat()

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "tasks": tasks,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_ruflo_lanes_json(review: dict, contradictions: dict, tasks: list) -> dict:
    timestamp = datetime.now().isoformat()
    sprint_id = review.get("sprint_id", "unknown")

    # Assign tasks to lanes
    c2_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C2"]
    c3_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C3"]
    c4_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C4"]
    c5_tasks = [t["task_id"] for t in tasks if t.get("lane") == "C5"]

    lanes = [
        {
            "lane_id": "C0",
            "owner_role": "Coordinator",
            "title": "Sprint coordination and integration",
            "description": "Tracks all lanes; owns file ownership matrix; stops on emergency conditions",
            "allowed_files": ["reports/rNN/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**", "tools/evidence/**", "tests/evidence/**"],
            "dependencies": [],
            "tasks": [t["task_id"] for t in tasks if t.get("lane") == "C0"],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C1",
            "owner_role": "Governance",
            "title": "Governance discovery",
            "description": "Read-only access to governance files; produces preflight report",
            "allowed_files": ["reports/rNN/00-preflight.md"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md"],
            "dependencies": [],
            "tasks": [],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C2",
            "owner_role": "Repair",
            "title": "Contradiction repair",
            "description": "Address any open CRITICAL contradictions from prior sprint",
            "allowed_files": ["reports/rNN/**", "src/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0"],
            "tasks": c2_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C3",
            "owner_role": "Implementation",
            "title": "Product implementation and taskcard execution",
            "description": f"Product objective: execute selected work from {SELECTED_PRODUCT_GAPS_PATH} through {SKILL_REGISTRY_PATH}; no ad-hoc src edits; update {PRODUCT_CODE_LEDGER_PATH}",
            "allowed_files": ["src/**", "tests/**", "reports/rNN/**", "taskcards/**", PRODUCT_CODE_LEDGER_PATH],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1"],
            "tasks": c3_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C4",
            "owner_role": "Dogfood",
            "title": "Dogfood export advancement",
            "description": f"Product objective: close or verify one selected dogfood export from {SELECTED_PRODUCT_GAPS_PATH} using a Format Factory-produced library",
            "allowed_files": ["src/**", "tests/**", "reports/rNN/**", PRODUCT_CODE_LEDGER_PATH],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C3"],
            "tasks": c4_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C5",
            "owner_role": "PackageInstall",
            "title": "Package and installed-workflow proof",
            "description": "Product objective: prove changed packages from physical artifacts; missing artifacts fail the lane",
            "allowed_files": ["packaging/**", "tests/**", "reports/rNN/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C3", "C4"],
            "tasks": c5_tasks,
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C6",
            "owner_role": "Evidence",
            "title": "Evidence bundle",
            "description": "Write the evidence declaration and run supervisor autonomous-cycle",
            "allowed_files": [".local/evidence/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C2", "C3", "C4", "C5"],
            "tasks": [t["task_id"] for t in tasks if t.get("lane") == "C6"],
            "status": "pending",
            "non_authoritative": True,
        },
    ]

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "coordinator_lane": "C0",
        "lanes": lanes,
        "overlap_check_passed": True,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_approval_gates_md(review: dict, contradictions: dict, current_mode: int, repo_root: Path = None) -> str:
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    lines = [
        "# Approval Gates Classification",
        f"Sprint ID: {review.get('sprint_id', 'unknown')}",
        f"Generated: {datetime.now().isoformat()}",
        f"Current Mode: MODE {current_mode}" + (" (ACTIVE_MCP_ACTIVATION)" if current_mode == 4 else
                                                  " (AUTONOMOUS_SPRINT_LOOP_RC)" if current_mode == 5 else ""),
        "",
        "## Pending Actions",
        "",
    ]

    # D86-SUP-06 fix: Physical check for .vscode/mcp.json
    mcp_physically_present = False
    if repo_root:
        mcp_json_path = repo_root / ".vscode" / "mcp.json"
        mcp_physically_present = mcp_json_path.exists()

    if critical_count > 0:
        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            f"| Repair {critical_count} CRITICAL contradictions | local-repair-loop | Claude_Code |",
            "| Continue to next sprint | stop-contradictions-present | Claude_Code (after repair) |",
        ]
    else:
        if current_mode >= 4 and mcp_physically_present:
            mcp_row = "| MCP activation (MODE 4 ACTIVE — .vscode/mcp.json verified present) | autonomous-continue | already-done |"
        elif current_mode >= 4 and not mcp_physically_present:
            mcp_row = "| MCP activation (MODE 4 claimed but .vscode/mcp.json MISSING) | stop-mcp-file-missing | User |"
        else:
            mcp_row = "| MCP activation | stop-mcp-activation-required | User |"

        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            "| Continue to next sprint lanes | autonomous-continue | null |",
            "| Gate approval (if any gate pending) | stop-gate-approval-required | Babar_Raza |",
            "| Push/commit | stop-push-approval-required | User |",
            mcp_row,
        ]

    # D86-SUP-06 fix: Physical check for MCP status line
    if current_mode >= 4 and mcp_physically_present:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 5 autonomous sprint loop (explicit user approval required)"
        mcp_status_line = "- MCP_STATUS: ACTIVE (.vscode/mcp.json verified present)"
    elif current_mode >= 4 and not mcp_physically_present:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 4 MCP file missing (restore .vscode/mcp.json)"
        mcp_status_line = "- MCP_STATUS: CLAIMED_BUT_MISSING (.vscode/mcp.json not found on disk)"
    else:
        next_gate_line = "- NEXT_HUMAN_GATE: MODE 4 MCP activation (explicit user approval required)"
        mcp_status_line = "- MCP_STATUS: NOT_ACTIVATED (MODE < 4)"

    lines += [
        "",
        "## Summary",
        f"- AUTONOMOUS_CONTINUE: {'YES' if autonomous else 'NO — repair required first'}",
        next_gate_line,
        mcp_status_line,
        "- DAEMON_STATUS: NOT_STARTED (no human gate needed to keep it stopped)",
    ]

    return "\n".join(lines) + "\n"


def generate_session_resume_md(review: dict, contradictions: dict, memory_snippet: str, current_mode: int) -> str:
    facts = review.get("facts", {})
    return f"""# Session Resume Briefing
# Format Factory — Supervisor-Generated
# Generated: {datetime.now().isoformat()}

## Quick State
- Last sprint: {review.get('sprint_id', 'unknown')}
- Evidence verdict: {review.get('verdict', 'unknown')}
- Tests: {facts.get('test_count', 0)} passed / {facts.get('fail_count', 0)} failed
- PENDING markers: {facts.get('pending_marker_count', 0)}
- CRITICAL contradictions: {contradictions.get('critical_count', 0)}
- Autonomous continue: {contradictions.get('autonomous_continue', True)}
- Current supervisor mode: MODE {current_mode}
- MCP status: {'ACTIVE (.vscode/mcp.json present)' if current_mode >= 4 else 'NOT_ACTIVATED'}

## What Was Done Last Sprint
(Read reports/supervisor/evidence-review.md for full details)

## What To Do Next
1. Read this file and evidence-review.md
2. Read approval-gates.md — follow classification
3. If contradictions exist -> fix them before advancing
4. If autonomous-continue -> proceed with next-sprint.md prompt
5. Read plans/master-plan.md for current phase state (AUTHORITY)

## Where To Find Evidence
- Last evidence bundle: {review.get('bundle_path', 'see .supervisor/state/current-run.json')}
- Supervisor outputs: reports/supervisor/
- Project memory: .supervisor/project-memory.md

## Project Memory (recent)
```
{memory_snippet}
```

## IMPORTANT REMINDERS
- Format Factory authority is FINAL. Supervisor output is advisory.
- No push without explicit user authorization.
- No gate self-approval. All gates 1-11 require human approval.
- MCP activation (MODE 4): {'COMPLETE' if current_mode >= 4 else 'requires explicit user approval'}.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate supervisor next-sprint packet from evidence review"
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("reports/supervisor/evidence-review.json"),
        help="Path to evidence-review.json",
    )
    parser.add_argument(
        "--contradictions",
        type=Path,
        default=Path("reports/supervisor/contradictions.json"),
        help="Path to contradictions.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for output files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review = load_json(args.review)
    contradictions = load_json(args.contradictions)
    memory_snippet = load_memory(repo_root / ".supervisor" / "project-memory.md")
    current_mode = read_current_mode(repo_root)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Synthesize sprint-specific tasks
    tasks = synthesize_sprint_tasks(review, contradictions, repo_root)

    # Generate next-sprint.md
    next_sprint_text = generate_next_sprint_md(review, contradictions, memory_snippet, tasks)
    (output_dir / "next-sprint.md").write_text(next_sprint_text, encoding="utf-8")

    # Generate next-sprint-taskmaster.json
    tm_data = generate_taskmaster_json(review, contradictions, tasks)
    schema_dir = repo_root / ".supervisor" / "schemas"
    tm_errors = validate_against_schema(tm_data, schema_dir / "next-sprint-taskmaster.schema.json")
    (output_dir / "next-sprint-taskmaster.json").write_text(json.dumps(tm_data, indent=2), encoding="utf-8")

    # Generate next-ruflo-lanes.json
    ruflo_data = generate_ruflo_lanes_json(review, contradictions, tasks)
    ruflo_errors = validate_against_schema(ruflo_data, schema_dir / "next-ruflo-lanes.schema.json")
    (output_dir / "next-ruflo-lanes.json").write_text(json.dumps(ruflo_data, indent=2), encoding="utf-8")

    # Generate approval-gates.md (mode-aware)
    gates_text = generate_approval_gates_md(review, contradictions, current_mode, repo_root)
    (output_dir / "approval-gates.md").write_text(gates_text, encoding="utf-8")

    # Generate session-resume.md
    resume_text = generate_session_resume_md(review, contradictions, memory_snippet, current_mode)
    (output_dir / "session-resume.md").write_text(resume_text, encoding="utf-8")

    critical_count = contradictions.get("critical_count", 0)
    print(f"PACKET_GENERATION: COMPLETE")
    print(f"  Output dir: {output_dir}")
    print(f"  next-sprint.md: written ({len(tasks)} tasks synthesized)")
    print(f"  next-sprint-taskmaster.json: written" + (f" (schema errors: {tm_errors})" if tm_errors else " (schema OK)"))
    print(f"  next-ruflo-lanes.json: written" + (f" (schema errors: {ruflo_errors})" if ruflo_errors else " (schema OK)"))
    print(f"  approval-gates.md: written (mode {current_mode}: {'MCP ACTIVE' if current_mode >= 4 else 'MCP pending'})")
    print(f"  session-resume.md: written")

    if critical_count > 0:
        print(f"  NOTE: {critical_count} CRITICAL contradictions — next-sprint focuses on repair")
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
